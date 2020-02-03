# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
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
        "_visibility": True,
        "_visibility_files": True,
        "_owners": [1],
        "_created_by": 2,
        "_default_preview": "previewer one",
        "_internal_notes": [{
            "user": "inveniouser",
            "note": "RDM record",
            "timestamp": fake.iso8601(tzinfo=None, end_datetime=None),
        }],
        "embargo_date": fake.iso8601(tzinfo=None, end_datetime=None),
        "contact": "info@inveniosoftware.org",
        "community": {
            "primary": "Maincom",
            "secondary": ["Subcom One", "Subcom Two"]
        },
        "resource_type": {
            "type": "image",
            "subtype": "photo"
        },
        "identifiers": [{
            "identifier": "10.5281/zenodo.9999999",
            "scheme": "DOI"
        }, {
            "identifier": "9999.99999",
            "scheme": "arXiv"
        }],
        "creators": [{
            "name": fake.name(),
            "type": "Personal",
            "identifiers": [{
                "identifier": "9999-9999-9999-9999",
                "scheme": "Orcid"
            }],
            "affiliations": [{
                "name": fake.company(),
                "identifier": "entity-one",
                "scheme": "entity-id-scheme"
            }]
        }],
        "contributors": [{
            "name": fake.name(),
            "type": "Personal",
            "identifiers": [{
                "identifier": "9999-9999-9999-9998",
                "scheme": "Orcid"
            }],
            "affiliations": [{
                "name": fake.company(),
                "identifier": "entity-one",
                "scheme": "entity-id-scheme"
            }],
            "role": "RightsHolder"
        }],
        "titles": [{
            "title": fake.company() + "'s gallery",
            "type": "Other",
            "lang": "eng"
        }],
        "descriptions": [{
            "description": fake.bs(),
            "type": "Abstract",
            "lang": "eng"
        }],
        "publication_date": fake.iso8601(tzinfo=None, end_datetime=None),
        "licenses": [{
            "license": "Copyright Maximo Decimo Meridio 2020. Long statement",
            "uri": "https://opensource.org/licenses/BSD-3-Clause",
            "identifier": "BSD-3",
            "scheme": "BSD-3",
        }],
        "subjects": [{
            "subject": "Romans",
            "identifier": "subj-1",
            "scheme": "no-scheme"
        }],
        "language": "eng",
        "dates": [{
            # No end date to avoid computations based on start
            "start": fake.iso8601(tzinfo=None, end_datetime=None),
            "description": "Random test date",
            "type": "Other"
        }],
        "version": "v0.0.1",
        "related_identifiers": [{
            "identifier": "10.5281/zenodo.9999988",
            "scheme": "DOI",
            "relation_type": "Requires",
            "resource_type": {
                "type": "image",
                "subtype": "photo"
            }
        }],
        "references": [{
            "reference_string": "Reference to something et al.",
            "identifier": "9999.99988",
            "scheme": "GRID"
        }],
        "locations": [{
            "point": {
                "lat": 41.902604,
                "lon": 12.496189
            },
            "place": "Rome",
            "description": "Rome, from Romans"
        }]
    }

    # Create and index record
    rec_uuid = uuid.uuid4()
    current_pidstore.minters['recid_v2'](rec_uuid, data_to_use)
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
