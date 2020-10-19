# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test serializers."""

import pytest
from invenio_pidstore.models import PersistentIdentifier
# TODO: use from invenio_records_files.api import Record
from invenio_records.api import Record
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow.fields import Bool

from invenio_rdm_records.services.schemas import MetadataSchema

# TODO: Figure out at what level to test... The higher the level, the more
#       layers we can cover, but the slower and more cumbersome to setup are
#       the tests. The lower the level, the less layers we cover, but the
#       the tests are quicker and typically easier to setup...
# We could test
# - at the MetadataSchemaV1.dump(ob) level OR
# - at the json_v1.transform_record(pid, record) level OR
# - at the client.get(url) level
#
# Long term, json_v1.transform_record(pid, record) seems a good compromise, but
# it still requires more setup/implemented code than we currently have.


@pytest.fixture(scope='module')
def app_config(app_config):
    """Override conftest.py's app_config
    """
    # Added custom configuration
    app_config['RDM_RECORDS_METADATA_NAMESPACES'] = {
        'dwc': {
            '@context': 'https://example.com/dwc/terms'
        },
        'nubiomed': {
            '@context': 'https://example.com/nubiomed/terms'
        }
    }

    app_config['RDM_RECORDS_METADATA_EXTENSIONS'] = {
        'dwc': {
            'family': {
                'elasticsearch': 'keyword',
                'marshmallow': SanitizedUnicode(required=True)
            },
            'behavior': {
                'elasticsearch': 'text',
                'marshmallow': SanitizedUnicode()
            }
        },
        'nubiomed': {
            'right_or_wrong': {
                'elasticsearch': 'boolean',
                'marshmallow': Bool()
            }
        }
    }

    return app_config


@pytest.mark.skip()
def test_extensions(db, minimal_record):
    """Test MetadataSchemaV1 dump() for 'extensions' field.

    Right now we are going for a schema level test which turns out to still be
    heavy, so something fundamental is lacking.
    """
    data = {
        'extensions': {
            'dwc': {
                'family': 'Felidae',
                'behavior': 'Plays with yarn, sleeps in cardboard box.',
            },
            'nubiomed': {
                'right_or_wrong': True
            }
        }
    }
    minimal_record.update(data)
    record = Record.create(minimal_record)
    db.session.commit()

    serialized_record = MetadataSchema().dump(record)  # returns MarshmalDict

    assert serialized_record['extensions'] == data['extensions']
