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


def test_ui_serializer(app, full_record_ui):
    """Test UI serializer."""
    # full_record_ui = full_record
    full_record_ui['access']['status'] = 'embargoed'
    expected_data = {
        'access_status': {
            'description_l10n': 'The files will be made publicly available on '
                                'January 1, 2131.',
            'icon': 'outline clock',
            'id': 'embargoed',
            'title_l10n': 'Embargoed',
            'embargo_date_l10n': 'January 1, 2131',
            'message_class': 'warning',
        },
        'contributors': {
            'affiliations': [[1, 'CERN']],
            'contributors': [{
                'affiliations': [[1, 'CERN']],
                'family_name': 'Nielsen',
                'given_name': 'Lars Holm',
                'identifiers': {
                    'orcid': '0000-0001-8135-3489'
                    },
                'name': 'Nielsen, Lars Holm',
                'role': 'other',
                'type': 'personal'
            }]
        },
        'creators': {
            'affiliations': [[1, 'CERN']],
            'creators': [{
                'affiliations': [[1, 'CERN']],
                'family_name': 'Nielsen',
                'given_name': 'Lars Holm',
                'identifiers': {
                    'orcid': '0000-0001-8135-3489'},
                'name': 'Nielsen, Lars Holm',
                'type': 'personal'
            }]
        },
        'publication_date_l10n_long': 'January 2018 – September 2020',
        'publication_date_l10n_medium': 'Jan 2018 – Sep 2020',
        'resource_type': 'Journal article',
        'languages': [
            {'id': 'da', 'title_l10n': "Danish"},
            {'id': 'en', 'title_l10n': "English"}
        ],
        'description_stripped': 'Test',
        'version': 'v1.0',
    }

    with app.app_context():
        serialized_record = UIJSONSerializer().serialize_object_to_dict(
            full_record_ui)
    assert serialized_record['ui'] == expected_data
    serialized_records = UIJSONSerializer().serialize_object_list(
        {"hits": {"hits": [full_record_ui]}})
    assert json.loads(serialized_records)['hits']['hits'][0]['ui'] == \
        expected_data
