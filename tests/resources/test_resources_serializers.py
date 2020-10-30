# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import json

from invenio_rdm_records.resources.serializers import UIJSONSerializer


def test_ui_serializer(app, minimal_record):
    """Test UI serializer."""
    expected_data = {
        'access_right': {
            'category': 'open',
            'icon': 'lock open',
            'title': 'Open Access'
        },
        'resource_type': {'title': 'Image / Photo'},
        'publication_date_l10n': 'Jun 1, 2020'
    }
    with app.app_context():
        serialized_record = UIJSONSerializer().serialize_object(minimal_record)
    assert json.loads(serialized_record)['ui'] == expected_data
    serialized_records = UIJSONSerializer().serialize_object_list(
        {"hits": {"hits": [minimal_record]}})
    assert json.loads(serialized_records)['hits']['hits'][0]['ui'] == \
        expected_data
