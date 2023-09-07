# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Search dumpers for location information."""


from invenio_records.dumpers import SearchDumperExt

from ..systemfields.access.protection import Visibility


class FilesDumperExt(SearchDumperExt):
    """Files dumper."""

    def dump(self, record, data):
        """Dump the data."""
        public_record_with_restricted_files = (
            data["access"].get("record") == Visibility.PUBLIC.value
            and data["access"].get("files") == Visibility.RESTRICTED.value
        )
        if public_record_with_restricted_files:
            data["files"] = {"enabled": data["files"]["enabled"]}
