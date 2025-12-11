# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2023-2025 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record access settings service."""

from datetime import datetime, timedelta, timezone

import arrow
from flask import current_app
from flask_login import current_user
from invenio_access.permissions import authenticated_user, system_identity
from invenio_base import invenio_url_for
from invenio_drafts_resources.services.records import RecordService
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests.proxies import current_requests_service
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_user_resources
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from invenio_rdm_records.notifications.builders import (
    GrantUserAccessNotificationBuilder,
    GuestAccessRequestTokenCreateNotificationBuilder,
)

from ...requests.access import AccessRequestToken, GuestAccessRequest, UserAccessRequest
from ...secret_links.errors import InvalidPermissionLevelError
from ..decorators import groups_enabled
from ..errors import AccessRequestExistsError, GrantExistsError
from ..results import GrantSubjectExpandableField


class RecordAccessService(RecordService):
    """RDM Secret Link service."""

    group_subject_type = "role"

    def link_result_item(self, *args, **kwargs):
        """Create a new instance of the resource unit."""
        return self.config.link_result_item_cls(*args, **kwargs)

    def link_result_list(self, *args, **kwargs):
        """Create a new instance of the resource list."""
        return self.config.link_result_list_cls(*args, **kwargs)

    def grant_result_item(self, *args, **kwargs):
        """Create a new instance of the resource unit."""
        kwargs["expandable_fields"] = self.expandable_fields
        return self.config.grant_result_item_cls(*args, **kwargs)

    def grants_result_list(self, *args, **kwargs):
        """Create a new instance of the resource list."""
        kwargs["expandable_fields"] = self.expandable_fields
        return self.config.grant_result_list_cls(*args, **kwargs)

    def get_parent_and_record_or_draft(self, _id):
        """Return parent and (record or draft)."""
        try:
            record, parent = self._get_record_and_parent_by_id(_id)
        except NoResultFound:
            record, parent = self._get_draft_and_parent_by_id(_id)
        return record, parent

    @property
    def schema_secret_link(self):
        """Schema for secret links."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_secret_link)

    @property
    def schema_grant(self):
        """Schema for secret links."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_grant)

    @property
    def schema_grants(self):
        """Schema for grants."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_grants)

    @property
    def schema_request_access(self):
        """Schema for secret links."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_request_access)

    @property
    def schema_access_settings(self):
        """Schema for record parent."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_access_settings)

    @property
    def expandable_fields(self):
        """List of expandable fields."""
        return [
            GrantSubjectExpandableField("subject"),
        ]

    #
    # Update parent request on access changes
    #

    def _update_parent_request(self, parent, uow):
        """Update the parent record request."""
        if parent.review:
            request = parent.review.get_object()
            uow.register(RecordCommitOp(request, indexer=self.indexer))

    #
    # Secret links
    #

    def _validate_secret_link_expires_at(
        self, expires_at, is_specified=True, secret_link=None
    ):
        """Validate the given expiration date.

        If a ``secret_link`` is specified, the validity of setting its
        expiration date to ``expires_at`` will be checked additionally.
        The ``is_specified`` flag hints at if the value of ``expires_at``
        was set in the given data, or if it was omitted (which makes a
        difference in patch operations).
        """
        if (
            current_app.config["RDM_RECORDS_REQUIRE_SECRET_LINKS_EXPIRATION"]
            and not expires_at
        ):
            raise ValidationError(
                message=_("Expiration date is required"),
                field_name="expires_at",
            )

        if expires_at and is_specified:
            # if the expiration date was specified, check if it's in the future
            expires_at = arrow.get(expires_at, tzinfo=timezone.utc).datetime
            if expires_at < datetime.now(timezone.utc):
                raise ValidationError(
                    message=_("Expiration date must be set to the future"),
                    field_name="expires_at",
                )

        if secret_link is not None:
            # if we're updating an existing secret link, we need to do some
            # more checks...

            # we interpret explicitly setting 'expires_at = null/None' as
            # removing the expiration date (semantically different from not
            # specifying an 'expires_at' value at all, at least for updates)
            introduces_expiration = (
                is_specified and not expires_at and secret_link.expires_at
            )

            extends_existing_expiration = (
                expires_at
                and secret_link.expires_at
                and expires_at > secret_link.expires_at
            )
            increases_expiration = introduces_expiration or extends_existing_expiration

            if increases_expiration:
                # it's not a problem to reduce the validity of a token (*),
                # but increasing its lifespan would require a new signature,
                # and thus a new token
                # (*) in that case, the permission generator will still say
                #     no, even if the signature is still valid
                raise ValidationError(
                    message=_("Cannot postpone expiration of links"),
                    field_name="expires_at",
                )

            elif expires_at and expires_at < datetime.now(timezone.utc):
                raise ValidationError(
                    message=_("Expiration date must be set to the future"),
                    field_name="expires_at",
                )

        return expires_at

    @unit_of_work()
    def create_secret_link(self, identity, id_, data, links_config=None, uow=None):
        """Create a secret link for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Validation
        data, __ = self.schema_secret_link.load(
            data, context=dict(identity=identity), raise_errors=True
        )
        expires_at = self._validate_secret_link_expires_at(data.get("expires_at"))
        if "permission" not in data:
            raise ValidationError(
                _("An access permission level is required"),
                field_name="permission",
            )

        # Creation
        try:
            link = parent.access.links.create(
                permission_level=data["permission"],
                origin=data.get("origin"),
                description=data.get("description", ""),
                expires_at=expires_at,
                extra_data=data.get("extra_data", {}),
            )
        except InvalidPermissionLevelError:
            raise ValidationError(
                _("Invalid access permission level."),
                field_name="permission",
            )

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))
        self._update_parent_request(parent, uow)

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    def read_all_secret_links(
        self,
        identity,
        id_,
        links_config=None,
    ):
        """Read the secret links of a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        links = parent.access.links.resolve_all()
        return self.link_result_list(
            service=self,
            identity=identity,
            results=links,
            links_config=links_config,
        )

    def read_secret_link(
        self,
        identity,
        id_,
        link_id,
        links_config=None,
    ):
        """Read a specific secret link of a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        link_ids = [link.link_id for link in parent.access.links]
        if str(link_id) not in link_ids:
            raise LookupError(str(link_id))

        link_idx = link_ids.index(link_id)
        link = parent.access.links[link_idx].resolve()

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    @unit_of_work()
    def update_secret_link(
        self,
        identity,
        id_,
        link_id,
        data,
        links_config=None,
        uow=None,
    ):
        """Update a secret link for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching (required for parts of the validation)
        link_ids = [link.link_id for link in parent.access.links]
        if str(link_id) not in link_ids:
            raise LookupError(str(link_id))

        link_idx = link_ids.index(link_id)
        link = parent.access.links[link_idx].resolve()

        # Validation
        data, __ = self.schema_secret_link.load(
            data, context=dict(identity=identity), raise_errors=True
        )
        permission = data.get("permission")
        expires_at = self._validate_secret_link_expires_at(
            data.get("expires_at"),
            is_specified=("expires_at" in data),
            secret_link=link,
        )

        # Update
        # we can't update the link's extra data, as that is encoded
        # in the token and would thus require a new token
        link.expires_at = expires_at or link.expires_at
        link.permission_level = permission or link.permission_level
        link.description = data.get("description", link.description)

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))
        self._update_parent_request(parent, uow)

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    @unit_of_work()
    def delete_secret_link(self, identity, id_, link_id, links_config=None, uow=None):
        """Delete a secret link for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        link_ids = [link.link_id for link in parent.access.links]
        if str(link_id) not in link_ids:
            raise LookupError(str(link_id))

        link_idx = link_ids.index(link_id)
        link = parent.access.links[link_idx].resolve()

        # Deletion
        parent.access.links.pop(link_idx)
        link.revoke()

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))
        self._update_parent_request(parent, uow)

        return True

    #
    # Access grants
    #

    def _validate_grant_subject(self, identity, grant):
        """Check if the grant subject exists and is visible to the given identity."""
        try:
            if grant.subject_type == "user":
                current_user_resources.users_service.read(
                    identity=identity, id_=grant.subject_id
                )
            elif grant.subject_type == RecordAccessService.group_subject_type:
                current_user_resources.groups_service.read(
                    identity=identity, id_=grant.subject_id
                )
            elif grant.subject_type == "system_role":
                # NOTE: system roles don't have a service yet, so we check through
                #       the system field's resolution (`grant.subject`)
                grant.subject
            else:
                return False

            return True

        except (LookupError, PermissionDeniedError):
            # NOTE: services in Users-Resources will use "permission denied" to mask
            #       "not found" errors, to not leak information about existence
            return False

    @unit_of_work()
    def bulk_create_grants(self, identity, id_, data, expand=False, uow=None):
        """Bulk create access grants for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Validation
        data, __ = self.schema_grants.load(
            data, context={"identity": identity}, raise_errors=True
        )

        grants = data["grants"]

        new_grants = []

        # fail if any of the grants already exist
        if any(
            existing_grant.subject_id == grant["subject"]["id"]
            and existing_grant.subject_type == grant["subject"]["type"]
            for existing_grant in parent.access.grants
            for grant in grants
        ):
            raise GrantExistsError()

        for grant in grants:
            # checks if groups are enabled in the instance
            if (
                not current_app.config.get("USERS_RESOURCES_GROUPS_ENABLED", False)
                and grant["subject"]["type"] == RecordAccessService.group_subject_type
            ):
                raise PermissionDeniedError()

            # Creation
            new_grant = parent.access.grants.create(
                subject_type=grant["subject"]["type"],
                subject_id=grant["subject"]["id"],
                permission=grant["permission"],
                origin=grant.get("origin"),
            )

            if not self._validate_grant_subject(identity, new_grant):
                raise ValidationError(
                    _("Could not find the specified subject."), field_name="subject.id"
                )

            if grant["subject"]["type"] == "user" and grant.get("notify"):
                uow.register(
                    NotificationOp(
                        GrantUserAccessNotificationBuilder.build(
                            record=record,
                            user={"user": grant["subject"]["id"]},
                            permission=grant["permission"],
                            message=grant.get("message"),
                        )
                    )
                )
            new_grants.append(new_grant)

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))
        self._update_parent_request(parent, uow)

        return self.grants_result_list(
            self,
            identity,
            new_grants,
            expand=expand,
        )

    def read_grant(self, identity, id_, grant_id, expand=False):
        """Read a specific access grant of a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        if not 0 <= grant_id < len(parent.access.grants):
            raise LookupError(str(grant_id))

        grant = parent.access.grants[grant_id]

        # checks if groups are enabled in the instance
        if (
            not current_app.config.get("USERS_RESOURCES_GROUPS_ENABLED", False)
            and grant.subject_type == RecordAccessService.group_subject_type
        ):
            raise PermissionDeniedError()

        return self.grant_result_item(
            self,
            identity,
            grant,
            expand=expand,
        )

    @unit_of_work()
    def update_grant(
        self,
        identity,
        id_,
        grant_id,
        data,
        expand=False,
        partial=False,
        uow=None,
    ):
        """Update an access grant for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching (required for parts of the validation)
        old_grant = parent.access.grants[grant_id]

        # checks if groups are enabled in the instance
        if (
            not current_app.config.get("USERS_RESOURCES_GROUPS_ENABLED", False)
            and old_grant.subject_type == RecordAccessService.group_subject_type
        ):
            raise PermissionDeniedError()

        if partial:
            data = {
                "permission": data.get("permission", old_grant.permission),
                "subject": {
                    "type": data.get("subject", {}).get("type", old_grant.subject_type),
                    "id": data.get("subject", {}).get("id", old_grant.subject_id),
                },
                "origin": data.get("origin", old_grant.origin),
            }

        # Validation
        data, __ = self.schema_grant.load(
            data, context={"identity": identity}, raise_errors=True
        )

        # Update
        try:
            new_grant = parent.access.grants.grant_cls.create(
                origin=data["origin"],
                permission=data["permission"],
                subject_type=data["subject"]["type"],
                subject_id=data["subject"]["id"],
                resolve_subject=True,
            )
        except LookupError:
            raise ValidationError(
                _("Could not find the specified subject."), field_name="subject.id"
            )

        parent.access.grants[grant_id] = new_grant

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))
        self._update_parent_request(parent, uow)

        return self.grant_result_item(
            self,
            identity,
            new_grant,
            expand=expand,
        )

    def read_all_grants(self, identity, id_, expand=False):
        """Read the access grants of a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        existing_grants = parent.access.grants

        for grant in existing_grants:
            # removes group grants if groups are not enabled in the instance
            if (
                not current_app.config.get("USERS_RESOURCES_GROUPS_ENABLED", False)
                and grant.subject_type == RecordAccessService.group_subject_type
            ):
                # don't fail with 403, instead return only user grants, even if group grants are present
                existing_grants.remove(grant)

        # Fetching
        return self.grants_result_list(
            service=self,
            identity=identity,
            results=existing_grants,
            expand=expand,
        )

    @unit_of_work()
    def delete_grant(self, identity, id_, grant_id, uow=None):
        """Delete an access grant for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        if not 0 <= grant_id < len(parent.access.grants):
            raise LookupError(str(grant_id))

        # checks if groups are enabled in the instance
        if (
            not current_app.config.get("USERS_RESOURCES_GROUPS_ENABLED", False)
            and parent.access.grants[grant_id].subject_type
            == RecordAccessService.group_subject_type
        ):
            raise PermissionDeniedError()

        # Deletion
        parent.access.grants.pop(grant_id)

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))
        self._update_parent_request(parent, uow)

        return True

    def _exists(self, created_by, record_id, request_type):
        """Return the request id if an open request already exists, else None."""
        query_terms = [
            dsl.Q("term", **{"topic.record": record_id}),
            dsl.Q("term", **{"type": request_type}),
            dsl.Q("term", **{"is_open": True}),
        ]

        # Build the query dynamically based on the keys in created_by
        for key, value in created_by.items():
            query_terms.append(dsl.Q("term", **{f"created_by.{key}": value}))

        open_requests = current_requests_service.search(
            system_identity,
            extra_filter=dsl.query.Bool("must", must=query_terms),
        )

        if open_requests.total > 1:
            current_app.logger.error(
                f"Multiple access requests detected for: "
                f"record_pid{record_id}, creator: {created_by}"
            )

        if open_requests.total > 0:
            return open_requests.to_dict()["hits"]["hits"][0]

    def request_access(self, identity, id_, data, expand=False):
        """Redirect the access request to specific service method."""
        if current_user.is_authenticated:
            valid_current_email = (
                data.get("email", "").lower() == current_user.email.lower()
            )
            if valid_current_email:
                return self.create_user_access_request(
                    identity, id_, data, expand=expand
                )

        return self.create_guest_access_request_token(
            identity, id_, data, expand=expand
        )

    #
    # Access requests
    #
    @unit_of_work()
    def create_user_access_request(self, identity, id_, data, expand=False, uow=None):
        """Create a user access request for the given record."""
        record = self.record_cls.pid.resolve(id_)

        # Permissions
        # fail early if record fully restricted
        self.require_permission(identity, "read", record=record)

        can_read_files = self.check_permission(identity, "read_files", record=record)

        if can_read_files:
            raise PermissionDeniedError(
                "You already have access to files of this record."
            )

        existing_access_request = self._exists(
            created_by={"user": str(identity.id)},
            record_id=id_,
            request_type=UserAccessRequest.type_id,
        )

        if existing_access_request:
            raise AccessRequestExistsError(existing_access_request["id"])

        data, __ = self.schema_request_access.load(
            data, context={"identity": identity}, raise_errors=True
        )

        data = {"payload": data}

        # Determine the request's receiver
        receiver = None
        record_owner = record.parent.access.owner.resolve()
        if record_owner:
            receiver = record_owner

        request = current_requests_service.create(
            identity,
            data,
            UserAccessRequest,
            receiver,
            topic=record,
            expires_at=None,
            expand=expand,
            uow=uow,
        )

        message = data["payload"].get("message")
        comment = None
        if message:
            comment = {
                "payload": {
                    "content": message,
                }
            }
        return current_requests_service.execute_action(
            identity,
            request.id,
            "submit",
            data=comment,
            uow=uow,
        )

    @unit_of_work()
    def create_guest_access_request_token(
        self, identity, id_, data, expand=False, uow=None
    ):
        """Create a request token that can be used to create an access request."""
        record = self.record_cls.pid.resolve(id_)
        if current_app.config.get("MAIL_SUPPRESS_SEND", False):
            # TODO should be handled globally, not here, maybe EmailOp?
            current_app.logger.warning(
                "Cannot proceed with guest based access request - "
                "email sending has been disabled!"
            )

        data, __ = self.schema_request_access.load(
            data, context={"identity": identity}, raise_errors=True
        )

        access_token = AccessRequestToken.create(
            email=data["email"],
            full_name=data["full_name"],
            message=data.get("message"),
            record_pid=id_,
            shelf_life=timedelta(hours=6),
            consent=data["consent_to_share_personal_data"],
        )

        # Create the URL for the email verification endpoint
        verify_url = invenio_url_for(
            "invenio_app_rdm_requests.verify_access_request_token",
            access_request_token=access_token.token,
        )
        uow.register(
            NotificationOp(
                GuestAccessRequestTokenCreateNotificationBuilder.build(
                    record=record, email=data["email"], verify_url=verify_url
                )
            )
        )

        return {
            "message": _("Verification link sent out, please check your e-mail inbox"),
        }

    @unit_of_work()
    def create_guest_access_request(self, identity, token, expand=False, uow=None):
        """Use the guest access request token to create an access request."""
        # Permissions
        if authenticated_user in identity.provides:
            raise PermissionDeniedError("request_guest_access")

        access_token = AccessRequestToken.get_by_token(token)
        if access_token is None:
            return

        access_token_data = access_token.to_dict()
        record = self.record_cls.pid.resolve(access_token_data["record_pid"])

        # Detect duplicate requests
        existing_access_request = self._exists(
            created_by={"email": access_token.email},
            record_id=access_token.record_pid,
            request_type=GuestAccessRequest.type_id,
        )

        if existing_access_request:
            raise AccessRequestExistsError(existing_access_request["id"])
        data = {
            "payload": {
                "permission": "view",
                "email": access_token_data["email"],
                "full_name": access_token_data["full_name"],
                "token": access_token_data["token"],
                "message": access_token_data.get("message", ""),
                "consent_to_share_personal_data": access_token_data.get(
                    "consent_to_share_personal_data"
                ),
                "secret_link_expiration": str(
                    record.parent.access.settings.secret_link_expiration
                ),
            }
        }

        receiver = None
        record_owner = record.parent.access.owner.resolve()
        if record_owner:
            receiver = record_owner

        access_token.delete()
        request = current_requests_service.create(
            system_identity,
            data,
            GuestAccessRequest,
            receiver,
            creator=data["payload"]["email"],
            topic=record,
            expires_at=None,  # TODO expire request ?
            expand=expand,
            uow=uow,
        )

        message = data["payload"].get("message")
        comment = None
        if message:
            comment = {"payload": {"content": message}}

        return current_requests_service.execute_action(
            identity,
            request.id,
            "submit",
            data=comment,
            uow=uow,
        )

    @unit_of_work()
    def update_access_settings(
        self,
        identity,
        id_,
        data,
        uow=None,
    ):
        """Update access settings for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Validation
        data, __ = self.schema_access_settings.load(
            data, context=dict(identity=identity), raise_errors=True
        )

        # Update
        setattr(parent.access, "settings", data)

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    # TODO: rework the whole service and move these to a separate one:
    #  https://github.com/inveniosoftware/invenio-rdm-records/issues/1685
    @groups_enabled(group_subject_type)
    def read_grant_by_subject(
        self, identity, id_, subject_id, subject_type, expand=False
    ):
        """Read a specific access grant of a record by subject."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        result = None
        for grant in parent.access.grants:
            if grant.subject_id == subject_id and grant.subject_type == subject_type:
                result = grant

        if not result:
            raise LookupError(subject_id)

        return self.grant_result_item(
            self,
            identity,
            result,
            expand=expand,
        )

    @groups_enabled(group_subject_type)
    def read_all_grants_by_subject(self, identity, id_, subject_type, expand=False):
        """Read access grants of a record (resp. its parent) by subject type."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        user_grants = []
        for grant in parent.access.grants:
            if grant.subject_type == subject_type:
                user_grants.append(grant)

        # Fetching
        return self.grants_result_list(
            service=self,
            identity=identity,
            results=user_grants,
            expand=expand,
        )

    @groups_enabled(group_subject_type)
    @unit_of_work()
    def update_grant_by_subject(
        self,
        identity,
        id_,
        subject_id,
        subject_type,
        data,
        expand=False,
        uow=None,
    ):
        """Update access grant for a record (resp. its parent) by subject."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching (required for parts of the validation)
        grant_index = None
        for grant in parent.access.grants:
            if grant.subject_id == subject_id and grant.subject_type == subject_type:
                grant_index = parent.access.grants.index(grant)

        if grant_index is None:
            raise LookupError(subject_id)

        old_grant = parent.access.grants[grant_index]
        data = {
            "permission": data.get("permission", old_grant.permission),
            "subject": {
                "type": data.get("subject", {}).get("type", old_grant.subject_type),
                "id": data.get("subject", {}).get("id", old_grant.subject_id),
            },
            "origin": data.get("origin", old_grant.origin),
        }

        # Validation
        data, __ = self.schema_grant.load(
            data, context={"identity": identity}, raise_errors=True
        )

        # Update
        try:
            new_grant = parent.access.grants.grant_cls.create(
                origin=data["origin"],
                permission=data["permission"],
                subject_type=data["subject"]["type"],
                subject_id=data["subject"]["id"],
                resolve_subject=True,
            )
        except LookupError:
            raise ValidationError(
                _("Could not find the specified subject."), field_name="subject.id"
            )

        parent.access.grants[grant_index] = new_grant

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))
        self._update_parent_request(parent, uow)

        return self.grant_result_item(
            self,
            identity,
            new_grant,
            expand=expand,
        )

    @groups_enabled(group_subject_type)
    @unit_of_work()
    def delete_grant_by_subject(
        self, identity, id_, subject_id, subject_type, uow=None
    ):
        """Delete an access grant for a record by subject."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Deletion
        result = None
        for grant in parent.access.grants:
            if grant.subject_id == subject_id and grant.subject_type == subject_type:
                result = grant
                parent.access.grants.remove(grant)

        if not result:
            raise LookupError(subject_id)

        uow.register(ParentRecordCommitOp(parent, indexer_context=dict(service=self)))
        self._update_parent_request(parent, uow)

        return True
