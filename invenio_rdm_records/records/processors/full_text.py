from contextlib import contextmanager
from flask import current_app
from invenio_db import db
from invenio_rdm_records.records.processors.base import RecordFilesProcessor
from invenio_files_rest.models import FileInstance, ObjectVersion
from invenio_records_resources.services.uow import TaskOp

from invenio_rdm_records.services.files.tasks import extract_full_text


class FullTextProcessor(RecordFilesProcessor):
    """Full text pdf extraction."""

    valid_extensions = ["pdf"]

    def _can_process(self, draft, record):
        """Determine if a record should be processed."""
        if (
            # Check if full text extraction is enabled
            current_app.config.get("FULL_TEXT_EXTRACTION_ENABLED", False)
            # Check for compatible files
            and bool(set(self.valid_extensions).intersection(record.files.exts))
        ):
            return True
        return False

    def _can_process_file(self, file_record):
        """Determine if a file should be processed."""
        return file_record.file.ext in self.valid_extensions

    def _cleanup(self, record, uow=None):
        """Clean up unused text files."""
        ...

    @contextmanager
    def unlocked_bucket(self, files):
        """Context manager to auto lock files."""
        files.unlock()
        yield
        files.lock()

    def _process_file(self, file_record, record, uow=None):
        if not self._can_process_file(file_record):
            return

        status_file = record.media_files.get(f"{file_record.key}.txt")
        if status_file:
            has_file_changed = status_file.processor["source_file_id"] != str(
                file_record.file.id
            )
            if status_file.processor["status"] == "finished" and not has_file_changed:
                return

        try:
            with db.session.begin_nested():
                # Check and create a media file if it doesn't exist
                if status_file is None:
                    fi = FileInstance.create()
                    fi.init_contents(default_location=record.media_bucket.location.uri)
                    obj = ObjectVersion.create(
                        record.media_bucket, f"{file_record.key}.txt", _file_id=fi.id
                    )
                    status_file = record.media_files.create(
                        f"{file_record.key}.txt",
                        obj=obj,
                    )

                status_file.processor = {
                    "type": "full-text",
                    "status": "init",
                    "source_file_id": str(file_record.file.id),
                    "props": {},
                }
                status_file.access.hidden = True
                status_file.commit()
                record.media_files.commit(f"{file_record.key}.txt")
            uow.register(
                TaskOp(
                    extract_full_text,  # task name
                    record_id=record["id"],
                    file_key=file_record.key,
                )
            )
        except Exception:
            # Nested transaction for current file is rolled back
            current_app.logger.exception(
                "Failed to initialize full text extraction.",
                extra={
                    "record_id": record["id"],
                    "file_key": file_record.key,
                },
            )
            raise

    def _process(self, draft, record, uow=None):
        # Enable media files always since we need it for state management
        record.media_files.enabled = True
        if not record.media_files.bucket:
            record.media_files.create_bucket()

        # Unlock the media files bucket, we need to add/modify files
        with self.unlocked_bucket(record.media_files):
            # Cleanup unused media files i.e. for deleted/updated files
            self._cleanup(record)

            # Use a copy of the files lists, since we might be modifying them
            record_files = list(record.files.values())

            for file_record in record_files:
                self._process_file(file_record, record, uow)

        # There was no file added in the end
        if not len(record.media_files.entries):
            record.media_files.enabled = False
