# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest
from dateutil.parser import parse
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.resources.serializers.marcxml import MARCXMLSerializer


@pytest.fixture
def updated_full_record(full_record_to_dict):
    """Record with added communities and custom fields."""
    # Add communities
    full_record_to_dict["parent"]["communities"] = {
        "default": "4078bbdf-4860-4f24-bc02-fd2899025ea7",
        "entries": [
            {
                "access": {
                    "member_policy": "open",
                    "members_visibility": "public",
                    "record_submission_policy": "open",
                    "review_policy": "closed",
                    "visibility": "public",
                },
                "children": {"allow": False},
                "created": "2024-04-09T08:38:17.494903+00:00",
                "custom_fields": {},
                "deletion_status": {"is_deleted": False, "status": "P"},
                "id": "4078bbdf-4860-4f24-bc02-fd2899025ea7",
                "links": {},
                "metadata": {
                    "title": "Biodiversity " "Literature " "Repository",
                    "type": {"id": "topic"},
                },
                "revision_id": 2,
                "slug": "blr",
                "updated": "2024-04-09T08:38:17.537548+00:00",
            },
            {
                "access": {
                    "member_policy": "open",
                    "members_visibility": "public",
                    "record_submission_policy": "open",
                    "review_policy": "closed",
                    "visibility": "public",
                },
                "children": {"allow": False},
                "created": "2024-04-09T08:38:17.573631+00:00",
                "custom_fields": {},
                "deletion_status": {"is_deleted": False, "status": "P"},
                "id": "4818dcdb-f52f-4ef0-8b99-38a145b694a7",
                "links": {},
                "metadata": {
                    "title": "Research Data " "Management",
                    "type": {"id": "topic"},
                },
                "revision_id": 2,
                "slug": "rdm",
                "updated": "2024-04-09T08:38:17.608333+00:00",
            },
        ],
        "ids": [
            "4078bbdf-4860-4f24-bc02-fd2899025ea7",
            "4818dcdb-f52f-4ef0-8b99-38a145b694a7",
        ],
    }

    # Add custom fields
    full_record_to_dict["custom_fields"]["thesis:university"] = "A university"

    full_record_to_dict["custom_fields"]["journal:journal"] = {
        "title": "Journal Title",
        "pages": "100",
        "volume": "5",
        "issue": "10",
    }

    # Add files

    full_record_to_dict["files"] = {
        "enabled": True,
        "entries": {
            "test.pdf": {
                "uuid": "cbdf3e08-8077-430e-a7d2-0f37bbea0580",
                "version_id": 3,
                "metadata": {},
                "key": "test.pdf",
                "checksum": "md5:d916d650dc8471cfccb92c807cdc5f98",
                "mimetype": "application/pdf",
                "size": 1934724,
                "ext": "pdf",
                "object_version_id": "cbdf3e08-8077-430e-a7d2-0f37bbea0580",
                "file_id": "cbdf3e08-8077-430e-a7d2-0f37bbea0580",
            }
        },
    }

    # Add contributor with GND identifiers

    full_record_to_dict["metadata"]["contributors"].append(
        {
            "person_or_org": {
                "name": "Doe, John the Contributor",
                "type": "personal",
                "given_name": "John the Contributor",
                "family_name": "Doe",
                "identifiers": [
                    {
                        "scheme": "orcid",
                        "identifier": "0000-0001-8135-3489",
                    },
                    {
                        "scheme": "gnd",
                        "identifier": "gnd:4079154-3",
                    },
                ],
            },
            "role": {"id": "other"},
            "affiliations": [{"id": "cern", "name": "CERN"}, {"name": "free-text"}],
        },
    )

    return full_record_to_dict


