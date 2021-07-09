# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the CLI."""

from pathlib import Path

from invenio_access.permissions import system_identity

from invenio_rdm_records.fixtures.demo import create_fake_record
from invenio_rdm_records.fixtures.tasks import create_demo_record
from invenio_rdm_records.fixtures.vocabularies import VocabulariesFixture


def test_fake_demo_record_creation(app, location, db, es_clear):
    """Assert that demo record creation works without failing."""
    vocabularies = VocabulariesFixture(
        system_identity,
        Path(__file__).parent / "data/vocabularies.yaml",
        delay=False,
    )
    vocabularies.load()

    create_demo_record(create_fake_record())
