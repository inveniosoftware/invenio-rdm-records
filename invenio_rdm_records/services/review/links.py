# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utility for rendering URI template links."""

from invenio_records_resources.services.base.links import Link


class RequestRecordLink(Link):
    """Shortcut for writing record request links."""

    @staticmethod
    def vars(request, vars):
        """Variables for the URI template."""
        vars.update({"record_id": request["topic"]["record"]})
