# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Helpers for serializers."""

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service

from .errors import VocabularyItemNotFoundError


def map_type(vocabulary, fields, id_):
    """Maps an internal vocabulary type to external vocabulary type."""
    res = vocabulary_service.read_all(
        system_identity,
        ['id'] + fields,
        vocabulary
    )

    for h in res.hits:
        if h["id"] == id_:
            return h["props"] if "props" in h else {}

    raise VocabularyItemNotFoundError(
        f"The '{vocabulary}' vocabulary item  '{id_}' was not found.")
