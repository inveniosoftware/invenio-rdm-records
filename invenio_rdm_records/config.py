# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

import idutils

from .services import facets


def _(x):
    """Identity function for string extraction."""
    return x


# Files REST

# FILES_REST_PERMISSION_FACTORY = record_files_permission_factory
"""Set default files permission factory."""

# Invenio-RDM-Records
# ===================

RDM_RECORDS_METADATA_NAMESPACES = {}
"""Namespaces for fields *added* to the metadata schema.

Of the shape:

.. code-block:: python

    {
        '<prefix1>': {
            '@context': '<url>'
        },
        # ...
        '<prefixN>': {
            '@context': '<url>'
        }
    }

For example:

.. code-block:: python

    {
        'dwc': {
            '@context': 'http://rs.tdwg.org/dwc/terms/'
        },
        'z':{
            '@context': 'https://zenodo.org/terms'
        }
    }

Use :const:`invenio_rdm_records.config.RDM_RECORDS_METADATA_EXTENSIONS` to
define the added fields.

See :class:`invenio_rdm_records.services.schemas.\
metadata_extensions.MetadataExtensions` for
how this configuration variable is used.
"""

RDM_RECORDS_METADATA_EXTENSIONS = {}
"""Fields added to the metadata schema.

Of the shape:

.. code-block:: python

    {
        '<prefix1>:<field1>': {
            'elasticsearch': '<allowed elasticsearch type>'
            'marshmallow': '<allowed marshmallow type>'
        },
        # ...
        '<prefixN>:<fieldN>': {
            'elasticsearch': '<allowed elasticsearch type>'
            'marshmallow': '<allowed marshmallow type>'
        }
    }

For example:

.. code-block:: python

    {
        'dwc:family': {
            'elasticsearch': 'keyword',
            'marshmallow': SanitizedUnicode()
        },
        'dwc:behavior': {
            'elasticsearch': 'text',
            'marshmallow': SanitizedUnicode()
        },
        'z:department': {
            'elasticsearch': 'text',
            'marshmallow': SanitizedUnicode()
        }
    }

Use :const:`invenio_rdm_records.config.RDM_RECORDS_METADATA_NAMESPACES` to
define the prefixes.

See :class:`invenio_rdm_records.services.schemas.\
metadata_extensions.MetadataExtensions` for
allowed types and how this configuration variable is used.
"""

RDM_RECORDS_USER_FIXTURE_PASSWORDS = {
    "admin@inveniosoftware.org": None
}
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

#: Default site URL (used only when not in a context - e.g. like celery tasks).
THEME_SITEURL = "http://127.0.0.1:5000"

#: DataCite DOI credentials
RDM_RECORDS_DOI_DATACITE_ENABLED = True
RDM_RECORDS_DOI_DATACITE_USERNAME = ""
RDM_RECORDS_DOI_DATACITE_PASSWORD = ""
RDM_RECORDS_DOI_DATACITE_PREFIX = "10.1234"
RDM_RECORDS_DOI_DATACITE_TEST_MODE = True
RDM_RECORDS_DOI_DATACITE_FORMAT = "{prefix}/{id}"

# PID Schemes


def always_valid(identifier):
    """Gives every identifier as valid."""
    return True


RDM_RECORDS_RECORD_PID_SCHEMES = {
    "doi": {
        "label": _("DOI"),
        "validator": idutils.is_doi
    }
}
RDM_RECORDS_PERSONORG_SCHEMES = {
    "orcid": {
        "label": _("ORCID"),
        "validator": idutils.is_orcid,
        "datacite": "ORCID"
    },
    "isni": {
        "label": _("ISNI"),
        "validator": idutils.is_isni,
        "datacite": "ISNI"
    },
    "gnd": {
        "label": _("GND"),
        "validator": idutils.is_gnd,
        "datacite": "GND"
    },
    "ror": {
        "label": _("ROR"),
        "validator": idutils.is_ror,
        "datacite": "ROR"
    },
}


