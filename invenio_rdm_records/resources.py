# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from invenio_drafts_resources.resources import DraftActionResource, \
    DraftActionResourceConfig, DraftResource, DraftResourceConfig
from invenio_records_resources.resources import RecordResource, \
    RecordResourceConfig
from invenio_records_resources.resources.record_response import RecordResponse


class BibliographicRecordResource(RecordResource):
    """Bibliographic record resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_CONFIG"


class BibliographicDraftResource(DraftResource):
    """Bibliographic record draft resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_CONFIG"


class BibliographicDraftActionResourceConfig(DraftActionResourceConfig):
    """Mock service configuration."""

    list_route = "/records/<pid_value>/draft/actions/<action>"

    action_commands = {
        "publish": "publish"
    }


class BibliographicDraftActionResource(DraftActionResource):
    """Bibliographic record draft actions resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_ACTION_CONFIG"

    default_config = BibliographicDraftActionResourceConfig
