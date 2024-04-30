from invenio_drafts_resources.services.records.components import ServiceComponent


class RecordFilesProcessorComponent(ServiceComponent):
    """Service component for RecordFilesProcessor."""

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        for processor in self.service.config.record_file_processors:
            processor(draft, record, uow=self.uow)
