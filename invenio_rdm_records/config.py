# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019 Northwestern University.
# Copyright (C) 2021-2024 Graz University of Technology.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from datetime import timedelta

import idutils
from invenio_access.permissions import system_permission
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_records_resources.services.records.queryparser.transformer import (
    RestrictedTerm,
    RestrictedTermValue,
    SearchFieldTransformer,
)

import invenio_rdm_records.services.communities.moderation as communities_moderation
from invenio_rdm_records.services.components.pids import validate_optional_doi
from invenio_rdm_records.services.components.verified import UserModerationHandler

from . import tokens
from .resources.serializers import DataCite43JSONSerializer
from .services import facets
from .services.config import lock_edit_published_files
from .services.permissions import RDMRecordPermissionPolicy
from .services.pids import providers
from .services.queryparser import word_internal_notes

# Invenio-RDM-Records
# ===================

RDM_RECORDS_USER_FIXTURE_PASSWORDS = {"admin@inveniosoftware.org": None}
"""Overrides for the user fixtures' passwords.

The password set for a user fixture in this dictionary overrides the
password set in the ``users.yaml`` file. This can be used to set custom
passwords for the fixture users (of course, this has to be configured
before the fixtures are installed, e.g. by setting up the services).
If ``None`` or an empty string is configured in this dictionary, then the
password from ``users.yaml`` will be used. If that is also absent, a password
will be generated randomly.
"""

RDM_RECORDS_UI_EDIT_URL = "/uploads/<pid_value>"
"""Default UI URL for the edit page of a Bibliographic Record."""

RDM_ARCHIVE_DOWNLOAD_ENABLED = True
"""Flag to enable/disable the all-in-one download endpoint."""

#: Default site URL (used only when not in a context - e.g. like celery tasks).
THEME_SITEURL = "http://127.0.0.1:5000"


def always_valid(identifier):
    """Gives every identifier as valid."""
    return True


RDM_RECORDS_PERSONORG_SCHEMES = {
    "orcid": {"label": _("ORCID"), "validator": idutils.is_orcid, "datacite": "ORCID"},
    "isni": {"label": _("ISNI"), "validator": idutils.is_isni, "datacite": "ISNI"},
    "gnd": {"label": _("GND"), "validator": idutils.is_gnd, "datacite": "GND"},
    "ror": {"label": _("ROR"), "validator": idutils.is_ror, "datacite": "ROR"},
}

RDM_RECORDS_IDENTIFIERS_SCHEMES = {
    "ark": {"label": _("ARK"), "validator": idutils.is_ark, "datacite": "ARK"},
    "arxiv": {"label": _("arXiv"), "validator": idutils.is_arxiv, "datacite": "arXiv"},
    "ads": {
        "label": _("Bibcode"),
        "validator": idutils.is_ads,
        "datacite": "bibcode",
    },
    "crossreffunderid": {
        "label": _("Crossref Funder ID"),
        "validator": always_valid,
        "datacite": "Crossref Funder ID",
    },
    "doi": {"label": _("DOI"), "validator": idutils.is_doi, "datacite": "DOI"},
    "ean13": {"label": _("EAN13"), "validator": idutils.is_ean13, "datacite": "EAN13"},
    "eissn": {"label": _("EISSN"), "validator": idutils.is_issn, "datacite": "EISSN"},
    "grid": {"label": _("GRID"), "validator": always_valid, "datacite": "GRID"},
    "handle": {
        "label": _("Handle"),
        "validator": idutils.is_handle,
        "datacite": "Handle",
    },
    "igsn": {"label": _("IGSN"), "validator": always_valid, "datacite": "IGSN"},
    "isbn": {"label": _("ISBN"), "validator": idutils.is_isbn, "datacite": "ISBN"},
    "isni": {"label": _("ISNI"), "validator": idutils.is_isni, "datacite": "ISNI"},
    "issn": {"label": _("ISSN"), "validator": idutils.is_issn, "datacite": "ISSN"},
    "istc": {"label": _("ISTC"), "validator": idutils.is_istc, "datacite": "ISTC"},
    "lissn": {"label": _("LISSN"), "validator": idutils.is_issn, "datacite": "LISSN"},
    "lsid": {"label": _("LSID"), "validator": idutils.is_lsid, "datacite": "LSID"},
    "pmid": {"label": _("PMID"), "validator": idutils.is_pmid, "datacite": "PMID"},
    "purl": {"label": _("PURL"), "validator": idutils.is_purl, "datacite": "PURL"},
    "upc": {"label": _("UPC"), "validator": always_valid, "datacite": "UPC"},
    "url": {"label": _("URL"), "validator": idutils.is_url, "datacite": "URL"},
    "urn": {"label": _("URN"), "validator": idutils.is_urn, "datacite": "URN"},
    "w3id": {"label": _("W3ID"), "validator": always_valid, "datacite": "w3id"},
    "other": {"label": _("Other"), "validator": always_valid, "datacite": "Other"},
}
"""These are used for references, main, alternate and related identifiers."""

