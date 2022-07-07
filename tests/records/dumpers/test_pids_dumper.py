# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from invenio_records.dumpers import SearchDumper

from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.api import RDMParent
from invenio_rdm_records.records.dumpers import PIDsDumperExt


def test_esdumper_with_externalpidsext(app, db, minimal_record, location):
    # Create a simple extension that adds a computed field.

    dumper = SearchDumper(extensions=[PIDsDumperExt()])

    minimal_record["pids"] = {
        "doi": {
            "identifier": "10.5281/zenodo.1234",
            "provider": "datacite",
            "client": "zenodo",
        },
        "handle": {
            "identifier": "9.12314",
            "provider": "cern-handle",
            "client": "zenodo",
        },
    }

    # Create the record
    record = RDMRecord.create(minimal_record, parent=RDMParent.create({}))
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    dumped_pids = dump["pids"]
    for dumped_pid in dumped_pids:
        pid_attrs = dumped_pid.keys()
        assert "scheme" in pid_attrs
        assert "identifier" in pid_attrs
        assert "provider" in pid_attrs
        assert "client" in pid_attrs

    # Load it
    new_record = RDMRecord.loads(dump, loader=dumper)
    assert minimal_record["pids"] == new_record["pids"]
