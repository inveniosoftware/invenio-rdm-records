# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
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
from invenio_access.models import ActionRoles
from invenio_access.permissions import any_user, authenticated_user, \
    superuser_access, system_process
from invenio_accounts.models import Role
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


@pytest.fixture(scope="function")
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture(scope="function")
def anyuser_identity():
    """System identity."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity


@pytest.fixture(scope="function")
def authenticated_identity():
    """Authenticated identity fixture."""
    identity = Identity(1)
    identity.provides.add(authenticated_user)
    return identity


@pytest.fixture(scope="function")
def superuser_identity(superuser_role_need):
    """Superuser identity fixture."""
    identity = Identity(1)
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture(scope="function")
def system_process_identity():
    """Superuser identity fixture."""
    identity = Identity(1)
    identity.provides.add(system_process)
    return identity
