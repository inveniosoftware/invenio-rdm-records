# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Entity resolver for records aware of drafts and records."""

from invenio_pidstore.errors import PIDUnregistered
from invenio_records_resources.references.entity_resolvers import (
    RecordProxy,
    RecordResolver,
)
from sqlalchemy.orm.exc import NoResultFound

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
            RDMDraft, "records", type_key="record", proxy_cls=RDMRecordProxy
        )

    def matches_entity(self, entity):
        """Check if the entity is a draft or a record."""
        return isinstance(entity, (RDMDraft, RDMRecord))