RDM_RECORDS_IDENTIFIERS_SCHEMES = {
    "ark": {
        "label": _("ARK"),
        "validator": idutils.is_ark,
        "datacite": "ARK"
    },
    "arxiv": {
        "label": _("arXiv"),
        "validator": idutils.is_arxiv,
        "datacite": "arXiv"
    },
    "bibcode": {
        "label": _("Bibcode"),
        "validator": idutils.is_ads,
        "datacite": "bibcode"
    },
    "doi": {
        "label": _("DOI"),
        "validator": idutils.is_doi,
        "datacite": "DOI"
    },
    "ean13": {
        "label": _("EAN13"),
        "validator": idutils.is_ean13,
        "datacite": "EAN13"
    },
    "eissn": {
        "label": _("EISSN"),
        "validator": idutils.is_issn,
        "datacite": "EISSN"
    },
    "handle": {
        "label": _("Handle"),
        "validator": idutils.is_handle,
        "datacite": "Handle"
    },
    "igsn": {
        "label": _("IGSN"),
        "validator": always_valid,
        "datacite": "IGSN"
    },
    "isbn": {
        "label": _("ISBN"),
        "validator": idutils.is_isbn,
        "datacite": "ISBN"
    },
    "issn": {
        "label": _("ISSN"),
        "validator": idutils.is_issn,
        "datacite": "ISSN"
    },
    "istc": {
        "label": _("ISTC"),
        "validator": idutils.is_istc,
        "datacite": "ISTC"
    },
    "lissn": {
        "label": _("LISSN"),
        "validator": idutils.is_issn,
        "datacite": "LISSN"
    },
    "lsid": {
        "label": _("LSID"),
        "validator": idutils.is_lsid,
        "datacite": "LSID"
    },
    "pmid": {
        "label": _("PMID"),
        "validator": idutils.is_pmid,
        "datacite": "PMID"
    },
    "purl": {
        "label": _("PURL"),
        "validator": idutils.is_purl,
        "datacite": "PURL"
    },
    "upc": {
        "label": _("UPC"),
        "validator": always_valid,
        "datacite": "UPC"
    },
    "url": {
        "label": _("URL"),
        "validator": idutils.is_url,
        "datacite": "URL"
    },
    "urn": {
        "label": _("URN"),
        "validator": idutils.is_urn,
        "datacite": "URN"
    },
    "w3id": {
        "label": _("W3ID"),
        "validator": always_valid,
        "datacite": "w3id"
    },
}
"""These are used for main, alternate and related identifiers."""


RDM_RECORDS_REFERENCES_SCHEMES = {
    "isni": {
        "label": _("ISNI"),
        "validator": idutils.is_isni
    },
    "grid": {
        "label": _("GRID"),
        "validator": always_valid
    },
    "crossreffunderid": {
        "label": _("Crossref Funder ID"),
        "validator": always_valid
    },
    "other": {
        "label": _("Other"),
        "validator": always_valid
    }
}
RDM_RECORDS_LOCATION_SCHEMES = {
    "wikidata": {
        "label": _("Wikidata"),
        "validator": always_valid
    },
    "geonames": {
        "label": _("GeoNames"),
        "validator": always_valid
    }
}


#
# Record permission policy
#
RDM_PERMISSION_POLICY = None
"""Override the default record permission policy."""


#
# Search configuration
#
RDM_FACETS = {
    'access_status': {
        'facet': facets.access_status,
        'ui': {
            'field': 'access.status',
        }
    },
    'is_published': {
        'facet': facets.is_published,
        'ui': {
            'field': 'is_published',
        }
    },
    'language': {
        'facet': facets.language,
        'ui': {
            'field': 'languages',
        }
    },
    'resource_type': {
        'facet': facets.resource_type,
        'ui': {
            'field': 'resource_type.type',
            'childAgg': {
                'field': 'resource_type.subtype',
            }
        }
    },
    'subject': {
        'facet': facets.subject,
        'ui': {
            'field': 'subjects.subject',
        }
    },
    'subject_nested': {
        'facet': facets.subject_nested,
        'ui': {
            'field': 'subjects.scheme',
            'childAgg': {
                'field': 'subjects.subject',
            }
        }
    },
}

RDM_SORT_OPTIONS = {
    "bestmatch": dict(
        title=_('Best match'),
        fields=['_score'],  # ES defaults to desc on `_score` field
    ),
    "newest": dict(
        title=_('Newest'),
        fields=['-created'],
    ),
    "oldest": dict(
        title=_('Oldest'),
        fields=['created'],
    ),
    "version": dict(
        title=_('Version'),
        fields=['-versions.index'],
    ),
    "updated-desc": dict(
        title=_('Recently updated'),
        fields=['-updated'],
    ),
    "updated-asc": dict(
        title=_('Least recently updated'),
        fields=['updated'],
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
    'facets': ['access_status', 'resource_type'],
    'sort': ['bestmatch', 'newest', 'oldest', 'version']
}
"""Record search configuration.

The configuration has two possible keys:

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
    'facets': ['access_status', 'is_published', 'resource_type'],
    'sort': ['bestmatch', 'updated-desc', 'updated-asc', 'newest', 'oldest',
             'version'],
}
"""User records search configuration (i.e. list of uploads)."""

RDM_SEARCH_VERSIONING = {
    'facets': [],
    'sort': ['version'],
    'sort_default': 'version',
    'sort_default_no_query': 'version',
}
"""Records versions search configuration (list of versions for a record)."""
