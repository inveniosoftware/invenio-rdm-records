# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from invenio_drafts_resources.resources import DraftActionResource, \
    DraftActionResourceConfig, DraftResource, DraftResourceConfig, \
    RecordResource, RecordResourceConfig

from .schemas import BibliographicDraftLinksSchemaV1, \
    BibliographicRecordLinksSchemaV1


class BibliographicRecordResourceConfig(RecordResourceConfig):
    """Bibliographic record resource configuration."""

    links_config = {
        **RecordResourceConfig.links_config,
        "record": BibliographicRecordLinksSchemaV1
    }

    draft_links_config = {
        **RecordResourceConfig.draft_links_config,
        "record": BibliographicDraftLinksSchemaV1
    }


class BibliographicRecordResource(RecordResource):
    """Bibliographic record resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_CONFIG"
    default_config = BibliographicRecordResourceConfig


class BibliographicDraftResourceConfig(DraftResourceConfig):
    """Bibliographic draft resource configuration."""

    links_config = {
        **DraftResourceConfig.links_config,
        "record": BibliographicDraftLinksSchemaV1
    }


class BibliographicDraftResource(DraftResource):
    """Bibliographic record draft resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_CONFIG"
    default_config = BibliographicDraftResourceConfig


class BibliographicDraftActionResourceConfig(DraftActionResourceConfig):
    """Mock service configuration."""

    list_route = "/records/<pid_value>/draft/actions/<action>"

    action_commands = {
        "publish": "publish"
    }

    record_links_config = {
        **DraftActionResourceConfig.record_links_config,
        "record": BibliographicRecordLinksSchemaV1
    }


class BibliographicDraftActionResource(DraftActionResource):
    """Bibliographic record draft actions resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_ACTION_CONFIG"
    default_config = BibliographicDraftActionResourceConfig
