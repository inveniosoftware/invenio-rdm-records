# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CESNET i.a.l.e.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Zip file extractor/listing using cached TOC for efficient extraction."""

import base64
import json
import os
import zipfile
from pathlib import PurePosixPath

from flask import Response, current_app, stream_with_context
from invenio_records_resources.services.files.extractors.base import FileExtractor
from zipstream import ZIP_DEFLATED, ZipStream

from .opened_container import OpenedContainerItem
from .reply_stream import ReplyStream


class StreamedZipContainerItem:
    """Represents a file or directory that can be streamed from a ZIP container.

    This class handles streaming of both individual files and entire directories:
    - For files: Streams the decompressed content directly
    - For directories: Creates a new ZIP on-the-fly containing all files in that directory
    """

    def __init__(
        self,
        file_record,
        container_item_metadata,
        header_pos=0,
        header=b"",
        file_size=0,
    ):
        """Initialize the StreamedZipContainerItem."""
        self.file_record = file_record
        self.container_item_metadata = container_item_metadata
        self.header_pos = header_pos
        self.header = header
        self.file_size = file_size

    def send_file(self):
        """
        Generate a Flask Response that streams the file or directory.

        This method returns different responses depending on the container item:
        - For files: Streams the decompressed file content
        - For directories: Streams a newly created ZIP containing all files
        """
        # Check if this is a directory
        if self.container_item_metadata.get("type") == "folder":
            return self._send_folder()
        else:
            return self._send_item()

    def _send_item(self):
        """Stream a single file from the ZIP container."""
        # Single file extraction
        mime = self.container_item_metadata.get("mime_type", "application/octet-stream")
        filename = self.container_item_metadata["id"]

        # Open the storage stream now (while request/session still active)
        # otherwise Flask sends HTTP headers but streaming later would fail
        # due to closed SQL session or request context.
        cm = self.file_record.open_stream("rb")
        fp = cm.__enter__()  # get the real file-like object and keep it open

        # For files, stream the single file
        @stream_with_context
        def generate():
            """Generator that streams the file content in chunks."""
            try:
                # Wrap the actual file object in ReplyStream
                with ReplyStream(
                    fp,
                    self.header_pos,
                    self.header,
                    self.file_size,
                ) as reply_stream:
                    # Open as a ZipFile using your wrapper
                    with zipfile.ZipFile(reply_stream) as zf:
                        with zf.open(filename, "r") as extracted:
                            # Stream the extracted file in chunks
                            chunk_size = 64 * 1024
                            while True:
                                chunk = extracted.read(chunk_size)
                                if not chunk:
                                    break

                                yield chunk
            finally:
                # ensure we close the underlying storage stream
                try:
                    cm.__exit__(None, None, None)
                except Exception:
                    pass

        return Response(
            generate(),
            mimetype=mime,
            headers={
                "Content-Disposition": f'attachment; filename="{self.container_item_metadata["key"]}"',
                "Content-Length": str(self.container_item_metadata["size"]),
            },
        )

    def _send_folder(self):
        """
        Stream an entire directory as a newly created ZIP file.

        This method creates a new ZIP file on-the-fly containing all files from
        the requested directory. It uses zipstream-ng library to avoid buffering the
        entire ZIP in memory.

        """
        dir_name = self.container_item_metadata["key"]
        zip_filename = f"{dir_name}.zip"

        # Open the storage stream now (while request/session still active)
        # otherwise Flask sends HTTP headers but streaming later would fail
        # due to closed SQL session or request context.
        cm = self.file_record.open_stream("rb")
        fp = cm.__enter__()  # get the real file-like object and keep it open

        @stream_with_context
        def generate_zip():
            """Generator that created ZIP file on the fly."""
            # Create ZipStream object
            zs = ZipStream(compress_type=ZIP_DEFLATED)
            try:
                with ReplyStream(
                    fp,
                    self.header_pos,
                    self.header,
                    self.file_size,
                ) as reply_stream:
                    with zipfile.ZipFile(reply_stream, "r") as source_zip:
                        # Collect all files in this directory
                        files_to_add = self._collect_files(self.container_item_metadata)

                        for file_info in files_to_add:
                            full_path = file_info["id"]

                            # Calculate relative path within the directory
                            relative_path = full_path
                            if full_path.startswith(
                                self.container_item_metadata["id"] + "/"
                            ):
                                relative_path = full_path[
                                    len(self.container_item_metadata["id"]) + 1 :
                                ]

                            # Stream file content from source
                            def make_generator(zip_ref, path):
                                def generator():
                                    with zip_ref.open(path, "r") as f:
                                        chunk_size = 64 * 1024
                                        while True:
                                            chunk = f.read(chunk_size)
                                            if not chunk:
                                                break
                                            yield chunk

                                return generator()

                            zs.add(
                                data=make_generator(source_zip, full_path),
                                arcname=relative_path,  # under which name it will be stored in the zip
                            )

                        # Stream the generated ZIP file
                        yield from zs
            finally:
                # ensure we close the underlying storage stream
                try:
                    cm.__exit__(None, None, None)
                except Exception:
                    pass

        # Cant calculate size here. Realistically zipstream can calculate size, but there will be no compression according to the docs
        return Response(
            generate_zip(),
            mimetype="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
        )

    def _collect_files(self, container_item_metadata):
        """Recursively collect all files in a directory container item."""
        files = []

        if container_item_metadata.get("type") == "file":
            return [container_item_metadata]

        for sub_item in container_item_metadata.get("children", {}).values():
            if sub_item.get("type") == "file":
                files.append(sub_item)
            elif sub_item.get("type") == "folder":
                files.extend(self._collect_files(sub_item))

        return files


