# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""CodeMeta custom fields tests."""

from invenio_access.permissions import system_identity

from invenio_rdm_records.records.api import RDMDraft, RDMRecord


def test_not_loaded_by_default(
    initialise_custom_fields, custom_field_exists, codemeta_cf_name, running_app
):
    """Tests that codemeta custom fields are not loaded by default."""
    # By default, CFs are disabled. They must be manually added (e.g. per instance) and initialised.
    result = custom_field_exists(codemeta_cf_name)
    assert result.exit_code == 0
    assert f"Field {codemeta_cf_name} does not exist" in result.output


def test_load_on_demand(
    custom_field_exists,
    codemeta_cf_name,
    initialise_codemeta_custom_fields,
    running_app,
):
    """Tests whether codemeta CF are correctly loaded on demand.
    This will test the validity of codemeta custom fields (e.g. whether they load without any errors).
    It is not meant to test the custom fields loading mechanism."""
    result = custom_field_exists(codemeta_cf_name)
    assert result.exit_code == 0
    assert f"Field {codemeta_cf_name} exists" in result.output


def test_mappings(initialise_codemeta_custom_fields, codemeta_cf_name, running_app):
    """Tests codemeta CF mappings after loading."""
    # Validate custom fiels are mapped
    record_mapping_field = list(RDMRecord.index.get_mapping().values())[0]["mappings"][
        "properties"
    ]["custom_fields"]

    draft_mapping_field = list(RDMDraft.index.get_mapping().values())[0]["mappings"][
        "properties"
    ]["custom_fields"]

    assert record_mapping_field["properties"].get(codemeta_cf_name)
    assert draft_mapping_field["properties"].get(codemeta_cf_name)


def test_record_creation_with_codemeta_fields(
    initialise_codemeta_custom_fields,
    codemeta_cf_name,
    codemeta_cf_value,
    codemeta_record,
    db,
    running_app,
    service,
):
    """Tests the creation of a CodeMeta draft and record. Validates record indexing."""
    # Test record
    assert not codemeta_record._errors
    assert codemeta_record.data.get("custom_fields") is not None
    assert (
        codemeta_record.data.get("custom_fields")[codemeta_cf_name]["id"]
        == codemeta_cf_value
    )

    # Validate record was indexed with custom field
    search_obj = service.search(system_identity)
    assert search_obj is not None
    assert search_obj.total > 0

    document = list(search_obj.hits)[0]
    assert document is not None
    assert document.get("custom_fields") is not None
    assert document.get("custom_fields")[codemeta_cf_name]["id"] == codemeta_cf_value


def test_codemeta_facets(
    initialise_codemeta_custom_fields,
    codemeta_record,
    service,
    codemeta_cf_facetted_term,
):
    """Tests CodeMeta custom fields facets."""
    # Intialize search.
    search_obj = service.search(system_identity)

    # Validate that search aggregations contain cf name.
    assert search_obj.aggregations[codemeta_cf_facetted_term]


def test_codemeta_fields_search(
    initialise_codemeta_custom_fields,
    codemeta_record,
    codemeta_cf_facetted_term,
    codemeta_cf_value,
    service,
):
    """Tests a record search by a CodeMeta term."""
    # Intialize search, pass a CodeMeta term as search parameter.
    search_obj = service.search(
        system_identity, params={codemeta_cf_facetted_term: codemeta_cf_value}
    )
    assert search_obj.total > 0
