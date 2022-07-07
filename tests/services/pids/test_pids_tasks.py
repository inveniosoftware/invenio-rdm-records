# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""PID service tasks tests."""

from invenio_pidstore.models import PIDStatus

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.pids.tasks import register_or_update_pid


def test_register_pid(
    running_app, search_clear, minimal_record, mocker, superuser_identity
):
    """Registers a PID."""

    def public_doi(self, metadata, url, doi):
        """Mock doi deletion."""
        pass

    mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        + "DataCiteRESTClient.public_doi",
        public_doi,
    )

    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    record = service.record_cls.publish(draft._record)
    record.pids = {pid.pid_type: {"identifier": pid.pid_value, "provider": "datacite"}}
    record.metadata = draft["metadata"]
    record.register()
    record.commit()
    assert pid.status == PIDStatus.NEW
    pid.reserve()
    assert pid.status == PIDStatus.RESERVED
    register_or_update_pid(recid=record["id"], scheme="doi")
    assert pid.status == PIDStatus.REGISTERED


def test_update_pid(
    running_app, search_clear, minimal_record, mocker, superuser_identity
):
    """No pid provided, creating one by default."""

    def public_doi(self, metadata, url, doi):
        """Mock doi deletion."""
        pass

    def update(self, pid, record, url=None, **kwargs):
        """Mock doi update."""
        pass

    mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        + "DataCiteRESTClient.public_doi",
        public_doi,
    )
    mocked_update = mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        + "DataCitePIDProvider.update"
    )

    mocked_update.side_effect = update

    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)
    doi = record["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.REGISTERED
    # we do not explicitly call the update_pid task
    # we check that the lower level provider update is called
    record_edited = service.edit(superuser_identity, record.id)
    assert mocked_update.called is False
    service.publish(superuser_identity, record_edited.id)
    assert mocked_update.called is True
