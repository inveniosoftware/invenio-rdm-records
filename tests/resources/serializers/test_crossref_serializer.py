# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN.
# Copyright (C) 2025-2026 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import re

from invenio_rdm_records.resources.serializers import CrossrefXMLSerializer


def test_crossref_serializer(running_app, full_record_to_dict):
    full_record_to_dict["pids"]["doi"] = {
        "identifier": "10.1234/12345-abcde",
        "provider": "crossref",
        "client": "crossref",
    }
    full_record_to_dict["metadata"]["resource_type"]["id"] = "publication-preprint"
    expected_data = """
<?xml version="1.0" encoding="utf-8"?>
<doi_batch xmlns="http://www.crossref.org/schema/5.4.0" xmlns:ai="http://www.crossref.org/AccessIndicators.xsd" xmlns:rel="http://www.crossref.org/relations.xsd" xmlns:fr="http://www.crossref.org/fundref.xsd" version="5.4.0">
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
    <posted_content type="other" language="da">
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
      </contributors>
      <titles>
        <title>InvenioRDM</title>
      </titles>
      <institution>
        <institution_name>InvenioRDM</institution_name>
      </institution>
      <jats:abstract xmlns:jats="http://www.ncbi.nlm.nih.gov/JATS1">
        <jats:p>A description with HTML tags</jats:p>
      </jats:abstract>
      <fr:program xmlns:fr="http://www.crossref.org/fundref.xsd" name="fundref">
        <fr:assertion name="ror">https://ror.org/00k4n6c32</fr:assertion>
        <fr:assertion name="award_number">111023</fr:assertion>
      </fr:program>
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
    serialized_record = serializer.serialize_object(full_record_to_dict).decode("utf-8")
    assert strip_dynamic(expected_data) == strip_dynamic(serialized_record)


def strip_dynamic(xml_str):
    """Helper function to strip dynamic content for testing."""
    xml_str = re.sub(r"<doi_batch_id>.*?</doi_batch_id>", "", xml_str, flags=re.DOTALL)
    xml_str = re.sub(r"<timestamp>.*?</timestamp>", "", xml_str, flags=re.DOTALL)
    return xml_str.strip()
