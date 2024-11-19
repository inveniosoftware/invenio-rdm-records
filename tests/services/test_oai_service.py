# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Service level tests for OAI Sets."""

import pytest
from invenio_db import db
from invenio_oaiserver.models import OAISet
from invenio_search import current_search_client
from marshmallow import ValidationError

from invenio_rdm_records.oaiserver.services.config import OAIPMHServerServiceConfig
from invenio_rdm_records.oaiserver.services.errors import OAIPMHSetNotEditable
from invenio_rdm_records.oaiserver.services.services import OAIPMHServerService
from invenio_rdm_records.proxies import (
    current_oaipmh_server_service,
    current_rdm_records_service,
)


def test_minimal_set_creation_and_edit(running_app, search_clear, minimal_oai_set):
    superuser_identity = running_app.superuser_identity
    service = current_oaipmh_server_service

    oai_item = service.create(superuser_identity, minimal_oai_set)
    oai_dict = oai_item.to_dict()
    assert oai_dict["name"] == "name"

    data = {**oai_dict, "name": "Updated name"}
    updated_oai_item = service.update(superuser_identity, oai_item._item.id, data)

    updated_oai_dict = updated_oai_item.to_dict()
    assert updated_oai_dict["name"] == "Updated name"


def test_raise_error_on_edit_and_delete(
    running_app, search_clear, minimal_oai_set, anyuser_identity
):
    superuser_identity = running_app.superuser_identity
    service = current_oaipmh_server_service
    system_created_oai_set = OAISet(**minimal_oai_set, system_created=True)
    db.session.add(system_created_oai_set)
    db.session.commit()
    oai_item = service.result_item(
        service=service,
        identity=anyuser_identity,
        item=system_created_oai_set,
        links_tpl=service.links_item_tpl,
    )

    oai_dict = oai_item.to_dict()
    assert oai_dict["name"] == "name"

    data = {**oai_dict, "name": "Updated name"}

    # Cannot update
    with pytest.raises(OAIPMHSetNotEditable):
        service.update(superuser_identity, system_created_oai_set.id, data)

    # Cannot delete
    with pytest.raises(OAIPMHSetNotEditable):
        service.delete(superuser_identity, system_created_oai_set.id)


def test_reserved_prefixes(running_app, search_clear, minimal_oai_set):
    superuser_identity = running_app.superuser_identity

    service = OAIPMHServerService(
        config=OAIPMHServerServiceConfig, extra_reserved_prefixes={"cds-"}
    )
    minimal_oai_set["spec"] = "cds-test"

    # Must fail as "cds-" is a reserved prefix
    with pytest.raises(ValidationError):
        service.create(superuser_identity, minimal_oai_set)


def test_rebuild_index(running_app, search_clear, minimal_oai_set):
    superuser_identity = running_app.superuser_identity
    service = current_oaipmh_server_service

    oai_record_index = current_rdm_records_service.record_cls.index._name
    percolators_index = f"{oai_record_index}-percolators"
    current_search_client.indices.delete(index=percolators_index, ignore=[404])
    current_search_client.indices.refresh()

    oai_item = service.create(superuser_identity, minimal_oai_set)
    oai_dict = oai_item.to_dict()
    assert oai_dict["name"] == "name"

    current_search_client.indices.refresh()
    res = current_search_client.search(index=percolators_index)
    assert res["hits"]["total"]["value"] == 1
    oai_hit = res["hits"]["hits"][0]
    assert oai_hit["_id"] == "oaiset-spec"
    assert oai_hit["_source"] == {
        "query": {"query_string": {"query": "is_published:true"}}
    }

    # Delete the percolator index
    current_search_client.indices.delete(index=percolators_index)
    current_search_client.indices.refresh()
    assert current_search_client.indices.exists(index=percolators_index) is False

    # Rebuild the OAI sets percolator index
    service.rebuild_index(superuser_identity)
    current_search_client.indices.refresh(index=percolators_index)

    res = current_search_client.search(index=percolators_index)
    assert res["hits"]["total"]["value"] == 1
    assert oai_hit["_id"] == "oaiset-spec"
    assert oai_hit["_source"] == {
        "query": {"query_string": {"query": "is_published:true"}}
    }