RDM_RECORDS_LOCATION_SCHEMES = {
    "wikidata": {"label": _("Wikidata"), "validator": always_valid},
    "geonames": {"label": _("GeoNames"), "validator": always_valid},
}

#
# Record permission policy
#
RDM_PERMISSION_POLICY = RDMRecordPermissionPolicy
"""Override the default record permission policy."""

#
# Record review requests
#
RDM_RECORDS_REVIEWS = [
    "community-submission",
]

#
# Record files configuration
#
RDM_ALLOW_METADATA_ONLY_RECORDS = True
"""Allow users to publish metadata-only records."""

RDM_DEFAULT_FILES_ENABLED = True
"""Deposit page files enabled value on new records."""

#
# Record access
#
RDM_ALLOW_RESTRICTED_RECORDS = True
"""Allow users to set restricted/private records."""

#
# Record communities
#
RDM_COMMUNITY_REQUIRED_TO_PUBLISH = False
"""Enforces at least one community per record."""

#
# Search configuration
#
RDM_FACETS = {
    "access_status": {
        "facet": facets.access_status,
        "ui": {
            "field": "access.status",
        },
    },
    "is_published": {
        "facet": facets.is_published,
        "ui": {
            "field": "is_published",
        },
    },
    "file_type": {
        "facet": facets.filetype,
        "ui": {
            "field": "files.types",
        },
    },
    "language": {
        "facet": facets.language,
        "ui": {
            "field": "languages",
        },
    },
    "resource_type": {
        "facet": facets.resource_type,
        "ui": {
            "field": "resource_type.type",
            "childAgg": {
                "field": "resource_type.subtype",
            },
        },
    },
    "subject": {
        "facet": facets.subject,
        "ui": {
            "field": "subjects.subject",
        },
    },
    # subject_nested is deprecated and should be removed.
    # subject_combined does require a pre-existing change to indexed documents,
    # so it's unclear if a direct replacement is right.
    # Keeping it around until v13 might be better. On the flipside it is an incorrect
    # facet...
    "subject_nested": {
        "facet": facets.subject_nested,
        "ui": {
            "field": "subjects.scheme",
            "childAgg": {
                "field": "subjects.subject",
            },
        },
    },
    "subject_combined": {
        "facet": facets.subject_combined,
        "ui": {
            "field": "subjects.scheme",
            "childAgg": {
                "field": "subjects.subject",
            },
        },
    },
}

RDM_SEARCH_SORT_BY_VERIFIED = False
"""Sort records by 'verified' first."""

RDM_SORT_OPTIONS = {
    "bestmatch": dict(
        title=_("Best match"),
        fields=["_score"],  # search defaults to desc on `_score` field
    ),
    "newest": dict(
        title=_("Newest"),
        fields=["-created"],
    ),
    "oldest": dict(
        title=_("Oldest"),
        fields=["created"],
    ),
    "version": dict(
        title=_("Version"),
        fields=["-versions.index"],
    ),
    "updated-desc": dict(
        title=_("Recently updated"),
        fields=["-updated"],
    ),
    "updated-asc": dict(
        title=_("Least recently updated"),
        fields=["updated"],
    ),
    "mostviewed": dict(
        title=_("Most viewed"), fields=["-stats.all_versions.unique_views"]
    ),
    "mostdownloaded": dict(
        title=_("Most downloaded"), fields=["-stats.all_versions.unique_downloads"]
    ),
}
"""Definitions of available record sort options.

.. code-block:

    "<option name>": dict(
        title=_('<title>'),
        fields=['-updated'],
    ),

"""


