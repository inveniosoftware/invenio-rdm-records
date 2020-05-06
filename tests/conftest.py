# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modifya
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""
from copy import deepcopy
from datetime import date

import pytest
from invenio_app.factory import create_app as _create_app

from invenio_rdm_records import config


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture."""
    return {}


@pytest.fixture(scope='module')
def app_config(app_config):
    """Override pytest-invenio app_config fixture.

    For test purposes we need to enforce the configuration variables set in
    config.py. Because invenio-rdm-records is not a flavour extension, it does
    not enforce them via a config entrypoint or ext.py; only flavour
    extensions are allowed to forcefully set configuration.

    This means there is a clash between configuration set by
    invenio-records-rest and this module for instance. We want this module's
    config.py to apply in tests.
    """
    supported_configurations = [
        'FILES_REST_PERMISSION_FACTORY',
        'PIDSTORE_RECID_FIELD',
        'RECORDS_REST_ENDPOINTS',
        'RECORDS_REST_FACETS',
        'RECORDS_REST_SORT_OPTIONS',
        'RECORDS_REST_DEFAULT_SORT',
        'RECORDS_FILES_REST_ENDPOINTS',
        'RECORDS_PERMISSIONS_RECORD_POLICY'
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    return app_config


@pytest.fixture(scope='module')
def create_app():
    """Create app fixture for UI+API app."""
    return _create_app


@pytest.fixture(scope='function')
def full_input_record():
    """Full record data as dict coming from the external world."""
    return {
        "_access": {
            "metadata_restricted": False,
            "files_restricted": False
        },
        "_created_by": 2,  # TODO: Revisit with deposit
        "_default_preview": "previewer one",
        "_internal_notes": [{
            "user": "inveniouser",
            "note": "RDM record",
            "timestamp": "2020-02-01"
        }],
        "_owners": [1],  # TODO: Revisit with deposit
        "access_right": "open",
        "embargo_date": "2022-12-31",
        "contact": "info@inveniosoftware.org",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        },
        "identifiers": {
            "DOI": "10.5281/zenodo.9999999",
            "arXiv": "9999.99999"
        },
        "creators": [
            {
                "name": "Julio Cesar",
                "type": "Personal",
                "given_name": "Julio",
                "family_name": "Cesar",
                "identifiers": {
                    "Orcid": "9999-9999-9999-9999"
                },
                "affiliations": [{
                    "name": "Entity One",
                    "identifier": "entity-one",
                    "scheme": "entity-id-scheme"
                }]
            },
            {
                "name": "California Digital Library",
                "type": "Organizational",
                "identifiers": {
                    "ROR": "03yrm5c26",
                }
            }
        ],
        "titles": [{
            "title": "A Romans story",
            "type": "Other",
            "lang": "eng"
        }],
        "publication_date": "2020-06-01",
        "subjects": [{
            "subject": "Romans",
            "identifier": "subj-1",
            "scheme": "no-scheme"
        }],
        "contributors": [{
            "name": "Maximo Decimo Meridio",
            "type": "Personal",
            "given_name": "Maximo",
            "family_name": "Decimo Meridio",
            "identifiers": {
                "Orcid": "9999-9999-9999-9998",
            },
            "affiliations": [{
                "name": "Entity One",
                "identifier": "entity-one",
                "scheme": "entity-id-scheme"
            }],
            "role": "RightsHolder"
        }],
        "dates": [{
            "start": "2020-06-01",
            "end":  "2021-06-01",
            "description": "Random test date",
            "type": "Other"
        }],
        "language": "eng",
        "related_identifiers": [{
            "identifier": "10.5281/zenodo.9999988",
            "scheme": "DOI",
            "relation_type": "Requires",
            "resource_type": {
                "type": "image",
                "subtype": "image-photo"
            }
        }],
        "version": "v0.0.1",
        "licenses": [{
            "license": "Berkeley Software Distribution 3",
            "uri": "https://opensource.org/licenses/BSD-3-Clause",
            "identifier": "BSD-3",
            "scheme": "BSD-3",
        }],
        "descriptions": [{
            "description": "A story on how Julio Cesar relates to Gladiator.",
            "type": "Abstract",
            "lang": "eng"
        }],
        "locations": [{
            "point": {
                "lat": 41.902604,
                "lon": 12.496189
            },
            "place": "Rome",
            "description": "Rome, from Romans"
        }],
        "references": [{
            "reference_string": "Reference to something et al.",
            "identifier": "9999.99988",
            "scheme": "GRID"
        }]
    }


@pytest.fixture(scope='function')
def full_record(full_input_record):
    """
    Dictionary with all fields to create a record.

    It fills in the post_loaded fields.
    """
    record = deepcopy(full_input_record)
    record['_publication_date_search'] = '2020-06-01'
    return record


@pytest.fixture(scope='function')
def minimal_input_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "_access": {
            "metadata_restricted": False,
            "files_restricted": False
        },
        "_owners": [1],
        "_created_by": 1,
        "access_right": "open",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        },
        # Technically not required
        "creators": [],
        "titles": [{
            "title": "A Romans story",
            "type": "Other",
            "lang": "eng"
        }]
    }


@pytest.fixture(scope='function')
def minimal_record(minimal_input_record):
    """
    Dictionary with the minimum required fields to create a record.

    It fills in the missing and post_loaded fields.
    """
    record = deepcopy(minimal_input_record)
    record['publication_date'] = date.today().isoformat()
    record['_publication_date_search'] = date.today().isoformat()
    return record