# Tests
def test_marcxml_serializer_minimal_record(running_app, minimal_record, parent):
    """Test minimal serializer for MARCXML."""
    serializer = MARCXMLSerializer()
    service = current_rdm_records.records_service
    draft = service.create(system_identity, minimal_record)
    record = service.publish(id_=draft.id, identity=system_identity)

    serialized_record = serializer.serialize_object(record.data)

    expected_data = f"""\
<?xml version='1.0' encoding='utf-8'?>
<record xmlns="http://www.loc.gov/MARC21/slim">
  <leader>00000nam##2200000uu#4500</leader>
  <controlfield tag="001">{record.id}</controlfield>
  <datafield tag="024" ind1=" " ind2=" ">
    <subfield code="2">doi</subfield>
    <subfield code="a">10.1234/{record.id}</subfield>
  </datafield>
  <datafield tag="909" ind1="C" ind2="O">
    <subfield code="o">oai:inveniordm:{record.id}</subfield>
  </datafield>
  <datafield tag="700" ind1=" " ind2=" ">
    <subfield code="a">Troy Inc.</subfield>
  </datafield>
  <datafield tag="245" ind1=" " ind2=" ">
    <subfield code="a">A Romans story</subfield>
  </datafield>
  <datafield tag="100" ind1=" " ind2=" ">
    <subfield code="a">Brown, Troy</subfield>
  </datafield>
  <datafield tag="540" ind1=" " ind2=" ">
    <subfield code="a">info:eu-repo/semantics/metadata-onlyAccess</subfield>
  </datafield>
  <datafield tag="260" ind1=" " ind2=" ">
    <subfield code="b">Acme Inc</subfield>
    <subfield code="c">2020-06-01</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">info:eu-repo/semantics/other</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">image</subfield>
    <subfield code="b">photo</subfield>
  </datafield>
  <controlfield tag="005">{parse(record["updated"]).strftime("%Y%m%d%H%M%S.0")}</controlfield>
  <datafield tag="542" ind1=" " ind2=" ">
    <subfield code="l">metadata-only</subfield>
  </datafield>
  <datafield tag="773" ind1=" " ind2=" ">
    <subfield code="a">10.1234/{record.data["parent"]["id"]}</subfield>
    <subfield code="i">isVersionOf</subfield>
    <subfield code="n">doi</subfield>
  </datafield>
</record>
"""

    assert serialized_record == expected_data


