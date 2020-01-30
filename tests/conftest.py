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
def full_record():
    """
    Dictionary to create a record with all the fields.

    The following attributes are injected by the de/serialization:
    - bucket
    - recid
    - conceptrecid
    - files (when files are added to the record)
    """
    return {
        "_visibility": True,
        "_visibility_files": True,
        "_owners": [1],
        "_created_by": 2,
        "_default_preview": "previewer one",
        "_internal_notes": [{
            "user": "inveniouser",
            "note": "RDM record",
            "timestamp": "2020-02-01"
        }],
        "embargo_date": "2022-12-31",
        "contact": "info@inveniosoftware.org",
        "community": {
            "primary": "Maincom",
            "secondary": ["Subcom One", "Subcom Two"]
        },
        "resource_type": {
            "type": "image",
            "subtype": "photo"
        },
        "identifiers": [{
            "identifier": "10.5281/zenodo.9999999",
            "scheme": "DOI"
        }, {
            "identifier": "9999.99999",
            "scheme": "arXiv"
        }],
        "creators": [{
            "name": "Julio Cesar",
            "type": "Personal",
            "given_name": "Julio",
            "family_name": "Cesar",
            "identifiers": [{
                "identifier": "9999-9999-9999-9999",
                "scheme": "Orcid"
            }],
            "affiliations": [{
                "name": "Entity One",
                "identifier": "entity-one",
                "scheme": "entity-id-scheme"
            }]
        }],
        "contributors": [{
            "name": "Maximo Decimo Meridio",
            "type": "Personal",
            "given_name": "Maximo",
            "family_name": "Decimo Meridio",
            "identifiers": [{
                "identifier": "9999-9999-9999-9998",
                "scheme": "Orcid"
            }],
            "affiliations": [{
                "name": "Entity One",
                "identifier": "entity-one",
                "scheme": "entity-id-scheme"
            }],
            "role": "RightsHolder"
        }],
        "titles": [{
            "title": "A Romans story",
            "type": "Other",
            "lang": "eng"
        }],
        "descriptions": [{
            "description": "A story on how Julio Cesar relates to Gladiator.",
            "type": "Abstract",
            "lang": "eng"
        }],
        "publication_date": "2020-06-01",
        "licenses": [{
            "license": "Copyright Maximo Decimo Meridio 2020. Long statement",
            "uri": "https://opensource.org/licenses/BSD-3-Clause",
            "identifier": "BSD-3",
            "scheme": "BSD-3",
        }],
        "subjects": [{
            "subject": "Romans",
            "identifier": "subj-1",
            "scheme": "no-scheme"
        }],
        "language": "eng",
        "dates": [{
            "start": "2020-06-01",
            "end":  "2021-06-01",
            "description": "Random test date",
            "type": "Other"
        }],
        "version": "v0.0.1",
        "related_identifiers": [{
            "identifier": "10.5281/zenodo.9999988",
            "scheme": "DOI",
            "relation_type": "Requires",
            "resource_type": {
                "type": "image",
                "subtype": "photo"
            }
        }],
        "references": [{
            "reference_string": "Reference to something et al.",
            "identifier": "9999.99988",
            "scheme": "GRID"
        }],
        "locations": [{
            "point": {
                "lat": 41.902604,
                "lon": 12.496189
            },
            "place": "Rome",
            "description": "Rome, from Romans"
        }]
    }


@pytest.fixture(scope='function')
def minimal_record():
    """
    Dictionary with the minimum requried fields to create a record.

    The following attributes are injected by the de/serialization:
    - recid
    """
    return {
        "_visibility": True,
        "_owners": [1],
    }
