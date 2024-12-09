# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IIIF Tiles generation storage."""

from pathlib import Path
from textwrap import wrap
from typing import Union

from flask import current_app

from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.services.iiif.converter import (
    ImageConverter,
    PyVIPSImageConverter,
)


class TilesStorage:
    """Base class for tile storage."""

    def __init__(self, *, converter: Union[ImageConverter, dict]):
        """Constructor."""
        self._converter = converter

    @property
    def converter(self):
        """Get converter."""
        if isinstance(self._converter, dict):
            converter_cls = self._converter["cls"]
            converter_params = self._converter.get("kwargs", {})
            return converter_cls(**converter_params)

        return self._converter

    def save(self, record: RDMRecord, filename: str):
        """Save tiles."""
        pass

    def open(self, record: RDMRecord, filename: str):
        """Open file in read mode."""
        pass

    def delete(self, record: RDMRecord, filename: str):
        """Delete tiles file."""
        pass


class LocalTilesStorage(TilesStorage):
    """Local tile storage implementation."""

    default_converter = {
        "cls": PyVIPSImageConverter,
    }

    def __init__(self, *, base_path: Union[str, None] = None, **kwargs):
        """Constructor."""
        self._base_path = base_path
        kwargs.setdefault("converter", self.default_converter)
        super().__init__(**kwargs)

    @property
    def base_path(self):
        """Return base path from object/config."""
        path = Path(
            self._base_path or current_app.config.get("IIIF_TILES_STORAGE_BASE_PATH")
        )
        if path.is_absolute():
            return path
        # If relative path, resolve against instance path
        return Path(current_app.instance_path) / path

    def _get_dir(self, record: RDMRecord) -> Path:
        """Get directory."""
        recid = record.pid.pid_value

        recid_parts = wrap(recid.ljust(4, "_"), 2)
        start_parts = recid_parts[:2]
        end_parts = recid_parts[2:]
        recid_path = "/".join(start_parts)
        if end_parts:
            recid_path += f"/{''.join(end_parts)}_"
        else:
            recid_path += "/_"

        path_partitions = recid_path.split("/")

        return (
            self.base_path / record.access.protection.files / Path(*path_partitions)
        ).absolute()

    def _get_file_path(self, record: RDMRecord, filename: str) -> Path:
        """Get file path."""
        # Partition record.id into 3 chunks of min. 2 characters (e.g. "12345678" -> ["12", "34", "5678"])
        return (self._get_dir(record) / (filename + ".ptif")).absolute()

    def save(self, record, filename, file_type):
        """Convert and save to ptif."""
        # Get the files
        file_source = getattr(record, file_type)

        # Get the output path and create necessary directories
        outpath = self._get_file_path(record, filename)
        self._get_dir(record).mkdir(parents=True, exist_ok=True)

        # Open the input stream and output stream
        with file_source[filename].open_stream("rb") as fin:
            fout = outpath.open("w+b")
            # Convert the file and log an error if the conversion fails
            if not self.converter.convert(fin, fout):
                current_app.logger.info(f"Image conversion failed {record.id}")
                return False

        return True

    def open(self, record, filename):
        """Open the file in read mode."""
        return self._get_file_path(record, filename).open("rb")

    def update_access(self, record):
        """Move files according to current files access of the record."""
        # NOTE: If we want to move the record from public -> restricted dir, uncomment
        # access = record.access.protection.files
        # directory = str(self._get_dir(record))
        # old_dir = str(directory).replace(
        #     access,
        #     "restricted" if access == "public" else "public",
        # )
        # if os.path.exists(old_dir):
        #     shutil.move(old_dir, directory)
        pass

    def delete(self, record, filename):
        """Delete the ptif."""
        try:
            Path(record.media_files[filename + ".ptif"].file.uri).unlink(
                missing_ok=True
            )
        except Exception:
            current_app.logger.exception(
                "Failed to delete tiles for record.",
                extra={
                    "record_id": record["id"],
                    "filename": filename,
                },
            )
            return False
        return True


tiles_storage = LocalTilesStorage()
