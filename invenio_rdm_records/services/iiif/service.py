# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IIIF Service."""

import tempfile

import importlib_metadata as metadata
from flask_babelex import lazy_gettext as _
from flask_iiif.api import IIIFImageAPIWrapper
from invenio_records_resources.services import Service

try:
    metadata.distribution("wand")
    from wand.image import Image

    HAS_IMAGEMAGICK = True
except (metadata.PackageNotFoundError, ImportError):
    # ImageMagick notinstalled
    HAS_IMAGEMAGICK = False


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
        # Kids, don't do this at home
        # If you find yourself wanting to copy this, ask for help first
        record = read(identity=identity, id_=id_)
        file_service = self.file_service(type_)
        files = file_service.list_files(identity=identity, id_=id_)
        record.files = files
        return record

    def _open_image(self, file_):
        fp = file_.get_stream("rb")
        # If ImageMagick with Wand is installed, extract first page
        # for PDF/text.
        pages_mimetypes = {"application/pdf", "text/plain"}
        if HAS_IMAGEMAGICK and file_.data["mimetype"] in pages_mimetypes:
            first_page = Image(Image(fp).sequence[0])
            tempfile_ = tempfile.TemporaryFile()
            with first_page.convert(format="png") as converted:
                converted.save(file=tempfile_)
            return tempfile_

        return fp

    def get_file(self, identity, uuid, key=None):
        """."""
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
        """Run the IIIF image API workflow."""
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
