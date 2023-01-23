# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

import idutils
from flask_babelex import lazy_gettext as _

from .services import facets
from .services.permissions import RDMRecordPermissionPolicy
from .services.pids import providers

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
    "bibcode": {
        "label": _("Bibcode"),
        "validator": idutils.is_ads,
        "datacite": "bibcode",
    },
    "doi": {"label": _("DOI"), "validator": idutils.is_doi, "datacite": "DOI"},
    "ean13": {"label": _("EAN13"), "validator": idutils.is_ean13, "datacite": "EAN13"},
    "eissn": {"label": _("EISSN"), "validator": idutils.is_issn, "datacite": "EISSN"},
    "handle": {
        "label": _("Handle"),
        "validator": idutils.is_handle,
        "datacite": "Handle",
    },
    "igsn": {"label": _("IGSN"), "validator": always_valid, "datacite": "IGSN"},
    "isbn": {"label": _("ISBN"), "validator": idutils.is_isbn, "datacite": "ISBN"},
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
}
"""These are used for main, alternate and related identifiers."""


RDM_RECORDS_REFERENCES_SCHEMES = {
    "isni": {"label": _("ISNI"), "validator": idutils.is_isni},
    "grid": {"label": _("GRID"), "validator": always_valid},
    "crossreffunderid": {"label": _("Crossref Funder ID"), "validator": always_valid},
    "other": {"label": _("Other"), "validator": always_valid},
}
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
    "subject_nested": {
        "facet": facets.subject_nested,
        "ui": {
            "field": "subjects.scheme",
            "childAgg": {
                "field": "subjects.subject",
            },
        },
    },
}

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
}
"""Definitions of available record sort options.

.. code-block:

    "<option name>": dict(
        title=_('<title>'),
        fields=['-updated'],
    ),

"""

RDM_SEARCH = {
    "facets": ["access_status", "resource_type"],
    "sort": ["bestmatch", "newest", "oldest", "version"],
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
    "facets": ["access_status", "is_published", "resource_type"],
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
    },
    "oai": {
        "providers": ["oai"],
        "required": True,
        "label": _("OAI"),
    },
}
"""The configured persistent identifiers for records.

.. code-block:: python

    "<scheme>": {
        "providers": ["<default-provider-name>", "<provider-name>", ...],
        "required": True/False,
    }
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
