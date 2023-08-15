# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources serializers tests."""

import pytest

from invenio_rdm_records.resources.serializers.errors import VocabularyItemNotFoundError
from invenio_rdm_records.resources.serializers.geojson import GeoJSONSerializer


def test_geojson_serializer_no_records():
    """Test serializer to GeoJSON"""
    input_data = {
        "metadata": {},
        "contributors": ["Nielsen, Lars Holm"],
        "types": ["info:eu-repo/semantic/other"],
        "relations": ["doi:10.1234/foo.bar"],
        "descriptions": ["A description \nwith HTML tags", "Bla bla bla"],
        "identifiers": ["1924MNRAS..84..308E", "10.1234/inveniordm.1234"],
        "publishers": ["InvenioRDM"],
        "languages": ["dan", "eng"],
        "formats": ["application/pdf"],
        "titles": ["InvenioRDM"],
        "creators": ["Nielsen, Lars Holm"],
        "subjects": ["custom"],
        "dates": ["2018/2020-09", "info:eu-repo/date/embargoEnd/2131-01-01"],
        "rights": [
            "info:eu-repo/semantics/embargoedAccess",
            "A custom license",
            "https://customlicense.org/licenses/by/4.0/",
            "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/licenses/by/4.0/legalcode",
        ],
    }
    expected_data = {"type": "FeatureCollection", "features": []}

    serializer = GeoJSONSerializer()
    serialized_record = serializer.dump_obj(input_data)

    assert serialized_record == expected_data


def test_geojson_serializer_single_records():
    """Test serializer to GeoJSON"""
    input_data = {
        "metadata": {
            "locations": {
                "features": [
                    {
                        "geometry": {"type": "Point", "coordinates": [6.05, 46.23333]},
                        "identifiers": [
                            {"scheme": "geonames", "identifier": "2661235"}
                        ],
                        "place": "CERN",
                        "description": "Invenio birth place.",
                    }
                ]
            }
        },
        "contributors": ["Nielsen, Lars Holm"],
        "types": ["info:eu-repo/semantic/other"],
        "relations": ["doi:10.1234/foo.bar"],
        "descriptions": ["A description \nwith HTML tags", "Bla bla bla"],
        "identifiers": ["1924MNRAS..84..308E", "10.1234/inveniordm.1234"],
        "publishers": ["InvenioRDM"],
        "languages": ["dan", "eng"],
        "formats": ["application/pdf"],
        "titles": ["InvenioRDM"],
        "creators": ["Nielsen, Lars Holm"],
        "subjects": ["custom"],
        "dates": ["2018/2020-09", "info:eu-repo/date/embargoEnd/2131-01-01"],
        "rights": [
            "info:eu-repo/semantics/embargoedAccess",
            "A custom license",
            "https://customlicense.org/licenses/by/4.0/",
            "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/licenses/by/4.0/legalcode",
        ],
    }
    expected_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [6.05, 46.23333]},
                "properties": {
                    "identifiers": [{"scheme": "geonames", "identifier": "2661235"}],
                    "place": "CERN",
                    "description": "Invenio birth place.",
                },
            }
        ],
    }

    serializer = GeoJSONSerializer()
    serialized_record = serializer.dump_obj(input_data)

    assert serialized_record == expected_data


def test_geojson_serializer_multiple_records():
    """Test serializer to GeoJSON"""
    input_data = {
        "metadata": {
            "locations": {
                "features": [
                    {
                        "geometry": {"type": "Point", "coordinates": [6.05, 46.23333]},
                        "identifiers": [
                            {"scheme": "geonames", "identifier": "2661235"}
                        ],
                        "place": "CERN",
                        "description": "Invenio birth place.",
                    },
                    {
                        "geometry": {"type": "Point", "coordinates": [48.8584, 2.2945]},
                        "identifiers": [{"scheme": "geonames", "identifier": "111"}],
                        "place": "Paris",
                        "description": "Eiffel Tower",
                    },
                ]
            }
        },
        "contributors": ["Nielsen, Lars Holm"],
        "types": ["info:eu-repo/semantic/other"],
        "relations": ["doi:10.1234/foo.bar"],
        "descriptions": ["A description \nwith HTML tags", "Bla bla bla"],
        "identifiers": ["1924MNRAS..84..308E", "10.1234/inveniordm.1234"],
        "publishers": ["InvenioRDM"],
        "languages": ["dan", "eng"],
        "formats": ["application/pdf"],
        "titles": ["InvenioRDM"],
        "creators": ["Nielsen, Lars Holm"],
        "subjects": ["custom"],
        "dates": ["2018/2020-09", "info:eu-repo/date/embargoEnd/2131-01-01"],
        "rights": [
            "info:eu-repo/semantics/embargoedAccess",
            "A custom license",
            "https://customlicense.org/licenses/by/4.0/",
            "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/licenses/by/4.0/legalcode",
        ],
    }
    expected_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [6.05, 46.23333]},
                "properties": {
                    "identifiers": [{"scheme": "geonames", "identifier": "2661235"}],
                    "place": "CERN",
                    "description": "Invenio birth place.",
                },
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [48.8584, 2.2945]},
                "properties": {
                    "identifiers": [{"scheme": "geonames", "identifier": "111"}],
                    "place": "Paris",
                    "description": "Eiffel Tower",
                },
            },
        ],
    }

    serializer = GeoJSONSerializer()
    serialized_record = serializer.dump_obj(input_data)

    assert serialized_record == expected_data
