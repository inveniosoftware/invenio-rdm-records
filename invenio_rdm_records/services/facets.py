# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C)      2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Facet definitions."""

from flask_babelex import gettext as _
from invenio_records_resources.services.records.facets import (
    NestedTermsFacet,
    TermsFacet,
)
from invenio_vocabularies.contrib.subjects import SubjectsLabels
from invenio_vocabularies.services.facets import VocabularyLabels

from ..records.systemfields.access.field.record import AccessStatusEnum

access_status = TermsFacet(
    field="access.status",
    label=_("Access status"),
    value_labels={
        AccessStatusEnum.OPEN.value: _("Open"),
        AccessStatusEnum.EMBARGOED.value: _("Embargoed"),
        AccessStatusEnum.RESTRICTED.value: _("Restricted"),
        AccessStatusEnum.METADATA_ONLY.value: _("Metadata-only"),
    },
)


is_published = TermsFacet(
    field="is_published",
    label=_("Status"),
    value_labels={"true": _("Published"), "false": _("Unpublished")},
)


language = TermsFacet(
    field="metadata.languages.id",
    label=_("Languages"),
    value_labels=VocabularyLabels("languages"),
)


resource_type = NestedTermsFacet(
    field="metadata.resource_type.props.type",
    subfield="metadata.resource_type.props.subtype",
    splitchar="::",
    label=_("Resource types"),
    value_labels=VocabularyLabels("resourcetypes"),
)


subject_nested = NestedTermsFacet(
    field="metadata.subjects.scheme",
    subfield="metadata.subjects.subject.keyword",
    label=_("Subjects"),
    value_labels=SubjectsLabels(),
)

subject = TermsFacet(
    field="metadata.subjects.subject.keyword",
    label=_("Subjects"),
)
