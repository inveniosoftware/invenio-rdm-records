# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service


def test_load_languages(app, vocabularies):
    vocabularies.load_vocabulary(
        'languages',
        {
            "pid-type": "lng",
            "data-file": "vocabularies/languages.yaml"
        },
        delay=False
    )

    item = vocabulary_service.read(
        ('languages', 'aae'), system_identity)
    item_dict = item.to_dict()

    assert item_dict["id"] == "aae"


def test_load_resource_types(app, vocabularies):
    vocabularies.load_vocabulary(
        'resource_types',
        {
            "pid-type": "rsrct",
            "data-file": "vocabularies/resource_types.yaml"
        },
        delay=False
    )

    item = vocabulary_service.read(
        ('resource_types', 'publication-annotationcollection'),
        system_identity
    )
    item_dict = item.to_dict()

    assert item_dict["id"] == "publication-annotationcollection"
    assert item_dict["props"]["datacite_general"] == "Collection"
