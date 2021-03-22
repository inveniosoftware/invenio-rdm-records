# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from flask import g
from flask_resources.context import resource_requestctx
from invenio_drafts_resources.resources import RecordResource
from invenio_records_resources.resources.records.utils import es_preference

#
# User records
#
class RDMUserRecordsResource(RecordResource):
    """Bibliographic record user records resource."""

    def search(self):
        """Perform a search over the items."""
        # TODO: Define this one in Invenio-Drafts-Resources, once resources
        # have been refactored to be easier to deal with.
        identity = g.identity
        hits = self.service.search_drafts(
            identity=identity,
            params=resource_requestctx.url_args,
            links_config=self.config.links_config,
            es_preference=es_preference()
        )
        return hits.to_dict(), 200
