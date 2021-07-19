# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

import idutils


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

RDM_RECORDS_CUSTOM_VOCABULARIES = {}
"""Paths to custom controlled vocabularies.

Of the shape:

.. code-block:: python

    {
        '<dotted>.<path>.<to field1>': {
            'path': '<absolute path to CSV file containing it>'
        },
        # ...
        '<dotted>.<path>.<to fieldN>': {
            'path': '<absolute path to CSV file containing it>'
        }
    }

For example:

.. code-block:: python

    {
        'resource_type': {
            'path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'my_resource_types.csv'
            )
        },
        'contributors.role': {
            'path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'my_contributor_roles.csv'
            )
        }
    }
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
        "validator": idutils.is_orcid
    },
    "isni": {
        "label": _("ISNI"),
        "validator": idutils.is_isni
    },
    "gnd": {
        "label": _("GND"),
        "validator": idutils.is_gnd
    },
    "ror": {
        "label": _("ROR"),
        "validator": idutils.is_ror
    },
}
RDM_RECORDS_IDENTIFIERS_SCHEMES = {
    "ark": {
        "label": _("ARK"),
        "validator": idutils.is_ark
    },
    "arxiv": {
        "label": _("arXiv"),
        "validator": idutils.is_arxiv
    },
    "bibcode": {
        "label": _("Bibcode"),
        "validator": idutils.is_ads
    },
    "doi": {
        "label": _("DOI"),
        "validator": idutils.is_doi
    },
    "ean13": {
        "label": _("EAN13"),
        "validator": idutils.is_ean13
    },
    "eissn": {
        "label": _("EISSN"),
        "validator": idutils.is_issn
    },
    "handle": {
        "label": _("Handle"),
        "validator": idutils.is_handle
    },
    "igsn": {
        "label": _("IGSN"),
        "validator": always_valid
    },
    "isbn": {
        "label": _("ISBN"),
        "validator": idutils.is_isbn
    },
    "issn": {
        "label": _("ISSN"),
        "validator": idutils.is_issn
    },
    "istc": {
        "label": _("ISTC"),
        "validator": idutils.is_istc
    },
    "lissn": {
        "label": _("LISSN"),
        "validator": idutils.is_issn
    },
    "lsid": {
        "label": _("LSID"),
        "validator": idutils.is_lsid
    },
    "pmid": {
        "label": _("PMID"),
        "validator": idutils.is_pmid
    },
    "purl": {
        "label": _("PURL"),
        "validator": idutils.is_purl
    },
    "upc": {
        "label": _("UPC"),
        "validator": always_valid
    },
    "url": {
        "label": _("URL"),
        "validator": idutils.is_url
    },
    "urn": {
        "label": _("URN"),
        "validator": idutils.is_urn
    },
    "w3id": {
        "label": _("W3ID"),
        "validator": always_valid
    },
}
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
RDM_RECORDS_DOI_DATACITE_FORMAT = "{prefix}/{id}"
