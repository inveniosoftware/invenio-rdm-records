# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Communities Service."""

from flask_babelex import lazy_gettext as _
from invenio_drafts_resources.services.records import RecordService
from invenio_records_resources.services.uow import unit_of_work


class RecordCommunitiesService(RecordService):
    """Record communities service.

    The communities service is in charge of managing communities of a given record.
    """

    @unit_of_work()
    def create(self, identity, data, record, uow=None):
        """Include the record in the given communities."""
        pass

    @unit_of_work()
    def delete(self, identity, id_, revision_id=None, uow=None):
        """Remove communities from the record."""
        pass
