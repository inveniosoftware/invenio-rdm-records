# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Links for RDM-Records."""

from invenio_records_resources.services import RecordLink


class RecordPIDsLink(RecordLink):
    """Short cut for writing links for records with PIDs."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        to_update = {}
        for scheme, pid in record.pids.items():
            to_update[f"pid_{scheme}"] = pid["identifier"]

        vars.update(to_update)


class HiddenLink:
    """Utility class for keeping track of and resolve links."""

    def should_render(self, obj, ctx):
        """Determine if the link should be rendered."""
        False
