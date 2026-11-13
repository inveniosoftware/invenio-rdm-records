# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Tests for the IIIF service image rendering."""

import io

import pytest
from PIL import Image

from invenio_rdm_records.services.iiif.service import (
    HAS_IMAGEMAGICK,
    HAS_VIPS,
    IIIFService,
    _flatten_on_white,
)

# A single-page PDF that draws nothing, so the page is rendered transparent.
MINIMAL_PDF = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >> endobj
trailer << /Root 1 0 R >>
%%EOF
"""


class MockFile:
    """Minimal stand-in for the file object passed to ``_open_image``."""

    def __init__(self, content, mimetype="application/pdf"):
        """Constructor."""
        self.data = {"mimetype": mimetype}
        self._content = content

    def get_stream(self, mode):
        """Return a fresh stream over the file content."""
        assert mode == "rb"
        return io.BytesIO(self._content)


def _can_render_pdf():
    """Return whether a PDF page can actually be rasterised here."""
    if not (HAS_VIPS or HAS_IMAGEMAGICK):
        return False

    try:
        Image.open(IIIFService._open_image(None, MockFile(MINIMAL_PDF)))
    except Exception:
        return False

    return True


HAS_PDF_RENDERER = pytest.mark.skipif(
    not _can_render_pdf(),
    reason="No working PDF renderer (PyVIPS/ImageMagick with a PDF delegate)",
)


def _png_bytes(image):
    """Return the PNG encoding of the given image."""
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()


def test_flatten_on_white_draws_transparency_on_white():
    """Transparent areas become white while drawn content is kept."""
    image = Image.new("RGBA", (4, 4), (255, 0, 0, 255))
    image.paste((0, 0, 0, 0), (0, 0, 2, 4))
    buffer = io.BytesIO(_png_bytes(image))

    flattened = Image.open(_flatten_on_white(buffer))

    assert flattened.mode == "RGB"
    assert flattened.getpixel((0, 0)) == (255, 255, 255)
    assert flattened.getpixel((3, 0)) == (255, 0, 0)


def test_flatten_on_white_keeps_undecodable_input():
    """Data that is not an image is returned as it was received."""
    buffer = io.BytesIO(b"not an image")
    buffer.seek(0)

    assert _flatten_on_white(buffer) is buffer
    assert buffer.tell() == 0


@HAS_PDF_RENDERER
def test_open_image_flattens_transparent_pdf_pages():
    """Transparent PDF pages are rendered on a white background."""
    page = Image.open(IIIFService._open_image(None, MockFile(MINIMAL_PDF)))

    assert page.mode == "RGB"
    assert page.getpixel((0, 0)) == (255, 255, 255)


def test_open_image_leaves_other_files_untouched():
    """Files that IIIF does not render are streamed as they are."""
    content = _png_bytes(Image.new("RGBA", (4, 4), (0, 0, 0, 0)))

    data = IIIFService._open_image(None, MockFile(content, mimetype="image/png"))

    assert data.read() == content
