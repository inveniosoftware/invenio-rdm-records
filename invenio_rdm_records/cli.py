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
from flask_principal import Identity
from invenio_access import any_user
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore import current_pidstore
from invenio_records_files.api import Record
from invenio_search import current_search

from .services import BibliographicRecordService
from .vocabularies import Vocabularies


def fake_resource_type():
    """Generates a fake resource_type."""
    vocabulary = Vocabularies.get_vocabulary('resource_type')
    _type, subtype = random.choice(list(vocabulary.data.keys()))
    resource_type = {
        "type": _type
    }
    if subtype:
        resource_type.update({
            "subtype": subtype
        })
    return resource_type


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
        "access": {
            "metadata": False,
            "files": False,
            "owned_by": [1],
            "access_right": "open",
            "embargo_date":
                fake.future_date(end_date='+1y').strftime("%Y-%m-%d")
        },
        "metadata": {
            "resource_type": fake_resource_type(),
            "creators": [{
                "name": fake.name(),
                "type": "personal",
                "identifiers": {
                    "orcid": "0000-0002-1825-0097",
                },
                "affiliations": [{
                    "name": fake.company(),
                    "identifiers": {
                        "ror": "03yrm5c26"
                    }
                }]
            } for i in range(4)],
            "title": fake.company() + "'s gallery",
            "additional_titles": [{
                "title": "a research data management platform",
                "type": "subtitle",
                "lang": "eng"
            }, {
                "title": fake.company() + "'s gallery",
                "type": "alternativetitle",
                "lang": "eng"
            }],
            "publisher": "InvenioRDM",
            "publication_date": fake_edtf_level_0(),
            "subjects": [{
                "subject": fake.word(),
                "identifier": "subj-1",
                "scheme": "no-scheme"
            }, {
                "subject": fake.word(),
                "identifier": "subj-1",
                "scheme": "no-scheme"
            }],
            "contributors": [{
                "name": fake.name(),
                "type": "personal",
                "affiliations": [{
                    "name": fake.company(),
                    "identifiers": {
                        "ror": "03yrm5c26"
                    }
                }],
                "role": "rightsholder"
            } for i in range(3)],
            "dates": [{
                # No end date to avoid computations based on start
                "date": fake.date(pattern='%Y-%m-%d'),
                "description": "Random test date",
                "type": "other"
            }],
            "languages": ["eng"],
            "related_identifiers": [{
                "identifier": "10.9999/rdm.9999988",
                "scheme": "doi",
                "relation_type": "requires",
                "resource_type": fake_resource_type()
            }],
            "sizes": [
                "11 pages"
            ],
            "formats": [
                "application/pdf"
            ],
            "version": "v0.0.1",
            "rights": [{
                "rights": "Berkeley Software Distribution 3",
                "uri": "https://opensource.org/licenses/BSD-3-Clause",
                "identifier": "BSD-3",
                "scheme": "BSD-3",
            }],
            "description": fake.text(max_nb_chars=3000),
            "additional_descriptions": [{
                "description": fake.text(max_nb_chars=200),
                "type": "methods",
                "lang": "eng"
            } for i in range(2)],
            "funding": [{
                "funder": {
                    "name": "European Commission",
                    "identifier": "1234",
                    "scheme": "ror"
                },
                "award": {
                    "title": "OpenAIRE",
                    "number": "246686",
                    "identifier": ".../246686",
                    "scheme": "openaire"
                }
            }],
            "locations": [{
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        float(fake.latitude()), float(fake.longitude())
                    ]
                },
                "place": fake.location_on_land()[2],
                "description": "Random place on land...",
                'identifiers': {
                    'wikidata': '12345abcde',
                    'geonames': '12345abcde'
                }
            }, {
                'geometry': {
                    'type': 'MultiPoint',
                    'coordinates': [
                        [float(fake.latitude()), float(fake.longitude())],
                        [float(fake.latitude()), float(fake.longitude())]
                    ]
                },
                "place": fake.location_on_land()[2],
            }
            ],
            "references": [{
                "reference": "Reference to something et al.",
                "identifier": "9999.99988",
                "scheme": "grid"
            }]
        }
    }

    # identity providing `any_user` system role
    identity = Identity(1)
    identity.provides.add(any_user)

    service = BibliographicRecordService()
    draft = service.create(data=data_to_use, identity=identity)
    record = service.publish(id_=draft.id, identity=identity)

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
