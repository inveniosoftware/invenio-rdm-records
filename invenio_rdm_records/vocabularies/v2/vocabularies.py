# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Vocabulary initialization."""

import csv
from os.path import dirname, join

from flask_principal import Identity
from invenio_access import any_user
from invenio_db import db
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services.service import VocabulariesService


class VocabulariesV2:
    """Vocabularies source data for invenio-vocabularies."""

    this_dir = dirname(__file__)
    vocabularies = {
        'languages': {
            'path': join(this_dir, 'languages.csv'),
        }
    }

    @classmethod
    def _load_data(cls, path):
        with open(path) as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            dicts = [row for row in reader]
            return dicts

    @classmethod
    def _create(cls, vocabulary_type, row, service, identity):
        i18n = ['title', 'description']  # Attributes with i18n support
        other = ['icon']  # Other top-level attributes

        default_language = 'en'  # Static (dependent on the files)

        metadata = {
            'title': {},
            'description': {},
            'props': {}
        }

        for attribute in row:
            value = row[attribute]
            if attribute in i18n:
                metadata[attribute][default_language] = value
            elif any(map(lambda s: value.startswith(s + '_'), i18n)):
                [prefix_attr, language] = attribute.split('_', 1)
                metadata[prefix_attr][language] = value
            elif attribute in other:
                metadata[attribute] = value
            else:
                metadata['props'][attribute] = value

        # Create and return record
        return service.create(
            identity=identity,
            data={
                'metadata': metadata,
                'vocabulary_type_id': vocabulary_type.id,
            },
        )

    @classmethod
    def create_all(cls):
        """Create the vocabulary item record from the source files."""
        identity = Identity(1)
        identity.provides.add(any_user)
        service = VocabulariesService()

        for vocabulary_type in cls.vocabularies:
            vocabulary = cls.vocabularies[vocabulary_type]

            # Load data
            rows = cls._load_data(vocabulary['path'])

            # Create vocabulary type
            vocabulary_type = VocabularyType(name=vocabulary_type)
            db.session.add(vocabulary_type)
            db.session.commit()

            for row in rows:
                cls._create(vocabulary_type, row, service, identity)