RDM_SEARCH = {
    "facets": ["access_status", "file_type", "resource_type"],
    "sort": [
        "bestmatch",
        "newest",
        "oldest",
        "version",
        "mostviewed",
        "mostdownloaded",
    ],
    "query_parser_cls": QueryParser.factory(
        mapping={
            "internal_notes.note": RestrictedTerm(system_permission),
            "internal_notes.id": RestrictedTerm(system_permission),
            "internal_notes.added_by": RestrictedTerm(system_permission),
            "internal_notes.timestamp": RestrictedTerm(system_permission),
            "_exists_": RestrictedTermValue(
                system_permission, word=word_internal_notes
            ),
        },
        tree_transformer_cls=SearchFieldTransformer,
    ),
}
"""Record search configuration.

The configuration has four possible keys:

- ``facets`` - A list of facet names which must have been defined in
  ``RDM_FACETS``.
- ``sort`` -  A list of sort option names which must have been defined in
  ``RDM_SORT_OPTIONS``.
- ``sort_default`` - The default sort option when a query is provided. Must be
  a single sort option name which must have been defined in
  ``RDM_SORT_OPTIONS``. If not provided, will use the first element of
  the ``sort`` list.
- ``sort_default_no_query`` - The default sort option when no query is
  provided. Must be a single sort option name which must have been defined in
  ``RDM_SORT_OPTIONS``. If not provided, will use the second element of
  the ``sort`` list.
"""

RDM_SEARCH_DRAFTS = {
    "facets": ["access_status", "is_published", "resource_type", "file_type"],
    "sort": ["bestmatch", "updated-desc", "updated-asc", "newest", "oldest", "version"],
}
"""User records search configuration (i.e. list of uploads)."""

RDM_SEARCH_VERSIONING = {
    "facets": [],
    "sort": ["version"],
    "sort_default": "version",
    "sort_default_no_query": "version",
}
"""Records versions search configuration (list of versions for a record)."""

#
# OAI-PMH Search configuration
#
RDM_OAI_PMH_FACETS = {}

RDM_OAI_PMH_SORT_OPTIONS = {
    "name": dict(
        title=_("Set name"),
        fields=["name"],
    ),
    "spec": dict(
        title=_("Set spec"),
        fields=["spec"],
    ),
    "created": dict(
        title=_("Created"),
        fields=["created"],
    ),
    "updated": dict(
        title=_("Updated"),
        fields=["updated"],
    ),
}
"""Definitions of available OAI-PMH sort options. """

RDM_OAI_PMH_SEARCH = {
    "facets": [],
    "sort": ["name", "spec", "created", "updated"],
}
"""OAI-PMH search configuration."""

#
# Persistent identifiers configuration
#
RDM_PERSISTENT_IDENTIFIER_PROVIDERS = [
    # DataCite DOI provider
    providers.DataCitePIDProvider(
        "datacite",
        client=providers.DataCiteClient("datacite", config_prefix="DATACITE"),
        label=_("DOI"),
    ),
    # DOI provider for externally managed DOIs
    providers.ExternalPIDProvider(
        "external",
        "doi",
        validators=[providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])],
        label=_("DOI"),
    ),
    # OAI identifier
    providers.OAIPIDProvider(
        "oai",
        label=_("OAI ID"),
    ),
]
"""A list of configured persistent identifier providers.

ATTENTION: All providers (and clients) takes a name as the first parameter.
This name is stored in the database and used in the REST API in order to
identify the given provider and client.

The name is further used to configure the desired persistent identifiers (see
``RDM_PERSISTENT_IDENTIFIERS`` below)
"""

RDM_PERSISTENT_IDENTIFIERS = {
    # DOI automatically removed if DATACITE_ENABLED is False.
    "doi": {
        "providers": ["datacite", "external"],
        "required": True,
        "label": _("DOI"),
        "validator": idutils.is_doi,
        "normalizer": idutils.normalize_doi,
        "is_enabled": providers.DataCitePIDProvider.is_enabled,
        "ui": {"default_selected": "yes"},  # "yes", "no" or "not_needed"
    },
    "oai": {
        "providers": ["oai"],
        "required": True,
        "label": _("OAI"),
        "is_enabled": providers.OAIPIDProvider.is_enabled,
    },
}
"""The configured persistent identifiers for records.

.. code-block:: python

    "<scheme>": {
        "providers": ["<default-provider-name>", "<provider-name>", ...],
        "required": True/False,
    }
"""

RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS = [
    # DataCite Concept DOI provider
    providers.DataCitePIDProvider(
        "datacite",
        client=providers.DataCiteClient("datacite", config_prefix="DATACITE"),
        serializer=DataCite43JSONSerializer(schema_context={"is_parent": True}),
        label=_("Concept DOI"),
    ),
]
"""Persistent identifier providers for parent record."""

RDM_PARENT_PERSISTENT_IDENTIFIERS = {
    "doi": {
        "providers": ["datacite"],
        "required": True,
        "condition": lambda rec: rec.pids.get("doi", {}).get("provider") == "datacite",
        "label": _("Concept DOI"),
        "validator": idutils.is_doi,
        "normalizer": idutils.normalize_doi,
        "is_enabled": providers.DataCitePIDProvider.is_enabled,
    },
}
"""Persistent identifiers for parent record."""

RDM_ALLOW_EXTERNAL_DOI_VERSIONING = True
"""Allow records with external DOIs to be versioned."""


RDM_OPTIONAL_DOI_VALIDATOR = validate_optional_doi
"""Optional DOI transitions validate method.

Check the signature of validate_optional_doi for more information.
"""


# Configuration for the DataCiteClient used by the DataCitePIDProvider

DATACITE_ENABLED = False
"""Flag to enable/disable DOI registration."""

DATACITE_USERNAME = ""
"""DataCite username."""

DATACITE_PASSWORD = ""
"""DataCite password."""

DATACITE_PREFIX = ""
"""DataCite DOI prefix."""

DATACITE_TEST_MODE = True
"""DataCite test mode enabled."""

DATACITE_FORMAT = "{prefix}/{id}"
"""A string used for formatting the DOI or a callable.

If set to a string, you can used ``{prefix}`` and ``{id}`` inside the string.

You can also provide a callable instead:

.. code-block:: python

    def make_doi(prefix, record):
        return f"{prefix}/{record.pid.pid_value}"

    DATACITE_FORMAT = make_doi
"""

DATACITE_DATACENTER_SYMBOL = ""
"""DataCite data center symbol.

This is only required if you want your records to be harvestable (OAI-PMH)
in DataCite XML format.
"""

#
# Custom fields
#
RDM_NAMESPACES = {}
"""Custom fields namespaces.

.. code-block:: python

    {<namespace>: <uri>, ...}

For example:

.. code-block:: python

    {
        "cern": "https://cern.ch/terms",
        "dwc": "http://rs.tdwg.org/dwc/terms/"
    }

"""

RDM_CUSTOM_FIELDS = []
"""Records custom fields definition.

.. code-block:: python

    [<custom-field-class-type>, <custom-field-class-type>, ...]

For example:

.. code-block:: python

    [TextCF(name="experiment"), ...]
"""

RDM_CUSTOM_FIELDS_UI = []
"""Upload form custom fields UI configuration.

Of the shape:

.. code-block:: python

    [{
        section: <section_name>,
        fields: [
            {
                field: "path-to-field",  # this should be validated against the defined fields in `RDM_CUSTOM_FIELDS`
                ui_widget: "<ui-widget-name>",  # predefined or user defined ui widget
                props: {
                    label:"<ui-label-to-display>",
                    placeholder:"<placeholder-passed-to-widget>",
                    icon:"<icon-passed-to-widget>",
                    description:"<description-passed-to-widget>",
                }
            },
        ],

        # ...
    }]

For example:

.. code-block:: python

    [{
        "section": "CERN Experiment"
        "fields" : [{
            field: "experiment",  # this should be validated against the defined fields in `RDM_CUSTOM_FIELDS`
            ui_widget: "CustomTextField",  # user defined widget in my-site
            props: {
                label: "Experiment",
                placeholder: "Type an experiment...",
                icon: "pencil",
                description: "You should fill this field with one of the experiments e.g LHC, ATLAS etc.",
            }
        },
        ...
    }]
"""

