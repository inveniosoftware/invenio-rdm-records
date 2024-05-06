# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record components."""

from invenio_drafts_resources.services.records.components import ServiceComponent


class RecordFilesProcessorComponent(ServiceComponent):
    """Service component for RecordFilesProcessor."""

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        for processor in self.service.config.record_file_processors:
            processor(draft, record, uow=self.uow)

    # TODO: Add this method to a new "RDMRecordServiceComponent" class
    def lift_embargo(self, identity, draft=None, record=None):
        """Lift embargo handler."""
        for processor in self.service.config.record_file_processors:
            processor(draft, record, uow=self.uow)
