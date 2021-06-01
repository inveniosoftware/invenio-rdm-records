# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the CLI."""

from pathlib import Path

from invenio_rdm_records.fixtures.demo import create_fake_record
from invenio_rdm_records.fixtures.tasks import create_demo_record


def test_fake_demo_record_creation(app, location, db, es_clear, vocabularies):
    """Assert that demo record creation works without failing."""
    vocabularies.load_vocabulary(
        'resource_types',
        {
            "pid-type": "rsrct",
            "data-file": (
                Path(__file__).parent / "data/vocabularies/resource_types.yaml"
            )
        },
        delay=False
    )
    vocabularies.load_vocabulary(
        'languages',
        {
            "pid-type": "lng",
            "data-file": (
                Path(__file__).parent / "data/vocabularies/languages.yaml"
            )
        },
        delay=False
    )

    create_demo_record(create_fake_record())
