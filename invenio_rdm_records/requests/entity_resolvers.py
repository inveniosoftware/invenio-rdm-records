# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2023 Graz University of Technology.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Entity resolver for records aware of drafts and records."""

import re

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError, PIDUnregistered
from invenio_records_resources.references.entity_resolvers import (
    EntityProxy,
    EntityResolver,
    RecordProxy,
    RecordResolver,
    ServiceResultProxy,
    ServiceResultResolver,
)
from invenio_users_resources.services.schemas import SystemUserSchema
from sqlalchemy.orm.exc import NoResultFound

from ..proxies import current_rdm_records_service
from ..records.api import RDMDraft, RDMRecord
from ..services.config import RDMRecordServiceConfig
from ..services.dummy import DummyExpandingService

# NOTE: this is the python regex from https://emailregex.com/
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class RDMRecordProxy(RecordProxy):
    """Proxy for resolve RDMDraft and RDMRecord."""

    def _get_record(self, pid_value):
        """Fetch the published record."""
        return RDMRecord.pid.resolve(pid_value)

    def _resolve(self):
        """Resolve the Record from the proxy's reference dict."""
        pid_value = self._parse_ref_dict_id()

        draft = None
        try:
            draft = RDMDraft.pid.resolve(pid_value, registered_only=False)
        except (PIDUnregistered, NoResultFound, PIDDoesNotExistError):
            # try checking if it is a published record before failing
            record = self._get_record(pid_value)
        else:
            # no exception raised. If published, get the published record instead
            record = draft if not draft.is_published else self._get_record(pid_value)

        return record

    def ghost_record(self, record):
        """Ghost representation of a record.

        Drafts at the moment cannot be resolved, service.read_many() is searching on
        public records, thus the `ghost_record` method will always kick in!
        """
        return {"id": record}

    def get_needs(self, ctx=None):
        """Enrich request with record needs.

        A user that can preview a record can also read its requests.
        """
        if ctx is None or "record_permission" not in ctx:
            return []

        record = self.resolve()
        record_permission = ctx["record_permission"]
        needs = current_rdm_records_service.config.permission_policy_cls(
            record_permission, record=record
        ).needs
        return needs


class RDMRecordResolver(RecordResolver):
    """RDM Record entity resolver."""

    type_id = "record"

    def __init__(self):
        """Initialize the resolver."""
        super().__init__(
            RDMDraft,
            RDMRecordServiceConfig.service_id,
            type_key=self.type_id,
            proxy_cls=RDMRecordProxy,
        )

    def matches_entity(self, entity):
        """Check if the entity is a draft or a record."""
        return isinstance(entity, (RDMDraft, RDMRecord))


class RDMRecordServiceResultProxy(ServiceResultProxy):
    """Proxy to resolve RDMDraft and RDMRecord."""

    def _get_record(self, pid_value):
        """Fetch the published record."""
        return self.service.read(system_identity, pid_value)

    def _resolve(self):
        """Resolve the result item from the proxy's reference dict."""
        pid_value = self._parse_ref_dict_id()

        draft = None
        try:
            draft = self.service.read_draft(system_identity, pid_value)
        except (PIDDoesNotExistError, NoResultFound):
            record = self._get_record(pid_value)
        else:
            # no exception raised. If published, get the published record instead
            record = (
                draft if not draft._record.is_published else self._get_record(pid_value)
            )

        return record.to_dict()


class RDMRecordServiceResultResolver(ServiceResultResolver):
    """Resolver for rdm record result items."""

    def __init__(self):
        """Ctor."""
        super().__init__(
            service_id=RDMRecordServiceConfig.service_id,
            type_key="record",
            proxy_cls=RDMRecordServiceResultProxy,
        )

    def _reference_entity(self, entity):
        """Create a reference dict for the given result item."""
        pid = entity.id if isinstance(entity, self.item_cls) else entity.pid.pid_value
        return {self.type_key: str(pid)}

    @property
    def draft_cls(self):
        """Get specified draft class or from service."""
        return self.get_service().draft_cls

    def matches_entity(self, entity):
        """Check if the entity is a draft."""
        if isinstance(entity, self.draft_cls):
            return True

        return ServiceResultResolver.matches_entity(self, entity=entity)


class EmailProxy(EntityProxy):
    """Entity proxy for email addresses."""

    def _resolve(self):
        """Resolve the email address from the dictionary."""
        return self._parse_ref_dict_id()

    def ghost_record(self, value):
        """Return the ghost representation of the unresolved value."""
        return value

    def system_record(self):
        """Return the representation of system user."""
        default_constant_values = {}
        return SystemUserSchema().dump(default_constant_values)

    def get_needs(self, ctx=None):
        """Get the needs provided by the entity."""
        return []

    def pick_resolved_fields(self, identity, resolved_dict):
        """Select which fields to return when resolving the reference."""
        return resolved_dict


class EmailResolver(EntityResolver):
    """Resolver for email addresses."""

    type_id = "email"
    type_key = "email"  # TODO: hack to make this entity resolver work in notifications

    def __init__(self):
        """Constructor."""
        super().__init__(None)
        self._service = DummyExpandingService("email")

    def matches_reference_dict(self, ref_dict):
        """Check if the entity dictionary references an email address."""
        return "email" in ref_dict

    def matches_entity(self, entity):
        """Check if the entity looks like an email address."""
        return isinstance(entity, str) and EMAIL_REGEX.fullmatch(entity)

    def _get_entity_proxy(self, ref_dict):
        """Get the entity proxy for email addresses."""
        return EmailProxy(self, ref_dict)

    def _reference_entity(self, entity):
        """Create a reference dict for the entity."""
        return {"email": entity}

    def get_service(self):
        """Return ``None``, because email addresses don't have a service."""
        return self._service
