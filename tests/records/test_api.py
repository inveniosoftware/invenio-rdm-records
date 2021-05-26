# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record."""

from invenio_rdm_records.records.api import RDMDraft


def test_idempotence_dumps_loads(running_app, minimal_record):
    """Idempotence of dumps and loads."""
    # This simple test asserts a key property of the dumps and loads methods.
    # A record that's dumped, must when loaded produce exactly the same dict
    # representation of a record. This key property ensures that it doesn't
    # matter if a record is loaded from primary storage (database) or secondary
    # storages (index, files, ...). A record when loaded behaves like a normal
    # record.

    # If this tests fails likely either a system fields pre/post_dump/load
    # method is having an issue, or it might be an Elasticsearch dumper.

    # DO NOT CHANGE TEST UNLESS YOU ABSOLUTELY KNOW WHAT YOU'RE DOING
    draft = RDMDraft.create(minimal_record)
    loaded_draft = RDMDraft.loads(draft.dumps())
    assert dict(draft) == dict(loaded_draft)
