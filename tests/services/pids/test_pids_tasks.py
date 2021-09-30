# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""PID service tasks tests."""


from collections import namedtuple

import pytest
from invenio_pidstore.models import PIDStatus

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.pids.tasks import register_pid

RunningApp = namedtuple("RunningApp", [
    "app", "location", "superuser_identity", "resource_type_v",
    "subject_v", "languages_v", "title_type_v"
])


@pytest.fixture
def running_app(
    app, location, superuser_identity, resource_type_v, subject_v, languages_v,
        title_type_v):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.
    """
    return RunningApp(app, location, superuser_identity,
                      resource_type_v, subject_v, languages_v, title_type_v)


def test_publish_record_w_created_doi(
    running_app, es_clear, minimal_record, mocker
):
    """Publish a record with an already created datacite DOI."""
    def public_doi(self, metadata, url, doi):
        """Mock doi deletion."""
        pass

    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCiteRESTClient.public_doi", public_doi)

    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(draft.id, superuser_identity, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)

    assert pid.status == PIDStatus.NEW
    record = service.publish(draft.id, superuser_identity)
    assert pid.status == PIDStatus.RESERVED
    register_pid(pid_type="doi", pid_value=pid.pid_value,
                 recid=record["id"], provider_name="datacite")
    assert pid.status == PIDStatus.REGISTERED


def test_publish_record(running_app, es_clear, minimal_record, mocker):
    """No pid provided, creating one by default."""
    def public_doi(self, metadata, url, doi):
        """Mock doi deletion."""
        pass

    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCiteRESTClient.public_doi", public_doi)

    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(draft.id, superuser_identity)
    doi = record["pids"]["doi"]["identifier"]
    provider = service.pids.get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.RESERVED
    register_pid(pid_type="doi", pid_value=pid.pid_value,
                 recid=record["id"], provider_name="datacite")
    assert pid.status == PIDStatus.REGISTERED


def test_register_external_pid(running_app, es_clear, minimal_record):
    """Registering external pid."""
    minimal_record["pids"]["doi"] = {
        "identifier": "10.1234/dummy.12345",
        "provider": "external"
    }
    service = current_rdm_records.records_service
    superuser_identity = running_app.superuser_identity
    draft = service.create(superuser_identity, minimal_record)
    doi = draft["pids"]["doi"]["identifier"]

    record = service.publish(draft.id, superuser_identity)
    provider = service.pids.get_provider("doi", "external")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.RESERVED
    register_pid(pid_type="doi", pid_value=pid.pid_value,
                 recid=record["id"], provider_name="external")
    assert pid.status == PIDStatus.REGISTERED
