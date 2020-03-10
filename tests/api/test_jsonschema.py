# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test jsonschema validation."""

from invenio_jsonschemas import current_jsonschemas
from invenio_records.api import Record


def test_metadata_extensions(appctx, minimal_record):
    data = {
        '$schema': (
            current_jsonschemas.path_to_url('records/record-v1.0.0.json')
        ),
        'extensions': {
            'dwc:family': 'Felidae',
            'dwc:behavior': 'Plays with yarn, sleeps in cardboard box.',
            'nubiomed:number_in_sequence': 3,
            'nubiomed:scientific_sequence': [1, 1, 2, 3, 5, 8],
            'nubiomed:original_presentation_date': '2019-02-14',
            'nubiomed:right_or_wrong': True
        }
    }
    minimal_record.update(data)
    record = Record(minimal_record)

    record.validate()
