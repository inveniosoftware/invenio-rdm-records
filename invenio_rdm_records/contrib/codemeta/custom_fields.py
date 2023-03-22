# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
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
    "code": "https://codemeta.github.io",
}


CODEMETA_CUSTOM_FIELDS = [
    KeywordCF(
        name="code:codeRepository",
        field_args={
            "validate": validate.URL(),
            "error_messages": {"validate": "You must provide a valid URL."},
        },
    ),
    KeywordCF(name="code:programmingLanguage"),
    KeywordCF(name="code:runtimePlatform"),
    KeywordCF(name="code:operatingSystem"),
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
                label="Repository URL",
                icon="linkify",
                description="URL or link where the code repository is hosted.",
            ),
        ),
        dict(
            field="code:programmingLanguage",
            ui_widget="Input",
            props=dict(
                label="Programming language",
                icon="code",
                description="Repository's programming language.",
                placeholder="Python ...",
            ),
        ),
        dict(
            field="code:runtimePlatform",
            ui_widget="Input",
            props=dict(
                label="Runtime platform",
                icon="cog",
                description="Repository runtime platform or script interpreter dependencies.",
                placeholder="Java v1, Python2.3, .Net Framework 3.0 ...",
            ),
        ),
        dict(
            field="code:operatingSystem",
            ui_widget="Input",
            props=dict(
                label="Supported operating system",
                icon="desktop",
                description="Supported operating systems.",
                placeholder="Windows 7, OSX 10.6, Android 1.6 ...",
            ),
        ),
        dict(
            field="code:developmentStatus",
            ui_widget="Dropdown",
            props=dict(
                label="Development Status",
                placeholder="Repository status",
                icon="heartbeat",
                description="Repository current status.",
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
