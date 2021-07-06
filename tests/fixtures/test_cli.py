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
    vocabularies_meta = [
        (
            'resourcetypes',
            "rsrct",
            Path(__file__).parent / "data/vocabularies/resource_types.yaml"
        ),
        (
            'languages',
            "lng",
            Path(__file__).parent / "data/vocabularies/languages.yaml"
        ),
        (
            'titletypes',
            "ttyp",
            Path(__file__).parent / "data/vocabularies/title_types.yaml"
        ),
        (
            'creatorsroles',
            "crr",
            Path(__file__).parent / "data/vocabularies/roles.yaml"
        ),
        (
            'contributorsroles',
            "cor",
            Path(__file__).parent / "data/vocabularies/roles.yaml"
        ),
        (
            'descriptiontypes',
            "dty",
            Path(__file__).parent / "data/vocabularies/description_types.yaml"
        ),
        (
            'relationtypes',
            "rlt",
            Path(__file__).parent / "data/vocabularies/relation_types.yaml"
        ),
    ]
    for id_, pid_type, filepath in vocabularies_meta:
        vocabularies.create_vocabulary_type(
            id_,
            {
                "pid-type": pid_type,
                "data-file": filepath
            },
        )
        vocabularies.load_datafile(id_, filepath, delay=False)

    create_demo_record(create_fake_record())
