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

import click
from edtf.parser.grammar import level0Expression
from faker import Faker
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import \
    current_service as current_vocabularies_service

from .fixtures import FixturesEngine
from .proxies import current_rdm_records
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
            "record": "public",
            "files": "public",
        },
        # PIDS-FIXME: re-enable
        # "pids":  {
        #     "doi": {
        #         "identifier": "10.5281/zenodo.1234",
        #         "provider": "datacite",
        #         "client": "zenodo"
        #     }
        # },
        "metadata": {
            "resource_type": fake_resource_type(),
            "creators": [{
                "person_or_org": {
                    "family_name": fake.last_name(),
                    "given_name": fake.first_name(),
                    "type": "personal",
                    "identifiers": [{
                        "scheme": "orcid",
                        "identifier": "0000-0002-1825-0097",
                    }],
                },
                "affiliations": [{
                    "name": fake.company(),
                    "identifiers": [{
                        "scheme": "ror",
                        "identifier": "03yrm5c26",
                    }]
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
                "identifier": "03yrm5c26",
                "scheme": "ror"
            }, {
                "subject": fake.word(),
                "identifier": "03yrm5c26",
                "scheme": "ror"
            }],
            "contributors": [{
                "person_or_org": {
                    "family_name": fake.last_name(),
                    "given_name": fake.first_name(),
                    "type": "personal",
                },
                "affiliations": [{
                    "name": fake.company(),
                    "identifiers": [{
                        "scheme": "ror",
                        "identifier": "03yrm5c26",
                    }]
                }],
                "role": "rightsholder"
            } for i in range(3)],
            # "dates": [{
            #     # No end date to avoid computations based on start
            #     "date": fake.date(pattern='%Y-%m-%d'),
            #     "description": "Random test date",
            #     "type": "other"
            # }],
            # TODO: Add when we have PIDs for languages vocabulary
            # "languages": [{"id": "eng"}],
            # "related_identifiers": [{
            #     "identifier": "10.9999/rdm.9999988",
            #     "scheme": "doi",
            #     "relation_type": "requires",
            #     "resource_type": fake_resource_type()
            # }],
            "sizes": [
                "11 pages"
            ],
            "formats": [
                "application/pdf"
            ],
            "version": "v0.0.1",
            # "rights": [{
            #     "rights": "Berkeley Software Distribution 3",
            #     "uri": "https://opensource.org/licenses/BSD-3-Clause",
            #     "identifier": "03yrm5c26",
            #     "scheme": "ror",
            # }],
            "description": fake.text(max_nb_chars=3000),
            "additional_descriptions": [{
                "description": fake.text(max_nb_chars=200),
                "type": "methods",
                "lang": "eng"
            } for i in range(2)],
            "funding": [{
                "funder": {
                    "name": "European Commission",
                    "identifier": "03yrm5c26",
                    "scheme": "ror"
                },
                "award": {
                    "title": "OpenAIRE",
                    "number": "246686",
                    "identifier": "0000-0002-1825-0097",
                    "scheme": "orcid"
                }
            }],
            # "locations": [{
            #     'geometry': {
            #         'type': 'Point',
            #         'coordinates': [
            #             float(fake.latitude()), float(fake.longitude())
            #         ]
            #     },
            #     "place": fake.location_on_land()[2],
            #     "description": "Random place on land...",
            #     'identifiers': [{
            #         'scheme': 'ror',
            #         'identifier': '03yrm5c26',
            #     }, {
            #         'scheme': 'orcid',
            #         'identifier': '0000-0002-1825-0097',
            #     }]
            # }, {
            #     'geometry': {
            #         'type': 'MultiPoint',
            #         'coordinates': [
            #             [float(fake.latitude()), float(fake.longitude())],
            #             [float(fake.latitude()), float(fake.longitude())]
            #         ]
            #     },
            #     "place": fake.location_on_land()[2],
            # }
            # ],
            "references": [{
                "reference": "Reference to something et al.",
                "identifier": "0000000114559647",
                "scheme": "isni"
            }],
            "identifiers": [{
                "identifier": "ark:/123/456",
                "scheme": "ark"
            }],
        }
    }

    service = current_rdm_records.records_service
    draft_files_service = service.draft_files

    draft = service.create(data=data_to_use, identity=system_identity)
    draft_files_service.update_files_options(
        id_=draft.id, identity=system_identity, data={'enabled': False})
    record = service.publish(id_=draft.id, identity=system_identity)

    return record


@click.group()
def rdm_records():
    """InvenioRDM records commands."""
    pass


@rdm_records.command('demo')
@with_appcontext
def demo():
    """Create 100 fake records for demo purposes."""
    click.secho('Creating demo records...', fg='green')

    for _ in range(100):
        create_fake_record()

    click.secho('Created records!', fg='green')


@rdm_records.command('fixtures')
@with_appcontext
def create_fixtures():
    """Create the fixtures required for record creation."""
    click.secho('Creating required fixtures...', fg='green')

    FixturesEngine(system_identity).run()

    click.secho('Created required fixtures!', fg='green')


@rdm_records.command("rebuild-index")
@with_appcontext
def rebuild_index():
    """Reindex all drafts, records and vocabularies."""
    click.secho("Reindexing records and drafts...", fg="green")

    rec_service = current_rdm_records.records_service
    rec_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing vocabularies...", fg="green")

    vocab_service = current_vocabularies_service
    vocab_service.rebuild_index(identity=system_identity)

    click.secho("Reindexed everything!", fg="green")
