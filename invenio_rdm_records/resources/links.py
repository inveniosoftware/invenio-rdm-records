# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Link utilities for file links."""

# TODO: Move to Invenio-Records-Resources

from invenio_records_resources.resources.records.schemas_links import ItemLink


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
