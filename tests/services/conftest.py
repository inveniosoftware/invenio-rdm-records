# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity
from invenio_access import any_user
from invenio_app.factory import create_api
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services.service import VocabulariesService

from invenio_rdm_records.vocabularies import Vocabularies


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope='function')
def vocabulary_clear(app):
    """Clears the Vocabulary singleton and pushes an application context.

    NOTE: app fixture pushes an application context
    """
    Vocabularies.clear()


@pytest.fixture()
def languages(db):
    """Languages fixture."""
    vocabulary_type = VocabularyType(name='languages')
    db.session.add(vocabulary_type)
    db.session.commit()

    identity = Identity(1)
    identity.provides.add(any_user)
    service = VocabulariesService()

    languages = {}

    for lang in (
        {"props": {"id": "en"}, "title": {"en": "English"}},
        {"props": {"id": "fr"}, "title": {"en": "French"}},
        {"props": {"id": "it"}, "title": {"en": "Italian"}},
    ):
        record = service.create(
            identity=identity,
            data={
                "metadata": lang,
                "vocabulary_type_id": vocabulary_type.id,
            },
        )
        languages[lang['props']['id']] = record

    return languages
