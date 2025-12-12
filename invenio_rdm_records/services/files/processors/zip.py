# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CESNET i.a.l.e.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""ZIP file processor that builds and caches a table of contents for efficient extraction."""

import base64
import json
import mimetypes
import os
import zipfile
from io import BytesIO
from pathlib import PurePosixPath

from flask import current_app
from invenio_db import db
from invenio_records_resources.services.files.processors.base import FileProcessor


class ZipProcessor(FileProcessor):
    """
    Processor for ZIP files that builds and caches a hierarchical table of contents.

    When a ZIP file is uploaded, this processor:
    1. Reads the ZIP's central directory to extract metadata
    2. Builds a hierarchical tree structure of all files and directories
    3. Records the byte range of the central directory for efficient later access
    4. Stores this information as a ".listing" file alongside the original ZIP

    This preprocessing step enables efficient extraction later without re-reading
    the entire ZIP file.
    """

    def can_process(self, file_record):
        """Determine if this processor can process a given file record."""
        return (
            os.path.splitext(file_record.key)[-1].lower()
            in current_app.config["RDM_CONTAINER_ZIP_FORMATS"]
        )

    def process(self, file_record):
        """Process the uploaded ZIP file by building and caching its table of contents."""
        record = file_record.record

        if record.media_files.enabled is False:
            record.media_files.enabled = True

            if not record.media_files.bucket:
                record.media_files.create_bucket()
            # The process is called asynchronously.
            # We do not know if we are inside a transaction in which the record would be committed later.
            # That why we need to commit here to ensure the bucket is created before adding new files to it.
            record.commit()

        listing_file = record.media_files.get(f"{file_record.key}.listing")

        if listing_file:
            return  # already processed

        toc = self._build_zip_toc(file_record)
        toc_bytes = json.dumps(toc, indent=2).encode("utf-8")
        toc_stream = BytesIO(toc_bytes)

        # add listing here
        try:
            with db.session.begin_nested():
                # Check and create a media file if it doesn't exist
                if listing_file is None:
                    listing_file = record.media_files.create(
                        f"{file_record.key}.listing",
                        stream=toc_stream,
                    )

                record.media_files.commit(f"{file_record.key}.listing")

        except Exception:
            # Nested transaction for current file is rolled back
            current_app.logger.exception(
                "Failed to initialize listing",
                extra={
                    "record_id": file_record["id"],
                    "file_key": file_record.key,
                },
            )

    def _build_zip_toc(self, file_record, max_entries=None):
        """Construct a hierarchical table of contents from the ZIP file.

        This method reads the ZIP's central directory and builds a tree structure
        containing:
        - Hierarchical directory structure
        - File metadata (size, compressed size, CRC32, MIME type)
        - Byte range of the central directory (for efficient later access)

        It is possible to truncate the listing if max_entries is set.

        Example structure:
        {
            "children": {
                "test_zip":
                {
                    "key": "test_zip",
                    "id": "test_zip",
                    "type": "folder",
                    "children": {
                        "test1.txt":
                            {
                                "key": "test1.txt",
                                "type": "file",
                                "id": "test_zip/test1.txt",
                                "size": 12,
                                "compressed_size": 14,
                                "mime_type": "text/plain",
                                "crc": 2962613731,
                            }
                    },
            }
            },
            "total": 1,
            "truncated": False,
        }
        """

        def insert_container_item(root, parts, info, current_path=""):
            """
            Insert a container item into the hierarchical tree.

            This function builds a directory tree by processing path
            components. For example, "dir1/dir2/file.txt" will create:
            dir1 -> dir2 -> file.txt
            """
            toc_pos = root
            current_path = ""
            for part in parts[:-1]:
                current_path = os.path.join(current_path, part)
                children = toc_pos.setdefault("children", {})
                if part not in children:
                    children[part] = {
                        "key": part,
                        "id": current_path,
                        "type": "folder",
                        "children": {},
                    }

                toc_pos = children[part]

            toc_pos["children"][parts[-1]] = {
                "key": parts[-1],
                "id": "/".join(parts),
                "type": "file",
                "size": info.file_size,
                "compressed_size": info.compress_size,
                "mime_type": mimetypes.guess_type(parts[-1])[0]
                or "application/octet-stream",
                "crc": info.CRC,
            }

        toc_root = {"children": {}}
        total_entries = 0
        truncated = False

        # Open the ZIP file and wrap it in RecordingStream to track byte ranges
        with file_record.open_stream("rb") as fp:
            with RecordingStream.open(fp) as recorded_stream:
                with zipfile.ZipFile(recorded_stream) as zf:
                    # Iterate through all entries in the ZIP's central directory
                    # Recording Stream will capture byte range accessed
                    for info in zf.infolist():
                        if info.is_dir():
                            continue
                        parts = list(PurePosixPath(info.filename).parts)
                        insert_container_item(toc_root, parts, info)
                        total_entries += 1
                        if max_entries and total_entries >= max_entries:
                            truncated = True
                            break

                return {
                    **toc_root,
                    "total": total_entries,
                    "truncated": truncated,
                    "toc": recorded_stream.toc(),  # byte range of central directory
                }


class RecordingStream:
    """A wrapper around a file stream that records the byte ranges accessed."""

    def __init__(self, fp):
        """Initialize the RecordingStream with the given file-like object."""
        self.fp = fp
        self.min_offset = None
        self.max_offset = None

    @staticmethod
    def open(fp):
        """Open a RecordingStream around the given file-like object."""
        return RecordingStream(fp)

    def __enter__(self):
        """Context manager enter."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit."""
        pass

    def seek(self, offset, whence=os.SEEK_SET):
        """Seek to a position and record the byte offset.

        This method tracks the minimum and maximum byte offsets accessed.
        """
        self.fp.seek(offset, whence)

        actual_pos = self.fp.tell()
        if self.min_offset is None or actual_pos < self.min_offset:
            self.min_offset = actual_pos

        if self.max_offset is None or actual_pos > self.max_offset:
            self.max_offset = actual_pos

    def tell(self):
        """Delegate tell to the underlying stream."""
        return self.fp.tell()

    def read(self, size=-1):
        """Delegate read to the underlying stream."""
        return self.fp.read(size)

    def toc(self):
        """Return the recorded byte range as a table of contents entry."""
        if self.min_offset is None:
            return {"content": base64.b64encode(b""), "min_offset": None}

        self.fp.seek(self.min_offset)
        return {
            "content": base64.b64encode(self.fp.read()).decode("utf-8"),
            "min_offset": self.min_offset,
            "max_offset": self.max_offset,
        }
