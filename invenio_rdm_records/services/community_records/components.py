# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Rdm-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Community records components."""
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_records_resources.services.uow import TaskOp

from invenio_rdm_records.services.tasks import remove_community_from_records


class CommunityRecordsComponent(ServiceComponent):
    """Service component for community records."""

    def delete(self, identity, data=None, record=None, uow=None, **kwargs):
        """Spawn tasks to remove all the records from the community."""
        community = record
        self.uow.register(TaskOp(remove_community_from_records, str(community.id)))
