# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Community Records Service."""

from invenio_i18n import lazy_gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services import (
    LinksTemplate,
    RecordService,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import unit_of_work
from invenio_search.engine import dsl

from ...proxies import current_record_communities_service
from ...records.systemfields.deletion_status import RecordDeletionStatusEnum


class CommunityRecordsService(RecordService):
    """Community records service.

    The record communities service is in charge of managing the records of a given community.
    """

    @property
    def community_record_schema(self):
        """Returns the community schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.community_record_schema)

    @property
    def community_cls(self):
        """Factory for creating a community class."""
        return self.config.community_cls

    def search(
        self,
        identity,
        community_id,
        params=None,
        search_preference=None,
        extra_filter=None,
        scan=False,
        scan_params=None,
        **kwargs,
    ):
        """Search for records published in the given community."""
        self.require_permission(identity, "search")

        community = self.community_cls.pid.resolve(
            community_id
        )  # Ensure community's existence

        params = params or {}

        community_filter = dsl.Q(
            "term", **{"parent.communities.ids": str(community.id)}
        )
        status = RecordDeletionStatusEnum.PUBLISHED.value

        published_filter = dsl.Q("term", **{"deletion_status": status})
        community_filter &= published_filter

        if extra_filter is not None:
            community_filter = community_filter & extra_filter

        search = self._search(
            "search",
            identity,
            params,
            search_preference,
            extra_filter=community_filter,
            permission_action="read",
            **kwargs,
        )

        if scan:
            scan_params = scan_params or {}
            search_result = search.scan(**scan_params)
        else:
            search_result = search.execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_community_records,
                context={
                    "args": params,
                    "pid_value": community_id,
                },
            ),
            links_item_tpl=self.links_item_tpl,
        )

    def _remove(self, community, record, identity):
        """Remove a community from the record."""
        data = dict(communities=[dict(id=str(community.id))])
        _, errors = current_record_communities_service.remove(
            identity, id_=record.pid.pid_value, data=data
        )

        return errors

    @unit_of_work()
    def delete(self, identity, community_id, data, revision_id=None, uow=None):
        """Remove records from a community."""
        community = self.community_cls.pid.resolve(community_id)

        self.require_permission(identity, "remove_record", record=community)

        valid_data, errors = self.community_record_schema.load(
            data,
            context={
                "identity": identity,
                "max_number": self.config.max_number_of_removals,
            },
            raise_errors=True,
        )
        records_dict = valid_data["records"]

        for record_dict in records_dict:
            record_id = record_dict["id"]
            try:
                record = self.record_cls.pid.resolve(record_id)
                errors += self._remove(community, record, identity)
            except PIDDoesNotExistError:
                errors.append(
                    {
                        "record": record_id,
                        "message": _("The record does not exist."),
                    }
                )
            except PermissionDeniedError:
                errors.append(
                    {
                        "record": record_id,
                        "message": _("Permission denied."),
                    }
                )

        return errors
