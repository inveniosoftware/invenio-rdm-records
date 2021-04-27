# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Service level tests for Invenio RDM Records."""

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError

from invenio_rdm_records.proxies import current_rdm_records


def test_resolve_pid(
    app, location, es_clear, superuser_identity, minimal_record
):
    """Test the reserve function with client logged in."""
    service = current_rdm_records.records_service
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # publish the record
    record = service.publish(draft.id, superuser_identity)
    doi = record.to_dict()["pids"]["doi"]["identifier"]

    # test resolution
    resolved_record = service.resolve_pid(
        id_=doi,
        identity=superuser_identity,
        pid_type="doi"
    )
    assert resolved_record.id == record.id
    assert resolved_record.to_dict()["pids"]["doi"]["identifier"] == doi


def test_resolve_non_existing_pid(
    app, location, es_clear, superuser_identity, minimal_record
):
    """Test the reserve function with client logged in."""
    service = current_rdm_records.records_service
    # create the draft
    draft = service.create(superuser_identity, minimal_record)
    # publish the record
    record = service.publish(draft.id, superuser_identity)
    doi = record.to_dict()["pids"]["doi"]["identifier"]

    # test resolution
    fake_doi = "10.1234/client.12345-abdce"
    with pytest.raises(PIDDoesNotExistError):
        service.resolve_pid(
            id_=fake_doi,
            identity=superuser_identity,
            pid_type="doi"
        )
