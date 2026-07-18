# SPDX-FileCopyrightText: 2023-2025 CERN.
# SPDX-FileCopyrightText: 2025-2026 Front Matter.
# SPDX-License-Identifier: MIT

"""Resources serializers tests."""

import re
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from commonmeta import Metadata

from invenio_rdm_records.resources.serializers import CrossrefXMLSerializer

CROSSREF_MOD = "invenio_rdm_records.resources.serializers.crossref"


def _version_record(own_doi, parent_doi=None, parent_id="3jbwv-w1332"):
    """Minimal InvenioRDM version record dict for relation tests."""
    parent = {"id": parent_id}
    if parent_doi:
        parent["pids"] = {"doi": {"identifier": parent_doi}}
    return {
        "pids": {"doi": {"identifier": own_doi}},
        "parent": parent,
        "metadata": {
            "title": "t",
            "publication_date": "2024-01-01",
            "resource_type": {"id": "blogpost"},
            "creators": [],
        },
    }


def test_crossref_serializer(running_app, full_record_to_dict):
    full_record_to_dict["pids"]["doi"] = {
        "identifier": "10.1234/12345-abcde",
        "provider": "crossref",
        "client": "crossref",
    }
    full_record_to_dict["metadata"]["resource_type"]["id"] = "poster"
    full_record_to_dict["metadata"]["publication_date"] = "2018-01-01"
    expected_data = """
<?xml version="1.0" encoding="utf-8"?>
<doi_batch xmlns="http://www.crossref.org/schema/5.5.0" xmlns:ai="http://www.crossref.org/AccessIndicators.xsd" xmlns:rel="http://www.crossref.org/relations.xsd" xmlns:fr="http://www.crossref.org/fundref.xsd" version="5.5.0">
  <head>
    <doi_batch_id>352789d5-4785-4ab6-8426-cc34773d3acd</doi_batch_id>
    <timestamp>20251101134647</timestamp>
    <depositor>
      <depositor_name>test</depositor_name>
      <email_address>info@example.org</email_address>
    </depositor>
    <registrant>test</registrant>
  </head>
  <body>
    <posted_content type="poster" language="da">
      <contributors>
        <person_name contributor_role="author" sequence="first">
          <given_name>Lars Holm</given_name>
          <surname>Nielsen</surname>
          <ORCID>https://orcid.org/0000-0001-8135-3489</ORCID>
        </person_name>
        <person_name contributor_role="author" sequence="additional">
          <given_name>Blabin</given_name>
          <surname>Tom</surname>
        </person_name>
        <person_name contributor_role="other" sequence="additional">
          <given_name>Lars Holm</given_name>
          <surname>Nielsen</surname>
          <ORCID>https://orcid.org/0000-0001-8135-3489</ORCID>
        </person_name>
        <person_name contributor_role="other" sequence="additional">
          <given_name>Dirkin</given_name>
          <surname>Dirk</surname>
        </person_name>
      </contributors>
      <titles>
        <title>InvenioRDM</title>
      </titles>
      <posted_date>
        <month>1</month>
        <day>1</day>
        <year>2018</year>
      </posted_date>
      <institution>
        <institution_name>InvenioRDM</institution_name>
      </institution>
      <jats:abstract xmlns:jats="http://www.ncbi.nlm.nih.gov/JATS1">
        <jats:p>A description with HTML tags</jats:p>
      </jats:abstract>
      <fr:program xmlns:fr="http://www.crossref.org/fundref.xsd" name="fundref">
        <fr:assertion name="fundgroup">
          <fr:assertion name="ror">https://ror.org/00k4n6c32</fr:assertion>
          <fr:assertion name="award_number">111023</fr:assertion>
        </fr:assertion>
        <fr:assertion name="fundgroup">
          <fr:assertion name="funder_name">Caltech Library</fr:assertion>
        </fr:assertion>
      </fr:program>
      <rel:program xmlns:rel="http://www.crossref.org/relations.xsd" name="relations">
        <rel:related_item>
          <rel:intra_work_relation relationship-type="isVersionOf" identifier-type="doi">10.1234/pgfpj-at058</rel:intra_work_relation>
        </rel:related_item>
      </rel:program>
      <version_info>
        <version>v1.0</version>
      </version_info>
      <doi_data>
        <doi>10.1234/12345-abcde</doi>
        <resource>https://127.0.0.1:5000/records/12345-abcde</resource>
        <collection property="text-mining">
          <item>
            <resource mime_type="text/html">https://127.0.0.1:5000/records/12345-abcde</resource>
          </item>
        </collection>
      </doi_data>
      <citation_list>
        <citation key="ref1">
          <unstructured_citation>Nielsen et al,.. 0000 0001 1456 7559</unstructured_citation>
        </citation>
      </citation_list>
    </posted_content>
  </body>
</doi_batch>""".strip()
    serializer = CrossrefXMLSerializer()
    result = serializer.serialize_object(full_record_to_dict)
    assert strip_dynamic(expected_data) == strip_dynamic(result)


def test_add_version_relations_child_isversionof():
    """A version deposit links to its concept DOI via IsVersionOf."""
    serializer = CrossrefXMLSerializer.__new__(CrossrefXMLSerializer)
    record = _version_record("10.53731/kdqkf-nf052", parent_doi="10.53731/3jbwv-w1332")
    metadata = Metadata(record, via="inveniordm")
    metadata.relations = []
    serializer._add_version_relations(record, metadata)
    assert {
        "id": "https://doi.org/10.53731/3jbwv-w1332",
        "type": "IsVersionOf",
    } in metadata.relations


def test_add_version_relations_parent_hasversion_all_versions():
    """The concept deposit lists every version via HasVersion (scan_versions).

    Unlike the ChainObject (which exposes only the latest child), this reaches
    DataCite parity: the concept DOI links to *all* versions.
    """
    serializer = CrossrefXMLSerializer.__new__(CrossrefXMLSerializer)
    record = _version_record("10.53731/kdqkf-nf052")
    metadata = Metadata(record, via="inveniordm")
    metadata.relations = []
    # The parent/concept deposit is passed as a ChainObject.
    chain = SimpleNamespace(_child={"id": "kid"}, _parent={})
    svc = MagicMock()
    svc.scan_versions.return_value = [
        {"pids": {"doi": {"identifier": "10.53731/kdqkf-nf052"}}},
        {"pids": {"doi": {"identifier": "10.53731/older-v1"}}},
    ]
    with patch(f"{CROSSREF_MOD}.current_rdm_records_service", new=svc):
        serializer._add_version_relations(chain, metadata)
    assert {
        "id": "https://doi.org/10.53731/kdqkf-nf052",
        "type": "HasVersion",
    } in metadata.relations
    assert {
        "id": "https://doi.org/10.53731/older-v1",
        "type": "HasVersion",
    } in metadata.relations
    svc.indexer.refresh.assert_called_once()


def strip_dynamic(xml_str):
    """Helper function to strip dynamic content for testing."""
    xml_str = re.sub(r"<doi_batch_id>.*?</doi_batch_id>", "", xml_str, flags=re.DOTALL)
    xml_str = re.sub(r"<timestamp>.*?</timestamp>", "", xml_str, flags=re.DOTALL)
    return xml_str.strip()
