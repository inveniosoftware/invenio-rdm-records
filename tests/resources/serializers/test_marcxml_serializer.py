# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

from collections import Iterable

import pytest
from dojson.contrib.marc21.utils import GroupableOrderedDict, create_record

from invenio_rdm_records.resources.serializers.marcxml import MARCXMLSerializer


@pytest.fixture(scope="function")
def updated_minimal_record(minimal_record):
    """Update fields (done after record create) for MARCXML serializer."""
    minimal_record["access"]["status"] = "open"
    for creator in minimal_record["metadata"]["creators"]:
        name = creator["person_or_org"].get("name")
        if not name:
            creator["person_or_org"]["name"] = "Name"

    return minimal_record


@pytest.fixture(scope="function")
def updated_full_record(full_record):
    """Update fields (done after record create) for MARCXML serializer."""
    full_record["access"]["status"] = "embargoed"

    return full_record


def test_marcxml_serializer_minimal_record(running_app, updated_minimal_record):
    """Test serializer for MARCXML"""
    serializer = MARCXMLSerializer()
    serialized_record = create_record(
        serializer.serialize_object(updated_minimal_record)
    )

    expected_data = '<record xmlns="http://www.loc.gov/MARC21/slim"><datafield tag="245" ind1="a" ind2=" "><subfield code="a">A Romans story</subfield></datafield><datafield tag="260" ind1="c" ind2=" "><subfield code="c">2020-06-01</subfield></datafield><datafield tag="260" ind1="b" ind2=" "><subfield code="a">Acme Inc</subfield></datafield><datafield tag="901" ind1=" " ind2=" "><subfield code="u">info:eu-repo/semantic/other</subfield></datafield><datafield tag="100" ind1="a" ind2=" "><subfield code="a">Name</subfield><subfield code="a">Troy Inc.</subfield></datafield><datafield tag="540" ind1=" " ind2=" "><subfield code="a">info:eu-repo/semantics/openAccess</subfield></datafield></record>'
    expected_data = create_record(expected_data)

    record1 = flatten(record_to_string_list(serialized_record))
    record2 = flatten(record_to_string_list(expected_data))

    record1 = set(record1)
    record2 = set(record2)

    assert record1 == record2


def record_to_string_list(record):
    """Recursively unnest all elements from GroupableOrderedDict"""
    if isinstance(record, str):
        return record
    if isinstance(record, GroupableOrderedDict):
        return record_to_string_list(record.values())
    elements = []
    for rec in record:
        elements.append(record_to_string_list(rec))
    return elements


def flatten(elements):
    """Flattens a n-dimensional irregular list"""
    if isinstance(elements, Iterable) and not isinstance(elements, str):
        return [a for i in elements for a in flatten(i)]
    else:
        return [elements]


def test_marcxml_serializer_full_record(running_app, updated_full_record):
    """Test serializer for MARCXML"""
    serializer = MARCXMLSerializer()
    serialized_record = create_record(serializer.serialize_object(updated_full_record))

    expected_data = '<record xmlns="http://www.loc.gov/MARC21/slim"><datafield tag="510" ind1=" " ind2=" "><subfield code="a">name=test location place; description=test location description; lat=-32.94682; lon=-60.63932</subfield></datafield><datafield tag="260" ind1="c" ind2=" "><subfield code="c">2018/2020-09</subfield><subfield code="c">info:eu-repo/date/embargoEnd/2131-01-01</subfield></datafield><datafield tag="856" ind1=" " ind2="2"><subfield code="a">doi:10.1234/foo.bar</subfield></datafield><datafield tag="540" ind1=" " ind2=" "><subfield code="a">info:eu-repo/semantics/embargoedAccess</subfield><subfield code="a">A custom license</subfield><subfield code="a">https://customlicense.org/licenses/by/4.0/</subfield><subfield code="a">Creative Commons Attribution 4.0 International</subfield><subfield code="a">https://creativecommons.org/licenses/by/4.0/legalcode</subfield></datafield><datafield tag="520" ind1=" " ind2="1"><subfield code="a">application/pdf</subfield></datafield><datafield tag="901" ind1=" " ind2=" "><subfield code="u">info:eu-repo/semantic/other</subfield></datafield><datafield tag="024" ind1=" " ind2=" "><subfield code="a">1924MNRAS..84..308E</subfield><subfield code="a">10.5281/inveniordm.1234</subfield></datafield><datafield tag="100" ind1="a" ind2=" "><subfield code="a">Nielsen, Lars Holm</subfield></datafield><datafield tag="653" ind1=" " ind2=" "><subfield code="a">custom</subfield></datafield><datafield tag="520" ind1=" " ind2=" "><subfield code="a">A description \nwith HTML tags</subfield><subfield code="a">Bla bla bla</subfield></datafield><datafield tag="024" ind1=" " ind2="3"><subfield code="a">v1.0</subfield></datafield><datafield tag="245" ind1="a" ind2=" "><subfield code="a">InvenioRDM</subfield></datafield><datafield tag="856" ind1=" " ind2="1"><subfield code="a">award_identifiers_scheme=null; award_identifiers_identifier=null; award_title=null; award_number=null; funder_id=00k4n6c32; funder_name=null; </subfield></datafield><datafield tag="700" ind1="a" ind2=" "><subfield code="u">Nielsen, Lars Holm</subfield></datafield><datafield tag="520" ind1=" " ind2="2"><subfield code="a">11 pages</subfield></datafield><datafield tag="260" ind1="b" ind2=" "><subfield code="a">InvenioRDM</subfield></datafield></record>'
    expected_data = create_record(expected_data)

    record1 = flatten(record_to_string_list(serialized_record))
    record2 = flatten(record_to_string_list(expected_data))

    record1 = set(record1)
    record2 = set(record2)

    assert record1 == record2