class ZipExtractor(FileExtractor):
    """
    Extractor for ZIP files that uses the pre-built table of contents for efficient extraction.

    This extractor leverages the cached TOC created by ZipProcessor to:
    - Quickly locate files without scanning the entire ZIP
    - Stream individual files without loading them fully into memory
    - Create directory ZIPs on-the-fly without buffering in memory
    """

    def can_process(self, file_record):
        """Determine if this extractor can process a given file record."""
        return (
            os.path.splitext(file_record.key)[-1].lower()
            in current_app.config["RDM_CONTAINER_ZIP_FORMATS"]
        )

    @staticmethod
    def _find_container_item(container_item_metadata, path_parts):
        """Recursively find container item in TOC based on path parts."""
        if not path_parts:
            return None

        key = path_parts[0]
        for sub_item in container_item_metadata:
            if sub_item["key"] == key:
                if len(path_parts) == 1:
                    return sub_item
                elif sub_item.get("children"):
                    return ZipExtractor._find_container_item(
                        sub_item["children"].values(), path_parts[1:]
                    )
        return None

    def list(self, file_record):
        """Return the cached table of contents for the ZIP file."""
        listing_file = file_record.record.media_files.get(f"{file_record.key}.listing")

        if listing_file:
            with listing_file.file.storage().open("rb") as f:
                listing = json.load(f)
                # Remove the internal TOC data and byte ranges as it's not useful for clients
                listing.pop("toc", None)
                return listing
        return {}

    def _get_container_item_metadata_and_toc(self, file_record, path):
        """Load listing and return (item metadata, toc).

        Raises FileNotFoundError if listing or metadata is not found.
        """
        parts = list(PurePosixPath(path).parts)

        # Load the cached table of contents
        listing_file = file_record.record.media_files.get(f"{file_record.key}.listing")
        if not listing_file:
            raise FileNotFoundError(f"Listing file not found in {file_record.key}.")

        with listing_file.file.storage().open("rb") as f:
            listing = json.load(f)

        # Find the requested container item in the TOC
        container_item_metadata = self._find_container_item(
            listing.get("children", {}).values(), parts
        )
        toc = listing.get("toc", {})

        if not container_item_metadata:
            raise FileNotFoundError(f"Path '{path}' not found in listing.")

        return container_item_metadata, toc

    def extract(self, file_record, path):
        """Extract a specific file or directory from the file record."""
        # Load container item from listing and zip toc
        container_item_metadata, toc = self._get_container_item_metadata_and_toc(
            file_record, path
        )
        # Create a streamed container item that can generate the response
        return StreamedZipContainerItem(
            file_record,
            container_item_metadata,
            toc.get("min_offset", 0),
            base64.b64decode(toc.get("content", b"")),
            toc.get("max_offset", 0),
        )

    def open(self, file_record, path):
        """Open a specific file from the file record.

        Return a readable stream that remains open until the caller closes it.
        """
        # Load container item from listing and zip toc
        container_item_metadata, toc = self._get_container_item_metadata_and_toc(
            file_record, path
        )

        # prepare cached header and offsets
        header_pos = toc.get("min_offset", 0)
        header_b64 = toc.get("content", "") or ""
        header = base64.b64decode(header_b64) if header_b64 else b""
        file_size = toc.get("max_offset", 0)

        # file_record.open_stream() returns a context manager. We need the
        # actual underlying file-like object that supports seek/read.
        # Enter the context manually and keep the context manager so we can
        # close it later when the returned object is closed.
        # Otherwise flask already send response but we need the stream open
        fp_cm = file_record.open_stream("rb")
        fp = fp_cm.__enter__()

        # Wrap in our ReplyStream which provides correct seeking/read behavior
        reply_stream = ReplyStream(fp, header_pos, header, file_size)

        # Create ZipFile on top of reply_stream. Keep references so they
        # remain alive while caller uses the returned object.
        zf = zipfile.ZipFile(reply_stream, "r")
        extracted = zf.open(container_item_metadata["id"], "r")

        # Return the OpenedContainerItem and keep a reference to the context manager
        # so it can be closed when the user closes the returned object.
        return OpenedContainerItem(extracted, zf, reply_stream, fp, fp_cm)
