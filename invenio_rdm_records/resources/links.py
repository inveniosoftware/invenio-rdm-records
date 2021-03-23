# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Link utilities for file links."""

# TODO: Move to Invenio-Records-Resources

from invenio_records_resources.resources.records.schemas_links import \
    ItemLink, search_link_when
from marshmallow import Schema
from marshmallow_utils.fields import Link


def fileitem_link_params(record_file):
    """Params function to extract the pid_value."""
    return {
        'pid_value': record_file.record.pid.pid_value,
        'key': record_file.key,
    }


class FileItemLink(ItemLink):
    """Link for files."""

    def __init__(self, **kwargs):
        """Initialize the link."""
        kwargs.setdefault('params', fileitem_link_params)
        super().__init__(**kwargs)


def versions_search_link_params(page_offset):
    """Return params generating function closed over page_offset."""
    def _inner(search_dict):
        """Return parameters for the link template."""
        pid_value = search_dict.pop("pid_value", None)

        # Filter out internal parameters
        params = {
            k: v for k, v in search_dict.items() if not k.startswith('_')
        }

        params['page'] += page_offset

        return {"pid_value": pid_value, "params": params}

    return _inner


class VersionsSearchLink(Link):
    """Link field for a search versions."""

    def __init__(self, template, page_offset):
        """Constructor."""
        super().__init__(
            template=template,
            params=versions_search_link_params(page_offset),
            when=search_link_when(page_offset)
        )


class SearchVersionsLinksSchema:
    """Factory class to dynamically generate a search versions links Schema.

    Follows the same interface as other such LinksSchema. Is needed in order
    - to account for pid_value in search links URL
    - to simplify creation of all the links
    """

    @classmethod
    def create(cls, template):
        """Dynamically create the schema from passed template."""
        return Schema.from_dict({
            "prev": VersionsSearchLink(template=template, page_offset=-1),
            "self": VersionsSearchLink(template=template, page_offset=0),
            "next": VersionsSearchLink(template=template, page_offset=1),
        })
