# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020-2024 Northwestern University.
# Copyright (C)      2021 TU Wien.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Facet definitions."""

from warnings import warn

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.records.facets import (
    CombinedTermsFacet,
    NestedTermsFacet,
    TermsFacet,
)
from invenio_vocabularies.contrib.subjects import SubjectsLabels
from invenio_vocabularies.records.models import VocabularyScheme
from invenio_vocabularies.services.facets import VocabularyLabels

from ..records.dumpers.combined_subjects import SPLITCHAR
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


filetype = TermsFacet(
    field="files.types",
    label=_("File type"),
    value_labels=lambda ids: {id: id.upper() for id in ids},
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


def deprecated_subject_nested():
    """Deprecated NestedTermsFacet.

    Will warn until this is completely removed.
    """
    warn(
        "subject_nested is deprecated. Use subject_combined instead.",
        DeprecationWarning,
    )
    return NestedTermsFacet(
        field="metadata.subjects.scheme",
        subfield="metadata.subjects.subject.keyword",
        label=_("Subjects"),
        value_labels=SubjectsLabels(),
    )


subject_nested = deprecated_subject_nested()


subject = TermsFacet(
    field="metadata.subjects.subject.keyword",
    label=_("Subjects"),
)


def get_subject_schemes():
    """Return subject schemes."""
    return [
        row.id for row in VocabularyScheme.query.filter_by(parent_id="subjects").all()
    ]


subject_combined = CombinedTermsFacet(
    field="metadata.subjects.scheme",
    combined_field="metadata.combined_subjects",
    parents=get_subject_schemes,
    splitchar=SPLITCHAR,
    label=_("Subjects"),
    value_labels=SubjectsLabels(),
)
