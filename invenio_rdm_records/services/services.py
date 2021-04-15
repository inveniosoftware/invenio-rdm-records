# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from datetime import datetime

import arrow
from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_files_rest.models import ObjectVersion
from invenio_records_resources.services.records.schema import \
    ServiceSchemaWrapper
from marshmallow.exceptions import ValidationError


class RDMRecordService(RecordService):
    """RDM record service."""

    def __init__(self, config, files_service=None, draft_files_service=None):
        """Constructor for RDMRecordService."""
        super().__init__(config)
        self._files = files_service
        self._draft_files = draft_files_service

    @property
    def files(self):
        """Record files service."""
        return self._files

    @property
    def draft_files(self):
        """Draft files service."""
        return self._draft_files

    def link_result_item(self, *args, **kwargs):
        """Create a new instance of the resource unit."""
        return self.config.link_result_item_cls(*args, **kwargs)

    def link_result_list(self, *args, **kwargs):
        """Create a new instance of the resource list."""
        return self.config.link_result_list_cls(*args, **kwargs)

    @property
    def schema_secret_link(self):
        """Schema for secret links."""
        return ServiceSchemaWrapper(
            self, schema=self.config.schema_secret_link
        )

    def import_files(self, id_, identity):
        """Import files from previous record version."""
        # FIXME: Remove "registered_only=False" since it breaks access to an
        # unpublished record.

        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "update_draft", record=draft)

        # Retrieve latest record
        record = self.record_cls.get_record(draft.versions.latest_id)

        if not draft.files.enabled or draft.files.items():
            raise ValidationError(
                _("Files should be enabled and no files uploaded.")
            )

        if not record.files.enabled or not record.files.bucket:
            raise ValidationError(_("Record should have files enabled"))

        # Set the record bucket on the draft
        for o in ObjectVersion.get_by_bucket(record.bucket):
            o.copy(bucket=draft.bucket)

        # Copy over the files
        for key, df in record.files.items():
            # metadata
            if df.metadata is not None:
                draft.files[key] = df.object_version, df.metadata
            else:
                draft.files[key] = df.object_version

        # Commit and index
        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self._draft_files.file_result_list(
            self._draft_files,
            identity,
            results=draft.files.values(),
            record=draft,
            links_tpl=self._draft_files.file_links_list_tpl(id_),
            links_item_tpl=self._draft_files.file_links_item_tpl(id_),
        )

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
        if expires_at and is_specified:
            # if the expiration date was specified, check if it's in the future
            expires_at = arrow.get(expires_at).to("utc").datetime
            expires_at = expires_at.replace(tzinfo=None)

            if expires_at < datetime.utcnow():
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
            increases_expiration = (
                is_specified and not expires_at and secret_link.expires_at
            ) or (
                expires_at
                and secret_link.expires_at
                and expires_at > secret_link.expires_at
            )

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

            elif expires_at and expires_at < datetime.utcnow():
                raise ValidationError(
                    message=_("Expiration date must be set to the future"),
                    field_name="expires_at",
                )

        return expires_at

    def create_secret_link(
        self,
        id_,
        identity,
        data,
        links_config=None,
    ):
        """Create a secret link for a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Validation
        data, __ = self.schema_secret_link.load(
            data, context=dict(identity=identity), raise_errors=True
        )
        expires_at = self._validate_secret_link_expires_at(
            data.get("expires_at")
        )
        if "permission" not in data:
            raise ValidationError(
                _("An access permission level is required"),
                field_name="permission",
            )

        # Creation
        link = parent.access.links.create(
            permission_level=data["permission"],
            expires_at=expires_at,
            extra_data=data.get("extra_data", {}),
        )

        # Commit and index
        parent.commit()
        if record:
            record.commit()

        db.session.commit()
        self._index_related_records(record, parent)

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    def read_secret_links(
        self,
        id_,
        identity,
        links_config=None,
    ):
        """Read the secret links of a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

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
        id_,
        identity,
        link_id,
        links_config=None,
    ):
        """Read a specific secret link of a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

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

    def update_secret_link(
        self,
        id_,
        identity,
        link_id,
        data,
        links_config=None,
    ):
        """Update a secret link for a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

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
        # note: we can't update the link's extra data, as that is encoded
        #       in the token and would thus require a new token
        link.expires_at = expires_at or link.expires_at
        link.permission_level = permission or link.permission_level

        # Commit and index
        parent.commit()
        if record:
            record.commit()

        db.session.commit()
        self._index_related_records(record, parent)

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    def delete_secret_link(
        self,
        id_,
        identity,
        link_id,
        links_config=None,
    ):
        """Delete a secret link for a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

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

        # Commit and index
        parent.commit()
        if record:
            record.commit()

        db.session.commit()
        self._index_related_records(record, parent)

        return True

    def get_pid(
        self, id_, identity,
    ):
        """Reserve doi."""
        #  provider =
        # find_the_provider_by_the_param_value
        # (<provider param value>)
        #  return provider.reserve(...)

        return "1234"

    def delete_pid(
        self, id_, identity, doi,
    ):
        """Unreserve doi."""
        return ""
