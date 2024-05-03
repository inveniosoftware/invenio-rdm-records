from contextlib import contextmanager

from flask import current_app
from invenio_db import db
from invenio_records_resources.services.uow import TaskOp

from invenio_rdm_records.records.processors.base import RecordFilesProcessor
from invenio_rdm_records.services.iiif.storage import tiles_storage
from invenio_rdm_records.services.iiif.tasks import generate_tiles


class TilesProcessor(RecordFilesProcessor):

    @property
    def valid_exts(self) -> list:
        """Return valid extenstions for tiles generation from config/default."""
        return current_app.config.get(
            "IIIF_VALID_EXTENSIONS", ["tiff", "jpeg", "png", "jpg"]
        )

    def _can_process(self, draft, record) -> bool:
        return current_app.config.get("IIIF_GENERATE_TILES", False) and (
            bool(set(self.valid_exts).intersection(record.files.exts))
            or (record.media_files.enabled and "ptif" in record.media_files.exts)
        )

    def _can_process_file(self, file_record, draft, record) -> bool:
        return file_record.file.ext in self.valid_exts

    @contextmanager
    def unlocked_bucket(self, files):
        files.unlock()
        yield
        files.lock()

    def _cleanup(self, record):
        media_files = list(record.media_files.entries.keys())
        for fname in media_files:
            if fname.endswith(".ptif") and (
                record.access.protection.files == "restricted"
                or record.files.get(fname[:-5]) is None
            ):
                deletion_status = tiles_storage.delete(record, fname[:-5])
                if deletion_status:
                    mf = record.media_files.get(fname)
                    fi = mf.file.file_model
                    record.media_files.delete(
                        fname, softdelete_obj=False, remove_rf=True
                    )
                    fi.delete()

    def _process_file(self, file_record, draft, record, uow=None):
        if not self._can_process_file(file_record, draft, record):
            return

        status_file = record.media_files.get(f"{file_record.key}.ptif")

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
                    status_file = record.media_files.create(
                        f"{file_record.key}.ptif",
                        obj={
                            "file": {
                                "uri": str(
                                    tiles_storage._get_file_path(
                                        record, file_record.key
                                    )
                                ),  # TODO Is there a "None Path" to point to? so we can always update this in the task
                                "storage_class": "L",
                                "size": None,
                                "checksum": None,
                            }
                        },
                    )

                # Doing this everytime makes sure that the access folder is correct on media file.
                status_file.processor = {
                    "type": "image-tiles",
                    "status": "init",
                    "props": {},
                    "source_file_id": str(file_record.file.id),
                }
                status_file.access.hidden = True
                status_file.commit()
                record.media_files.commit(f"{file_record.key}.ptif")
            uow.register(
                TaskOp(
                    generate_tiles,
                    record_id=record["id"],
                    file_key=file_record.key,
                )
            )
        except Exception:
            pass

    def _process(self, draft, record, uow):
        if record.access.protection.files != "public" and not (
            record.media_files.enabled and "ptif" in record.media_files.exts
        ):
            # There is no cleanup/generation to do
            return

        # Enable media files always since we need it for state management
        record.media_files.enabled = True
        if not record.media_files.bucket:
            record.media_files.create_bucket()

        # Unlock the media files bucket, we need to add/modify files
        with self.unlocked_bucket(record.media_files):
            # Cleanup unused media files i.e. for deleted/updated files
            self._cleanup(record)

            if record.access.protection.files == "restricted":
                if not len(record.media_files.entries):
                    record.media_files.enabled = False
                return

            # Look through files and call the task for generating tiles
            for fname, file_record in record.files.items():
                self._process_file(file_record, draft, record, uow)

        if not len(record.media_files.entries):
            record.media_files.enabled = False
