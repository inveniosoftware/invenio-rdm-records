# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Command-line tools for demo module."""
import datetime
import random
import uuid

import click
from edtf.parser.grammar import level0Expression
from faker import Faker
from flask.cli import with_appcontext
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore import current_pidstore
from invenio_records_files.api import Record
from invenio_search import current_search

from .vocabularies import Vocabularies


def fake_resource_type():
    """Generates a fake resource_type."""
    vocabulary = Vocabularies.get_vocabulary('resource_type')
    _type, subtype = random.choice(list(vocabulary.data.keys()))
    return {
        "type": _type,
        "subtype": subtype
    }


def fake_edtf_level_0():
    """Generates a fake publication_date string."""
    def fake_date(end_date=None):
        fake = Faker()
        date_pattern = ['%Y', '%m', '%d']
        # make it less and less likely to get less and less parts of the date

        if random.choice([True, False]):
            date_pattern.pop()
            if random.choice([True, False]):
                date_pattern.pop()

        return fake.date("-".join(date_pattern), end_datetime=end_date)

    f_date = fake_date()

    # if interval
    if random.choice([True, False]):
        # get f_date as date object
        parser = level0Expression("level0")
        parsed_date = parser.parseString(f_date)[0]
        date_tuple = parsed_date.lower_strict()[:3]
        f_date_object = datetime.date(*date_tuple)

        interval_start = fake_date(end_date=f_date_object)

        return "/".join([interval_start, f_date])

    return f_date


def create_fake_record():
    """Create records for demo purposes."""
    fake = Faker()
    data_to_use = {
        "_access": {
            "metadata_restricted": False,
            "files_restricted": False
        },
        "_created_by": 2,
        "_default_preview": "previewer one",
        "_internal_notes": [{
            "user": "inveniouser",
            "note": "RDM record",
            "timestamp": fake.iso8601(tzinfo=None, end_datetime=None),
        }],
        "_owners": [1],
        "access_right": "open",
        "embargo_date": fake.iso8601(tzinfo=None, end_datetime=None),
        "contact": "info@inveniosoftware.org",
        "resource_type": fake_resource_type(),
        "identifiers": {
            "DOI": "10.9999/rdm.9999999",
            "arXiv": "9999.99999",
        },
        "creators": [{
            "name": fake.name(),
            "type": "Personal",
            "identifiers": {
                "Orcid": "9999-9999-9999-9999",
            },
            "affiliations": [{
                "name": fake.company(),
                "identifier": "entity-one",
                "scheme": "entity-id-scheme"
            }]
        }],
        "titles": [{
            "title": fake.company() + "'s gallery",
            "type": "Other",
            "lang": "eng"
        }],
        "publication_date": fake_edtf_level_0(),
        "subjects": [{
            "subject": "Romans",
            "identifier": "subj-1",
            "scheme": "no-scheme"
        }],
        "contributors": [{
            "name": fake.name(),
            "type": "Personal",
            "identifiers": {
                "Orcid": "9999-9999-9999-9998",
            },
            "affiliations": [{
                "name": fake.company(),
                "identifier": "entity-one",
                "scheme": "entity-id-scheme"
            }],
            "role": "RightsHolder"
        }],
        "dates": [{
            # No end date to avoid computations based on start
            "start": fake.iso8601(tzinfo=None, end_datetime=None),
            "description": "Random test date",
            "type": "Other"
        }],
        "language": "eng",
        "related_identifiers": [{
            "identifier": "10.9999/rdm.9999988",
            "scheme": "DOI",
            "relation_type": "Requires",
            "resource_type": fake_resource_type()
        }],
        "version": "v0.0.1",
        "licenses": [{
            "license": "Berkeley Software Distribution 3",
            "uri": "https://opensource.org/licenses/BSD-3-Clause",
            "identifier": "BSD-3",
            "scheme": "BSD-3",
        }],
        "descriptions": [{
            "description": fake.text(max_nb_chars=3000),
            "type": "Abstract",
            "lang": "eng"
        }],
        "locations": [{
            "point": {
                "lat": str(fake.latitude()),
                "lon": str(fake.longitude())
            },
            "place": fake.location_on_land()[2],
            "description": "Random place on land for random coordinates..."
        }],
        "references": [{
            "reference_string": "Reference to something et al.",
            "identifier": "9999.99988",
            "scheme": "GRID"
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
