# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Entity resolver for records aware of drafts and records."""

from invenio_pidstore.errors import PIDUnregistered
from invenio_records_resources.references.resolvers.records import \
    RecordProxy, RecordResolver

from ..records.api import RDMDraft, RDMRecord


class RDMRecordProxy(RecordProxy):
    """Proxy for resolve RDMDraft and RDMRecord."""

    def _resolve(self):
        """Resolve the Record from the proxy's reference dict."""
        pid_value = self._parse_ref_dict_id()

        try:
            return RDMDraft.pid.resolve(pid_value, registered_only=False)
        except PIDUnregistered:
            return RDMRecord.pid.resolve(pid_value)


class RDMRecordResolver(RecordResolver):
    """RDM Record entity resolver."""

    type_id = 'record'

    def __init__(self):
        """Initialize the resolver."""
        super().__init__(RDMDraft, "records", type_key="record",
                         proxy_cls=RDMRecordProxy)
