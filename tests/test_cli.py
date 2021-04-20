# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the CLI."""

from invenio_rdm_records.cli import create_fake_record


def test_fake_demo_record_creation(app, db, location, es_clear):
    record = create_fake_record()

    assert record.id
    assert "links" in record.data.keys()
    assert "files" in record.data.keys()
    assert "pids" in record.data.keys()
    assert "metadata" in record.data.keys()
