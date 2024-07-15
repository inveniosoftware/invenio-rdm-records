# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tiles processor."""

from contextlib import contextmanager

from flask import current_app
from invenio_db import db
from invenio_records_resources.services.uow import TaskOp

from invenio_rdm_records.records.processors.base import RecordFilesProcessor
from invenio_rdm_records.services.iiif.storage import tiles_storage
from invenio_rdm_records.services.iiif.tasks import cleanup_tiles_file, generate_tiles


class TilesProcessor(RecordFilesProcessor):
    """Processor to generate pyramidal tifs."""

    @property
    def valid_exts(self) -> list:
        """Return valid extensions for tiles generation from config/default."""
        return current_app.config.get(
            "IIIF_TILES_VALID_EXTENSIONS", ["tiff", "pdf", "jpeg", "png"]
        )

    def _can_process(self, draft, record) -> bool:
        """Checks to determine if to process the record."""
        for file_type in ["media_files", "files"]:
            files = getattr(record, file_type)
            if (
                # Check if tiles generation is enabled...
                current_app.config.get("IIIF_TILES_GENERATION_ENABLED", False)
                and (
                    # ...has convertible files (i.e. images)
                    bool(set(self.valid_exts).intersection(files.exts))
                    # ...or has already converted files
                    or (
                        record.media_files.enabled and "ptif" in record.media_files.exts
                    )
                )
            ):
                return True
        return False

    def _can_process_file(self, file_record, draft, record) -> bool:
        """Checks to determine if to process the record."""
        return file_record.file.ext in self.valid_exts

    @contextmanager
    def unlocked_bucket(self, files):
        """Context manager to auto lock files."""
        files.unlock()
        yield
        files.lock()

    def _cleanup(self, record, uow=None):
        """Cleans up unused media files and ptifs."""
        media_files = list(record.media_files.entries.keys())
        for fname in media_files:
            if fname.endswith(".ptif") and (
                record.access.protection.files == "restricted"
                or (
                    record.files.get(fname[:-5]) is None
                    and record.media_files.get(fname[:-5]) is None
                )
            ):
                deletion_status = tiles_storage.delete(record, fname[: -len(".ptif")])
                if deletion_status:
                    mf = record.media_files.get(fname)
                    fi = mf.file.file_model
                    record.media_files.delete(
                        fname, softdelete_obj=False, remove_rf=True
                    )
                    fi.delete()
                else:
                    # Send a task to make sure we retry in case of a transient error
                    uow.register(
                        TaskOp(
                            cleanup_tiles_file,
                            record_id=record["id"],
                            tile_file_key=fname,
                        )
                    )

    def _process_file(self, file_record, draft, record, file_type, uow=None):
        """Process a file record to kickoff pyramidal tiff generation."""
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
                                ),
                                "storage_class": "L",
                                "size": None,
                                "checksum": None,
                            }
                        },
                    )

                status_file.processor = {
                    "type": "image-tiles",
                    "status": "init",
                    "source_file_id": str(file_record.file.id),
                    "props": {},
                }
                status_file.access.hidden = True
                status_file.commit()
                record.media_files.commit(f"{file_record.key}.ptif")
            uow.register(
                TaskOp(
                    generate_tiles,
                    record_id=record["id"],
                    file_key=file_record.key,
                    file_type=file_type,
                )
            )
        except Exception:
            # Nested transaction for current file is rolled back
            current_app.logger.exception(
                "Failed to initialize tiles generation.",
                extra={
                    "record_id": record["id"],
                    "file_key": file_record.key,
                },
            )

    def _process(self, draft, record, uow):
        """Process the whole record to generate pyramidal tifs for valid files."""
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

            # Use a copy of the files lists, since we might be modifying them
            record_files = list(record.files.values())
            record_media_files = list(record.media_files.values())

            for file_record in record_files:
                self._process_file(file_record, draft, record, "files", uow)
            for file_record in record_media_files:
                self._process_file(file_record, draft, record, "media_files", uow)

        if not len(record.media_files.entries):
            record.media_files.enabled = False
