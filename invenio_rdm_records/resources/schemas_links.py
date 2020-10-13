# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from invenio_drafts_resources.resources import DraftLinksSchema
from invenio_records_resources.resources import RecordLinksSchema
from invenio_records_resources.resources.records.schemas_links import \
    SearchLinksSchema, search_link_params, search_link_when
from marshmallow_utils.fields import Link
from uritemplate import URITemplate


class BibliographicDraftLinksSchemaV1(DraftLinksSchema):
    """Draft Links schema."""

    # WARNING: It was intentionally decided that if
    #          config.py::RECORDS_UI_ENDPOINTS is changed by the instance,
    #          the instance also needs to overwrite this Schema (in the
    #          links_config)
    self_html = Link(
        template=URITemplate("/uploads/{pid_value}"),
        permission="read",
        params=lambda record: {'pid_value': record.pid.pid_value}
    )


class BibliographicRecordLinksSchemaV1(RecordLinksSchema):
    """Record Links schema."""

    # WARNING: It was intentionally decided that if
    #          config.py::RECORDS_UI_ENDPOINTS is changed by the instance,
    #          the instance also needs to overwrite this Schema (in the
    #          links_config)
    self_html = Link(
        template=URITemplate("/records/{pid_value}"),
        permission="read",
        params=lambda record: {'pid_value': record.pid.pid_value}
    )


class BibliographicUserRecordsSearchLinksSchemaV1(SearchLinksSchema):
    """User Record Links schema."""

    self = Link(
        template=URITemplate("/api/user/records{?params*}"),
        permission="search",
        params=search_link_params(0)
    )
    prev = Link(
        template=URITemplate("/api/user/records{?params*}"),
        permission="search",
        params=search_link_params(-1),
        when=search_link_when(-1)
    )
    next = Link(
        template=URITemplate("/api/user/records{?params*}"),
        permission="search",
        params=search_link_params(+1),
        when=search_link_when(+1)
    )
