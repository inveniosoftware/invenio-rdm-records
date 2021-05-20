# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Handler functions for Invenio-RDM-Records."""


import tempfile

import pkg_resources
from flask import g

try:
    pkg_resources.get_distribution('wand')
    from wand.image import Image
    HAS_IMAGEMAGICK = True
except pkg_resources.DistributionNotFound:
    # Python module not installed
    HAS_IMAGEMAGICK = False
except ImportError:
    # ImageMagick notinstalled
    HAS_IMAGEMAGICK = False

from ..proxies import current_rdm_records


def image_opener(key):
    """Handler to locate file based on key.

    .. note::
        If the file is a PDF then only the first page will be
        returned as an image.

    :param key: A key encoded in the format "<recid>:<filename>".
    :returns: A file-like object.
    """
    key_parts = key.split(":")
    assert len(key_parts) == 2

    recid = key_parts[0]
    filename = key_parts[1]
    identity = g.identity
    service = current_rdm_records.records_service
    try:
        file_item = service.files.get_file_content(recid, filename, identity)
    except KeyError:
        return None  # FIXME: throw custom exception `FileNotFound`?

    fp = file_item.get_stream('rb')

    # If ImageMagick with Wand is installed, extract first page
    # for PDF/text.
    pages_mimetypes = ['application/pdf', 'text/plain']
    if HAS_IMAGEMAGICK and file_item.data["mimetype"] in pages_mimetypes:
        first_page = Image(Image(fp).sequence[0])
        tempfile_ = tempfile.TemporaryFile()
        with first_page.convert(format='png') as converted:
            converted.save(file=tempfile_)
        return tempfile_

    return fp
