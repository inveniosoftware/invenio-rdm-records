# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IIIF Tiles converter."""

from flask import current_app

try:
    import pyvips

    HAS_VIPS = True
except ModuleNotFoundError:
    # Python module pyvips not installed
    HAS_VIPS = False
except OSError:
    # Underlying library libvips not installed
    HAS_VIPS = False


class ImageConverter:
    """Base class for Image converters."""

    default_params = {}

    def __init__(self, params=None):
        """Constructor."""
        self._params = params

    @property
    def params(self):
        """Get converter parameters."""
        return (
            self._params
            or current_app.config.get("IIIF_TILES_CONVERTER_PARAMS", {})
            or self.default_params
        )

    def convert(self, in_stream, out_stream) -> bool:
        """Convert image."""
        raise NotImplementedError()


class PyVIPSImageConverter(ImageConverter):
    """PyVIPS image converter for pyramidal tifs."""

    default_params = {
        "compression": "jpeg",
        "Q": 90,
        "tile_width": 256,
        "tile_height": 256,
    }

    @staticmethod
    def fp_source(input_file):
        """File-like source generator for pyvips."""

        def read_handler(size):
            return input_file.read(size)

        # seek is optional, but may improve performance by reducing buffering
        def seek_handler(offset, whence):
            input_file.seek(offset, whence)
            return input_file.tell()

        source = pyvips.SourceCustom()
        source.on_read(read_handler)
        source.on_seek(seek_handler)

        return source

    @staticmethod
    def fp_target(output_file):
        """File-like target generator for pyvips."""

        def write_handler(chunk):
            return output_file.write(chunk)

        def read_handler(size):
            return output_file.read(size)

        def seek_handler(offset, whence):
            output_file.seek(offset, whence)
            return output_file.tell()

        def end_handler():
            try:
                output_file.close()
            except IOError:
                return -1
            else:
                return 0

        target = pyvips.TargetCustom()
        target.on_write(write_handler)
        target.on_read(read_handler)
        target.on_seek(seek_handler)
        target.on_end(end_handler)

        return target

    def convert(self, in_stream, out_stream):
        """Convert to ptifs."""
        if not HAS_VIPS:
            return

        try:
            source = self.fp_source(in_stream)
            target = self.fp_target(out_stream)

            image = pyvips.Image.new_from_source(source, "", access="sequential")
            image.tiffsave_target(target, tile=True, pyramid=True, **self.params)
            return True
        except Exception:
            current_app.logger.exception("Image processing with pyvips failed")
            return False
