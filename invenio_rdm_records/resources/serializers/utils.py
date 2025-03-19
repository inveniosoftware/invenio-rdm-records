# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Helpers for serializers."""

import math

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_search.engine import dsl
from invenio_vocabularies.proxies import current_service as vocabulary_service

from .errors import VocabularyItemNotFoundError


def get_vocabulary_props(vocabulary, fields, id_):
    """Returns props associated with a vocabulary, id_."""
    # This is ok given that read_all is cached per vocabulary+fields and
    # is reused overtime
    results = vocabulary_service.read_all(
        system_identity,
        ["id"] + fields,
        vocabulary,
        extra_filter=dsl.Q("term", id=id_),
    )

    for h in results.hits:
        return h.get("props", {})

    raise VocabularyItemNotFoundError(
        _("The '{vocabulary}' vocabulary item '{id_}' was not found.").format(
            vocabulary=vocabulary, id_=id_
        )
    )


def get_preferred_identifier(priority, identifiers):
    """Get the preferred identifier."""
    scheme_to_idx = {}

    for idx, identifier in enumerate(identifiers):
        scheme_to_idx[identifier.get("scheme", "Other")] = idx

    found_schemes = scheme_to_idx.keys()
    for scheme in priority:
        if scheme in found_schemes:
            idx = scheme_to_idx[scheme]
            return identifiers[idx]

    return None


def convert_size(size_bytes):
    """Convert syze, in bytes, to its string representation.

    Computed in bytes (base 1024):
    """
    if size_bytes == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
