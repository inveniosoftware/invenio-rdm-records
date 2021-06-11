# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Fake demo records."""

import datetime
import json
import random
from pathlib import Path

from edtf.parser.grammar import level0Expression
from faker import Faker
from invenio_access.permissions import system_identity

from invenio_rdm_records.fixtures import VocabulariesFixture


class CachedVocabularies:
    """Singleton to store some vocabulary entries.

    This is needed because otherwise expensive random picking would have to be
    done for every call to create_fake_record().

    Even then, we shouldn't load all vocabularies' entries in memory
    (at least not big ones).
    """

    _resource_type_ids = []
    _subject_ids = []

    @classmethod
    def _read_vocabulary(cls, vocabulary):
        dir_ = Path(__file__).parent

        return VocabulariesFixture(
            system_identity,
            [Path("./app_data"), dir_ / "data"],
            "vocabularies.yaml",
        ).get_records_by_vocabulary(vocabulary)

    @classmethod
    def fake_resource_type(cls):
        """Generate a random resource_type."""
        if not cls._resource_type_ids:
            cls._resource_type_ids = []

            dir_ = Path(__file__).parent

            res_types = cls._read_vocabulary("resource_types")

            for res in res_types:
                cls._resource_type_ids.append(res["id"])

        random_id = random.choice(cls._resource_type_ids)
        return {"id": random_id}

    @classmethod
    def fake_subjects(cls):
        """Generate random subjects."""
        if not cls._subject_ids:
            subjects = cls._read_vocabulary("subjects")

            for subj in subjects:
                cls._subject_ids.append(subj["id"])

        if not cls._subject_ids:
            return []

        n = random.choice([0, 1, 2])
        random_ids = random.sample(cls._subject_ids, n)
        return [{"id": i} for i in random_ids]

    @classmethod
    def fake_language(cls):
        """Generate a random resource_type."""
        random_id = random.choice(["eng", "aah", "aag"])
        return {"id": random_id}


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
        "files":  {
            "enabled": False,
        },
        "pids": {
        },
        "metadata": {
            "resource_type": CachedVocabularies.fake_resource_type(),
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
            "subjects": CachedVocabularies.fake_subjects(),
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
            "languages": [CachedVocabularies.fake_language()],
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

    return json.loads(json.dumps(data_to_use))
