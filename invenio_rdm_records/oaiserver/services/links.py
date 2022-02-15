# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Flask-Resources is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utility for rendering URI template links."""

from invenio_records_resources.services.base import Link


class OAIPMHSetLink(Link):
    """Short cut for writing record links."""

    @staticmethod
    def vars(set, vars):
        """Variables for the URI template."""
        vars.update(
            {
                "id": set.id,
                "spec": set.spec,
            }
        )
