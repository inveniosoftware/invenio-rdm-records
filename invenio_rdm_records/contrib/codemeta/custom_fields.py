# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""CodeMeta specific custom fields.

Implements the following fields:
- Repository URL
- Programming language
- Runtime platform
- Operating system
- Development status
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import KeywordCF
from invenio_records_resources.services.records.facets import CFTermsFacet
from invenio_vocabularies.services.custom_fields import VocabularyCF
from invenio_vocabularies.services.facets import VocabularyLabels
from marshmallow import validate

CODEMETA_NAMESPACE = {
    # CodeMeta
    "code": "https://codemeta.github.io/terms/#",
}


CODEMETA_CUSTOM_FIELDS = [
    KeywordCF(
        name="code:codeRepository",
        field_args={
            "validate": validate.URL(),
            "error_messages": {"validate": _("You must provide a valid URL.")},
        },
    ),
    VocabularyCF(
        name="code:programmingLanguage",
        vocabulary_id="code:programmingLanguages",
        multiple=True,
        dump_options=False,
    ),
    VocabularyCF(
        name="code:developmentStatus",
        vocabulary_id="code:developmentStatus",
        dump_options=True,
        multiple=False,
    ),
]

CODEMETA_CUSTOM_FIELDS_UI = {
    "section": _("Software"),
    "fields": [
        dict(
            field="code:codeRepository",
            ui_widget="Input",
            props=dict(
                is_identifier=True,
                label=_("Repository URL"),
                icon="linkify",
                description=_("URL or link where the code repository is hosted."),
            ),
        ),
        dict(
            field="code:programmingLanguage",
            ui_widget="AutocompleteDropdown",
            props=dict(
                label=_("Programming language"),
                icon="code",
                description=_("Repository's programming language."),
                placeholder=_("e.g. Python ..."),
                autocompleteFrom="/api/vocabularies/code:programmingLanguages",
                autocompleteFromAcceptHeader="application/vnd.inveniordm.v1+json",
                required=False,
                multiple=True,
                clearable=True,
            ),
        ),
        dict(
            field="code:developmentStatus",
            ui_widget="Dropdown",
            props=dict(
                label=_("Development Status"),
                placeholder=_("Repository status"),
                icon="heartbeat",
                description=_("Repository current status."),
                search=False,
                multiple=False,
                clearable=True,
            ),
        ),
    ],
}

CODEMETA_FACETS = {
    "developmentStatus": {
        "facet": CFTermsFacet(
            field="code:developmentStatus.id",
            label=_("Development status"),
            value_labels=VocabularyLabels("code:developmentStatus"),
        ),
        "ui": {  # ui display
            "field": CFTermsFacet.field("code:developmentStatus.id"),
        },
    },
    "programmingLanguage": {
        "facet": CFTermsFacet(
            field="code:programmingLanguage",
            label=_("Programming language"),
        ),
        "ui": {  # ui display
            "field": CFTermsFacet.field("code:programmingLanguage"),
        },
    },
}
