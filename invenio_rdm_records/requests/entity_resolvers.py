# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Entity resolver for records aware of drafts and records."""

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError, PIDUnregistered
from invenio_records_resources.references.entity_resolvers import (
    RecordProxy,
    RecordResolver,
    ServiceResultProxy,
    ServiceResultResolver,
)
from sqlalchemy.orm.exc import NoResultFound

from invenio_rdm_records.services.config import RDMRecordServiceConfig

from ..records.api import RDMDraft, RDMRecord


class RDMRecordProxy(RecordProxy):
    """Proxy for resolve RDMDraft and RDMRecord."""

    def _resolve(self):
        """Resolve the Record from the proxy's reference dict."""
        pid_value = self._parse_ref_dict_id()

        try:
            return RDMDraft.pid.resolve(pid_value, registered_only=False)
        except (PIDUnregistered, NoResultFound):
            # try checking if it is a published record before failing
            return RDMRecord.pid.resolve(pid_value)


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

    def _resolve(self):
        """Resolve the result item from the proxy's reference dict."""
        pid_value = self._parse_ref_dict_id()

        try:
            return self.service.read_draft(system_identity, pid_value).to_dict()
        except (PIDDoesNotExistError, NoResultFound):
            return self.service.read(system_identity, pid_value).to_dict()


class RDMRecordServiceResultResolver(ServiceResultResolver):
    """Resolver for rdm record result items."""

    def __init__(self):
        """Ctor."""
        super().__init__(
            service_id=RDMRecordServiceConfig.service_id,
            type_key="record",
            proxy_cls=RDMRecordServiceResultProxy,
        )
