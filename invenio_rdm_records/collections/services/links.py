# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collection links."""

from invenio_records_resources.services.base.links import Link, LinksTemplate


class CollectionLinkstemplate(LinksTemplate):
    """Templates for generating links for a collection object."""

    def __init__(self, links=None, context=None):
        """Initialize the links template."""
        super().__init__(links, context)


class CollectionLink(Link):
    """Link variables setter for Collection links."""

    @staticmethod
    def vars(collection, vars):
        """Variables for the URI template."""
        vars.update(
            {
                "community": collection.community.slug,
                "tree": collection.collection_tree.slug,
                "collection": collection.slug,
                "id": collection.id,
            }
        )
