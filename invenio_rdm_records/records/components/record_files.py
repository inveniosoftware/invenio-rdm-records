from invenio_drafts_resources.services.records.components import ServiceComponent


class RecordFilesProcessorComponent(ServiceComponent):
    """Service component for RecordFilesProcessor."""

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        # breakpoint()
        for fname, file in record.files.items():
            for processor in self.service.config.record_file_processors:
                processor(file, draft, record, uow=self.uow)
