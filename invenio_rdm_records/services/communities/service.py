# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2024      Graz University of Technology.
# Copyright (C) 2024      KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Communities Service."""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_pidstore.errors import PIDDoesNotExistError, PIDUnregistered
from invenio_records_resources.services import (
    RecordIndexerMixin,
    Service,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import (
    IndexRefreshOp,
    RecordIndexOp,
    unit_of_work,
)
from invenio_requests import current_request_type_registry, current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search.engine import dsl
from sqlalchemy.orm.exc import NoResultFound

from ...notifications.builders import CommunityInclusionSubmittedNotificationBuilder
from ...proxies import current_rdm_records, current_rdm_records_service
from ...requests import CommunityInclusion
from ..errors import (
    CannotRemoveCommunityError,
    CommunityAlreadyExists,
    InvalidAccessRestrictions,
    OpenRequestAlreadyExists,
    RecordCommunityMissing,
    RecordSubmissionClosedCommunityError,
)


class RecordCommunitiesService(Service, RecordIndexerMixin):
    """Record communities service.

    The communities service is in charge of managing communities of a given record.
    """

    @property
    def schema(self):
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def communities_schema(self):
        """Returns the communities schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.communities_schema)

    @property
    def record_cls(self):
        """Factory for creating a record class."""
        return self.config.record_cls

    @property
    def draft_cls(self):
        """Factory for creating a draft class."""
        return self.config.draft_cls

    def _exists(self, community_id, record):
        """Return the request id if an open request already exists, else None."""
        results = current_requests_service.search(
            system_identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"receiver.community": community_id}),
                    dsl.Q("term", **{"topic.record": record.pid.pid_value}),
                    dsl.Q("term", **{"type": CommunityInclusion.type_id}),
                    dsl.Q("term", **{"is_open": True}),
                ],
            ),
        )
        if results.total > 1:
            current_app.logger.error(
                f"Multiple community inclusions request detected for: "
                f"record_pid{record.pid.pid_value}, community_id{community_id}"
            )
        return next(results.hits)["id"] if results.total > 0 else None

    def _include(self, identity, community_id, comment, require_review, record, uow):
        """Create request to add the community to the record."""
        # check if the community exists
        community = current_communities.service.record_cls.pid.resolve(community_id)
        com_id = str(community.id)

        already_included = com_id in record.parent.communities
        if already_included:
            raise CommunityAlreadyExists()

        # check if there is already an open request, to avoid duplications
        existing_request_id = self._exists(com_id, record)

        if existing_request_id:
            raise OpenRequestAlreadyExists(existing_request_id)

        type_ = current_request_type_registry.lookup(CommunityInclusion.type_id)
        receiver = ResolverRegistry.resolve_entity_proxy(
            {"community": com_id}
        ).resolve()

        request_item = current_requests_service.create(
            identity,
            {},
            type_,
            receiver,
            topic=record,
            uow=uow,
        )

        # create review request
        request_item = current_rdm_records.community_inclusion_service.submit(
            identity, record, community, request_item._request, comment, uow
        )
        # include directly when allowed
        if not require_review:
            request_item = current_rdm_records.community_inclusion_service.include(
                identity, community, request_item._request, uow
            )
        return request_item

    @unit_of_work()
    def add(self, identity, id_, data, uow):
        """Include the record in the given communities."""
        valid_data, errors = self.schema.load(
            data,
            context={
                "identity": identity,
                "max_number": self.config.max_number_of_additions,
            },
            raise_errors=True,
        )
        communities = valid_data["communities"]

        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "add_community", record=record)

        processed = []
        for community in communities:
            community_id = community["id"]
            comment = community.get("comment", None)
            require_review = community.get("require_review", False)

            result = {
                "community_id": community_id,
            }
            try:
                can_submit_record = (
                    current_communities.service.config.permission_policy_cls(
                        "submit_record",
                        community_id=community_id,
                        record=current_communities.service.record_cls.pid.resolve(
                            community_id
                        ),
                    ).allows(identity)
                )

                if not can_submit_record:
                    raise RecordSubmissionClosedCommunityError()

                request_item = self._include(
                    identity, community_id, comment, require_review, record, uow
                )
                result["request_id"] = str(request_item.data["id"])
                result["request"] = request_item.to_dict()
                processed.append(result)
                uow.register(
                    NotificationOp(
                        CommunityInclusionSubmittedNotificationBuilder.build(
                            request_item._request
                        )
                    )
                )
            except (NoResultFound, PIDDoesNotExistError):
                result["message"] = _("Community not found.")
                errors.append(result)
            except (
                CommunityAlreadyExists,
                OpenRequestAlreadyExists,
                InvalidAccessRestrictions,
                PermissionDeniedError,
            ) as ex:
                result["message"] = ex.description
                errors.append(result)
            except RecordSubmissionClosedCommunityError as e:
                result["message"] = e.description
                errors.append(result)

        uow.register(IndexRefreshOp(indexer=self.indexer))

        return processed, errors

    def _remove(self, identity, community_id, record):
        """Remove a community from the record."""
        if community_id not in record.parent.communities.ids:
            raise RecordCommunityMissing(record.id, community_id)

        try:
            self.require_permission(
                identity, "remove_community", record=record, community_id=community_id
            )
            # By default, admin/superuser has permission to do everything, so PermissionDeniedError won't be raised for admin in any case
        except PermissionDeniedError as exc:
            # If permission is denied, determine which error to raise, based on config
            community_required = current_app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"]
            is_last_community = len(record.parent.communities.ids) <= 1
            if community_required and is_last_community:
                raise CannotRemoveCommunityError()
            else:
                # If the config wasn't enabled, then raise the PermissionDeniedError
                raise exc

        # Default community is deleted when the exact same community is removed from the record
        record.parent.communities.remove(community_id)

    @unit_of_work()
    def remove(self, identity, id_, data, uow):
        """Remove communities from the record."""
        record = self.record_cls.pid.resolve(id_)

        valid_data, errors = self.schema.load(
            data,
            context={
                "identity": identity,
                "max_number": self.config.max_number_of_removals,
            },
            raise_errors=True,
        )
        communities = valid_data["communities"]
        processed = []
        for community in communities:
            community_id = community["id"]
            try:
                self._remove(identity, community_id, record)
                processed.append({"community": community_id})
            except (
                RecordCommunityMissing,
                PermissionDeniedError,
                CannotRemoveCommunityError,
            ) as ex:
                errors.append(
                    {
                        "community": community_id,
                        "message": ex.description,
                    }
                )
        if processed:
            uow.register(
                ParentRecordCommitOp(
                    record.parent,
                    indexer_context=dict(service=current_rdm_records_service),
                )
            )
            uow.register(
                RecordIndexOp(record, indexer=self.indexer, index_refresh=True)
            )

        return processed, errors

    def search(
        self,
        identity,
        id_,
        params=None,
        search_preference=None,
        expand=False,
        extra_filter=None,
        **kwargs,
    ):
        """Search for record's communities."""
        try:
            record = self.record_cls.pid.resolve(id_)
        except PIDUnregistered:
            record = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "read", record=record)

        communities_ids = record.parent.communities.ids
        communities_filter = dsl.Q("terms", **{"id": [id_ for id_ in communities_ids]})
        if extra_filter is not None:
            communities_filter = communities_filter & extra_filter

        return current_communities.service.search(
            identity,
            params=params,
            search_preference=search_preference,
            expand=expand,
            extra_filter=communities_filter,
            **kwargs,
        )

    @staticmethod
    def _get_excluded_communities_filter(record, identity, id_):
        """Return filter to exclude communities that should not be suggested."""
        communities_to_exclude = []
        communities_ids = record.parent.communities.ids

        for community_id in communities_ids:
            communities_to_exclude.append(dsl.Q("term", **{"id": community_id}))

        open_requests = current_requests_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"topic.record": id_}),
                    dsl.Q("term", **{"type": CommunityInclusion.type_id}),
                    dsl.Q("term", **{"is_open": True}),
                ],
            ),
        )

        # the assumption here is that there should be only a few open requests,
        # so requests.hits (first page one) should be enough
        for request in open_requests.hits:
            communities_to_exclude.append(
                dsl.Q("term", **{"id": request["receiver"]["community"]})
            )

        exclusion_filter = dsl.query.Bool("must_not", must_not=communities_to_exclude)

        return exclusion_filter

    def search_suggested_communities(
        self,
        identity,
        id_,
        params=None,
        search_preference=None,
        expand=False,
        by_membership=False,
        extra_filter=None,
        **kwargs,
    ):
        """Search for communities that can be added to a record."""
        record = self.record_cls.pid.resolve(id_)

        self.require_permission(identity, "add_community", record=record)

        communities_filter = self._get_excluded_communities_filter(
            record, identity, id_
        )

        if extra_filter is not None:
            communities_filter = communities_filter & extra_filter

        if by_membership:
            return current_communities.service.search_user_communities(
                identity,
                params=params,
                search_preference=search_preference,
                extra_filter=communities_filter,
                **kwargs,
            )

        return current_communities.service.search(
            identity,
            params=params,
            search_preference=search_preference,
            expand=expand,
            extra_filter=communities_filter,
            **kwargs,
        )

    @unit_of_work()
    def set_default(self, identity, id_, data, uow):
        """Set default community."""
        valid_data, _ = self.communities_schema.load(
            data,
            context={
                "identity": identity,
            },
            raise_errors=True,
        )
        record = self.record_cls.pid.resolve(id_)
        self.require_permission(identity, "manage", record=record)

        default_community_id = valid_data.get("default", {}).get("id") or None
        record.parent.communities.default = default_community_id

        uow.register(
            ParentRecordCommitOp(
                record.parent,
                indexer_context=dict(service=current_rdm_records_service),
            )
        )

        return record.parent

    @unit_of_work()
    def bulk_add(self, identity, community_id, record_ids, set_default=False, uow=None):
        """Bulk adds records to a community.

        :param identity: The identity performing the action.
        :param community_id: The ID of the community.
        :param record_ids: List of record IDs to be added to the community.
        :param set_default: Whether to set the community as default for the added records.
        """
        self.require_permission(identity, "bulk_add")
        errors = []
        for record_id in record_ids:
            record = self.record_cls.pid.resolve(record_id)
            community = current_communities.service.record_cls.pid.resolve(community_id)

            set_default = set_default or not record.parent.communities
            already_included = community.id in record.parent.communities
            if already_included:
                errors.append(
                    {
                        "record_id": record_id,
                        "community_id": community_id,
                        "message": _("Community already included."),
                    }
                )
                continue

            parent_community = getattr(community, "parent", None)
            already_in_parent = (
                parent_community
                and str(parent_community.id) in record.parent.communities
            )

            if parent_community and not already_in_parent:
                record.parent.communities.add(parent_community, request=None)

            record.parent.communities.add(community, request=None, default=set_default)

            # Commit and bulk re-index everything
            uow.register(
                ParentRecordCommitOp(
                    record.parent,
                    indexer_context={"service": current_rdm_records_service},
                    bulk_index=True,
                )
            )
        return errors