# Feature flag to enable/disable Resource access tokens (RATs)
RDM_RESOURCE_ACCESS_TOKENS_ENABLED = False
"""Flag to show whether RATs feature should be enabled."""

# Configuration for Resource Access Tokens.
RDM_RESOURCE_ACCESS_TOKENS_JWT_LIFETIME = timedelta(minutes=30)
"""Maximum tokens lifetime."""

RDM_RESOURCE_ACCESS_TOKENS_WHITELISTED_JWT_ALGORITHMS = ["HS256", "HS384", "HS512"]
"""Accepted JWT algorithms for decoding the RAT."""

RDM_RESOURCE_ACCESS_TOKEN_REQUEST_ARG = "resource_access_token"
"""URL argument to provide resource access token."""

RDM_RESOURCE_ACCESS_TOKENS_SUBJECT_SCHEMA = tokens.resource_access.SubjectSchema
"""Resource access token Marshmallow schema for parsing JWT subject."""

RDM_LOCK_EDIT_PUBLISHED_FILES = lock_edit_published_files
"""Lock editing already published files (enforce record versioning).

   signature to implement:
   def lock_edit_published_files(service, identity, record=None, draft=None):
"""

RDM_CONTENT_MODERATION_HANDLERS = [
    UserModerationHandler(),
]
"""Records content moderation handlers."""

RDM_COMMUNITY_CONTENT_MODERATION_HANDLERS = [
    communities_moderation.UserModerationHandler(),
]
"""Community content moderation handlers."""

# Feature flag to enable/disable user moderation
RDM_USER_MODERATION_ENABLED = False
"""Flag to enable creation of user moderation requests on specific user actions."""

RDM_RECORDS_MAX_FILES_COUNT = 100
"""Max amount of files allowed to upload in the deposit form."""

RDM_RECORDS_MAX_MEDIA_FILES_COUNT = 100
"""Max amount of media files allowed to upload in the deposit form."""

RDM_MEDIA_FILES_DEFAULT_QUOTA_SIZE = 10 * (10**9)  # 10 GB
"""Default size for a bucket in bytes for media files."""

RDM_MEDIA_FILES_DEFAULT_MAX_FILE_SIZE = 10 * (10**9)  # 10 GB
"""Default maximum file size for a bucket in bytes for media files."""

# For backwards compatibility,
# FILES_REST_DEFAULT_QUOTA_SIZE & FILES_REST_DEFAULT_MAX_FILE_SIZE
# are used respectively instead
RDM_FILES_DEFAULT_QUOTA_SIZE = None
"""Default size for a bucket in bytes for files."""

RDM_FILES_DEFAULT_MAX_FILE_SIZE = None
"""Default maximum file size for a bucket in bytes for files."""


RDM_DATACITE_FUNDER_IDENTIFIERS_PRIORITY = ("ror", "doi", "grid", "isni", "gnd")
"""Priority of funder identifiers types to be used for DataCite serialization."""

RDM_IIIF_MANIFEST_FORMATS = [
    "gif",
    "jp2",
    "jpeg",
    "jpg",
    "png",
    "tif",
    "tiff",
]
"""Formats to be included in the IIIF Manifest."""

#
# IIIF Tiles configuration
#
IIIF_TILES_GENERATION_ENABLED = False
"""Enable generating pyramidal TIFF tiles for uploaded images."""

IIIF_TILES_VALID_EXTENSIONS = [
    "jp2",
    "jpeg",
    "jpg",
    "pdf",  # We can still generate tiles for the first page of a PDF
    "png",
    "png",
    "tif",
    "tiff",
]
"""Valid (normalized) file extensions for generating tiles."""

IIIF_TILES_STORAGE_BASE_PATH = "images/"
"""Base path for storing IIIF tiles.

Relative paths are resolved against the application instance path.
"""

IIIF_TILES_CONVERTER_PARAMS = {
    "compression": "jpeg",
    "Q": 90,
    "tile_width": 256,
    "tile_height": 256,
}
"""Parameters to be passed to the tiles converter."""

RDM_RECORDS_RESTRICTION_GRACE_PERIOD = timedelta(days=30)
"""Grace period for changing record access to restricted."""

RDM_RECORDS_ALLOW_RESTRICTION_AFTER_GRACE_PERIOD = False
"""Whether record access restriction is allowed after the grace period or not."""
