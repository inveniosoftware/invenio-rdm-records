# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2022 Universität Hamburg.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IIIF Service."""

import io
import tempfile

import importlib_metadata as metadata
from flask_iiif.api import IIIFImageAPIWrapper
from invenio_records_resources.services import Service

try:
    metadata.distribution("wand")
    from wand.image import Image

    HAS_IMAGEMAGICK = True
except (metadata.PackageNotFoundError, ImportError):
    # ImageMagick notinstalled
    HAS_IMAGEMAGICK = False

try:
    import pyvips

    HAS_VIPS = True
except ModuleNotFoundError:
    # Python module pyvips not installed
    HAS_VIPS = False
except OSError:
    # Underlying library libvips not installed
    HAS_VIPS = False


class IIIFService(Service):
    """IIIF service.

    This is just a thin layer on top of Flask-IIIF API.
    """

    def __init__(self, config, records_service):
        """Constructor."""
        super().__init__(config)
        self._records_service = records_service

    def _iiif_uuid(self, uuid):
        """Split the uuid content.

        We assume the uuid is build as ``<record|draft>:<pid_value>``.
        """
        type_, id_ = uuid.split(":", 1)
        return type_, id_

    def _iiif_image_uuid(self, uuid):
        """Split the uuid content.

        We assume the uuid is build as ``<record|draft>:<pid_value>:<key>``.
        """
        type_, id_, key = uuid.split(":", 2)
        return type_, id_, key

    def file_service(self, type_):
        """Get the correct instance of the file service, draft vs record."""
        return (
            self._records_service.files
            if type_ == "record"
            else self._records_service.draft_files
        )

    def read_record(self, identity, uuid):
        """Read the correct version of the record and its files."""
        type_, id_ = self._iiif_uuid(uuid)
        read = (
            self._records_service.read
            if type_ == "record"
            else self._records_service.read_draft
        )
        return read(identity=identity, id_=id_)

    def _open_image(self, file_):
        fp = file_.get_stream("rb")
        # If the file is not a PDF or text, return the file
        if file_.data["mimetype"] not in {"application/pdf", "text/plain"}:
            return fp

        # If Wand (ImageMagick) or PyVIPS is installed, extract the first page
        if HAS_VIPS:  # prefer PyVIPS since it doesn't load the whole file in memory

            def _seek_handler(offset, whence):
                fp.seek(offset, whence)
                return fp.tell()

            source = pyvips.SourceCustom()
            source.on_read(fp.read)
            source.on_seek(_seek_handler)

            # PyVIPS returns by default the first page of the PDF
            first_page = pyvips.Image.new_from_source(source, "", access="sequential")
            # Convert to memory to be able to return a file-like object
            first_page_buf = io.BytesIO(first_page.write_to_memory())
            fp.close()
            return first_page_buf
        elif HAS_IMAGEMAGICK:
            first_page = Image(blob=fp)
            first_page_buf = io.BytesIO()
            with first_page.convert(format="png") as converted:
                converted.save(file=first_page_buf)
            first_page_buf.seek(0)
            fp.close()
            return first_page_buf

        return fp

    def get_file(self, identity, uuid, key=None):
        """Get the file for the given ``uuid``.

        If the ``uuid`` has the shape ``<record|draft>:<pid_value>:<key>``, then the
        ``key`` argument is ignored.
        If it is of the shape ``<record|draft>:<pid_value>`` however, the ``key``
        argument is required.
        :raises FileKeyNotFoundError: If the record has no file for the ``key``
        """
        if key:
            type_, id_ = self._iiif_uuid(uuid)
        else:
            type_, id_, key = self._iiif_image_uuid(uuid)

        service = self.file_service(type_)
        # TODO: add cache and check if the metadata is present
        return service.get_file_content(id_=id_, file_key=key, identity=identity)

    def image_api(
        self,
        identity,
        uuid,
        region,
        size,
        rotation,
        quality,
        image_format,
    ):
        """Run the IIIF image API workflow.

        :raises FileKeyNotFoundError: If the record has no file for the ``key``
        """
        # Validate IIIF parameters
        IIIFImageAPIWrapper.validate_api(
            uuid=uuid,
            region=region,
            size=size,
            rotation=rotation,
            quality=quality,
            image_format=image_format,
        )

        type_, id_, key = self._iiif_image_uuid(uuid)
        service = self.file_service(type_)
        # TODO: check cache before this
        file_ = service.get_file_content(id_=id_, file_key=key, identity=identity)
        data = self._open_image(file_)
        # TODO: include image magic for pdf
        image = IIIFImageAPIWrapper.open_image(data)
        image.apply_api(
            region=region,
            size=size,
            rotation=rotation,
            quality=quality,
        )
        # prepare image to be serve
        to_serve = image.serve(image_format=image_format)
        image.close_image()
        return to_serve