def test_marcxml_serializer_full_record(db, running_app, updated_full_record):
    """Test serializer for MARCXML with a full record."""
    serializer = MARCXMLSerializer()
    serialized_record = serializer.serialize_object(updated_full_record)

    expected_data = f"""\
<?xml version='1.0' encoding='utf-8'?>
<record xmlns="http://www.loc.gov/MARC21/slim">
  <leader>00000nam##2200000uu#4500</leader>
  <controlfield tag="001">12345-abcde</controlfield>
  <datafield tag="024" ind1=" " ind2=" ">
    <subfield code="2">doi</subfield>
    <subfield code="a">10.1234/12345-abcde</subfield>
  </datafield>
  <datafield tag="909" ind1="C" ind2="O">
    <subfield code="o">oai:invenio-rdm.com:12345-abcde</subfield>
    <subfield code="p">user-blr</subfield>
    <subfield code="p">user-rdm</subfield>
  </datafield>
  <datafield tag="700" ind1=" " ind2=" ">
    <subfield code="a">Nielsen, Lars Holm</subfield>
    <subfield code="0">(orcid)0000-0001-8135-3489</subfield>
    <subfield code="u">CERN</subfield>
    <subfield code="4">oth</subfield>
  </datafield>
  <datafield tag="700" ind1=" " ind2=" ">
    <subfield code="a">Dirk, Dirkin</subfield>
    <subfield code="4">oth</subfield>
  </datafield>
  <datafield tag="700" ind1=" " ind2=" ">
    <subfield code="a">Doe, John the Contributor</subfield>
    <subfield code="0">(orcid)0000-0001-8135-3489</subfield>
    <subfield code="0">(gnd)gnd:4079154-3</subfield>
    <subfield code="u">CERN</subfield>
    <subfield code="4">oth</subfield>
  </datafield>
  <datafield tag="700" ind1=" " ind2=" ">
    <subfield code="a">Tom, Blabin</subfield>
  </datafield>
  <datafield tag="245" ind1=" " ind2=" ">
    <subfield code="a">InvenioRDM</subfield>
  </datafield>
  <datafield tag="100" ind1=" " ind2=" ">
    <subfield code="a">Nielsen, Lars Holm</subfield>
    <subfield code="0">(orcid)0000-0001-8135-3489</subfield>
    <subfield code="u">CERN</subfield>
  </datafield>
  <datafield tag="856" ind1=" " ind2="2">
    <subfield code="a">doi:10.1234/foo.bar</subfield>
  </datafield>
  <datafield tag="540" ind1=" " ind2=" ">
    <subfield code="a">info:eu-repo/semantics/embargoedAccess</subfield>
  </datafield>
  <datafield tag="540" ind1=" " ind2=" ">
    <subfield code="a">A custom license</subfield>
    <subfield code="u">https://customlicense.org/licenses/by/4.0/</subfield>
  </datafield>
  <datafield tag="540" ind1=" " ind2=" ">
    <subfield code="a">Creative Commons Attribution 4.0 International</subfield>
    <subfield code="u">https://creativecommons.org/licenses/by/4.0/legalcode</subfield>
  </datafield>
  <datafield tag="650" ind1="1" ind2="7"/>
  <datafield tag="650" ind1="1" ind2="7">
    <subfield code="a">cc-by-4.0</subfield>
    <subfield code="2">spdx</subfield>
  </datafield>
  <datafield tag="653" ind1=" " ind2=" ">
    <subfield code="a">Abdominal Injuries</subfield>
  </datafield>
  <datafield tag="653" ind1=" " ind2=" ">
    <subfield code="a">custom</subfield>
  </datafield>
  <datafield tag="520" ind1=" " ind2=" ">
    <subfield code="a">&amp;lt;h1&amp;gt;A description&amp;lt;/h1&amp;gt; &amp;lt;p&amp;gt;with HTML tags&amp;lt;/p&amp;gt;</subfield>
  </datafield>
  <datafield tag="500" ind1=" " ind2=" ">
    <subfield code="a">Bla bla bla</subfield>
  </datafield>
  <datafield tag="041" ind1=" " ind2=" ">
    <subfield code="a">dan</subfield>
  </datafield>
  <datafield tag="041" ind1=" " ind2=" ">
    <subfield code="a">eng</subfield>
  </datafield>
  <datafield tag="999" ind1="C" ind2="5">
    <subfield code="x">Nielsen et al,..</subfield>
  </datafield>
  <datafield tag="260" ind1=" " ind2=" ">
    <subfield code="b">InvenioRDM</subfield>
    <subfield code="c">2018/2020-09</subfield>
    <subfield code="c">info:eu-repo/date/embargoEnd/2131-01-01</subfield>
  </datafield>
  <datafield tag="502" ind1=" " ind2=" ">
    <subfield code="c">A university</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">user-blr</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">user-rdm</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">info:eu-repo/semantics/other</subfield>
  </datafield>
  <datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">image</subfield>
    <subfield code="b">photo</subfield>
  </datafield>
  <datafield tag="520" ind1=" " ind2="1">
    <subfield code="a">application/pdf</subfield>
  </datafield>
  <datafield tag="520" ind1=" " ind2="2">
    <subfield code="a">11 pages</subfield>
  </datafield>
  <datafield tag="536" ind1=" " ind2=" ">
    <subfield code="c">111023</subfield>
    <subfield code="a">Launching of the research program on meaning processing</subfield>
  </datafield>
  <controlfield tag="005">20231114183055.0</controlfield>
  <datafield tag="856" ind1="4" ind2=" ">
    <subfield code="s">1934724</subfield>
    <subfield code="z">md5:d916d650dc8471cfccb92c807cdc5f98</subfield>
    <subfield code="u">https://127.0.0.1:5000/records/12345-abcde/files/test.pdf</subfield>
  </datafield>
  <datafield tag="542" ind1=" " ind2=" ">
    <subfield code="l">embargoed</subfield>
  </datafield>
  <datafield tag="773" ind1=" " ind2=" ">
    <subfield code="a">10.1234/foo.bar</subfield>
    <subfield code="i">Is cited by</subfield>
    <subfield code="n">doi</subfield>
  </datafield>
  <datafield tag="773" ind1=" " ind2=" ">
    <subfield code="a">10.1234/pgfpj-at058</subfield>
    <subfield code="i">isVersionOf</subfield>
    <subfield code="n">doi</subfield>
  </datafield>
  <datafield tag="909" ind1="C" ind2="4">
    <subfield code="p">Journal Title</subfield>
    <subfield code="v">5</subfield>
    <subfield code="n">10</subfield>
    <subfield code="c">100</subfield>
    <subfield code="y">2018/2020-09</subfield>
  </datafield>
</record>
"""

    assert serialized_record == expected_data
