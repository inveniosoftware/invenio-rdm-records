# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Command-line tools for demo module."""

import uuid

import click
from faker import Faker
from flask.cli import with_appcontext
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore import current_pidstore
from invenio_records_files.api import Record
from invenio_search import current_search


def create_fake_record():
    """Create records for demo purposes."""
    fake = Faker()
    data_to_use = {
        "_access": {
            "metadata_restricted": False,
            "files_restricted": False
        },
        "access_right": "open",
        "contributors": [{"name": fake.name()}],
        "description": fake.bs(),
        "owners": [1],
        "publication_date": fake.iso8601(tzinfo=None, end_datetime=None),
        "resource_type": {
            "subtype": "dataset",
            "type": "Dataset"
        },
        "title": fake.company() + "'s dataset"
    }

    # Create and index record
    rec_uuid = uuid.uuid4()
    current_pidstore.minters['recid'](rec_uuid, data_to_use)
    record = Record.create(data_to_use, id_=rec_uuid)
    RecordIndexer().index(record)

    # Flush to index and database
    current_search.flush_and_refresh(index='records')
    db.session.commit()

    return record


@click.group()
def rdm_records():
    """InvenioRDM records commands."""
    pass


@rdm_records.command('demo')
@with_appcontext
def demo():
    """Create 10 fake records for demo purposes."""
    click.secho('Creating demo records...', fg='blue')

    for _ in range(10):
        create_fake_record()

    click.secho('Created records!', fg='green')
