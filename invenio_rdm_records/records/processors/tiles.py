from flask import current_app
from invenio_records_resources.services.uow import TaskOp

from invenio_rdm_records.records.processors.base import RecordFilesProcessor
from invenio_rdm_records.services.iiif.storage import (  # TODO Refactor to a singleton
    tiles_storage,
)
from invenio_rdm_records.services.iiif.tasks import generate_tiles


class TilesProcessor(RecordFilesProcessor):

    @property
    def valid_exts(self):
        return current_app.config.get(
            "IIIF_VALID_EXTENSIONS", ["tiff", "jpeg", "png", "jpg"]
        )

    def _can_process(self, draft, record):
        return current_app.config.get("IIIF_GENERATE_TILES", False) and bool(
            set(self.valid_exts).intersection(record.files.exts)
        )

    def _can_process_file(self, file_record, draft, record):
        if file_record.file.ext in self.valid_exts:
            return True

    def _process(self, draft, record, uow):

        # Enable media files always since we need it for state management
        record.media_files.enabled = True
        # record["media_files"]["enabled"] = True

        # Unlock the media files bucket, we need to add/modify files
        record.media_files.unlock()  # TODO where to lock and unlock? is this ok?

        # Cleanup unused media files i.e. for deleted/updated files
        media_files = list(record.media_files.entries.keys())
        for fname in media_files:
            if fname.endswith(".ptif") and record.files.get(fname[:-5]) is None:
                tiles_storage.delete(record, fname)
                record.media_files.delete(fname)

        # Change file directory based on any access updates, we try and check if there are any files with the opposite
        # access and move them.
        tiles_storage.update_access(record)

        # Look through files and call the task for generating tiles
        for fname, file_record in record.files.items():
            if not self._can_process_file(file_record, draft, record):
                continue

            status_file = record.media_files.get(f"{file_record.key}.ptif")
            if (
                status_file
                and status_file.processor["status"] in ["finished"]
                and status_file.processor["file_id"] == str(file_record.file.id)
            ):
                status_file.file.file_model.uri = str(
                    tiles_storage._get_file_path(record, file_record.key)
                )
                continue

            # Check and create a media file if it doesn't exist
            if status_file is None:
                status_file = record.media_files.create(
                    f"{file_record.key}.ptif",
                    obj={
                        "file": {
                            "uri": str(
                                tiles_storage._get_file_path(record, file_record.key)
                            ),  # TODO Is there a "None Path" to point to? so we can always update this in the task
                            "storage_class": "R",
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
                "file_id": str(file_record.file.id),
            }
            status_file.access = {"hidden": True}
            status_file.commit()
            record.media_files.commit(f"{file_record.key}.ptif")

            uow.register(
                TaskOp(
                    generate_tiles,
                    record_id=record["id"],
                    file_key=file_record.key,
                )
            )

        # Lock the media files bucket
        record.media_files.lock()
