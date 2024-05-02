class RecordFilesProcessor:
    """Base class for record files processors."""

    def _can_process(self, file_record, draft, record):
        """Determine if this processor can process a given record file."""
        return False

    def _process(self, draft, record, uow=None):
        """Process a record file."""
        pass

    def __call__(self, draft, record, uow=None):
        if self._can_process(draft, record):
            self._process(draft, record, uow=uow)
