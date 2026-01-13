# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CESNET i.a.l.e.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""A generic opened container file wrapper to manage lifecycle of extracted files."""

import io


class OpenedContainerItem(io.IOBase):
    """A thin wrapper around an extracted file-like object that keeps the container handle and streams alive.

    This is a generic lifecycle wrapper suitable for any container format.

    The `extracted_container_item` argument is the file-like (readable) object returned by the
    container library when opening a container item (e.g. ZipFile.open()). The `container`
    is the container handle (for example, a ZipFile or TarFile) that must be closed after the
    extracted stream. `reply_stream` is a ReplyStream wrapper with cached headers.
    The `underlying_stream` is the wrapped file-like object (e.g. file_record.open_stream("rb"))
    and is used to read the container contents and should be closed last.
    `underlying_cm` is the context manager returned by the storage's `open_stream` (so we can call __exit__ on close).
    """

    def __init__(
        self,
        extracted_container_item,
        container,
        reply_stream,
        underlying_stream,
        underlying_cm=None,
    ):
        """Initialize the OpenedContainerFile."""
        self._extracted_container_item = extracted_container_item
        self._container = container
        self._reply = reply_stream
        # underlying_stream is the actual file-like object
        self._fp = underlying_stream
        # underlying_cm is the context manager returned by file_record.open_stream
        # (so we can call __exit__ on close). It may be None if the caller
        # provided a raw stream.
        self._fp_cm = underlying_cm

    def readable(self):
        """File is readable."""
        return True

    def writable(self):
        """File is not writable."""
        return False

    def seekable(self):
        """Check if the extracted file is seekable."""
        return hasattr(self._extracted_container_item, "seek")

    def read(self, *args, **kwargs):
        """Delegate read to the underlying extracted file."""
        return self._extracted_container_item.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        """Delegate readline to the underlying extracted file."""
        return self._extracted_container_item.readline(*args, **kwargs)

    def seek(self, *args, **kwargs):
        """Delegate seek to the underlying extracted file."""
        return getattr(self._extracted_container_item, "seek", lambda *a, **k: None)(
            *args, **kwargs
        )

    def tell(self, *args, **kwargs):
        """Delegate tell to the underlying extracted file."""
        return getattr(self._extracted_container_item, "tell", lambda *a, **k: None)(
            *args, **kwargs
        )

    def __iter__(self):
        """Create iterator."""
        return iter(self._extracted_container_item)

    def __next__(self):
        """Get next chunk."""
        return next(self._extracted_container_item)

    def close(self):
        """Close extracted stream, archive object and underlying stream (in that order)."""
        # Close extracted first
        try:
            self._extracted_container_item.close()
        except Exception:
            pass

        # Then close the archive handle
        try:
            if self._container is not None:
                self._container.close()
        except Exception:
            pass

        # Finally close the underlying storage stream
        try:
            if hasattr(self._fp, "close"):
                self._fp.close()
        except Exception:
            pass

        # If we have a context manager, ensure we exit it so resources are properly released.
        try:
            if self._fp_cm is not None:
                self._fp_cm.__exit__(None, None, None)
        except Exception:
            pass

        # Drop references
        self._extracted_container_item = None
        self._container = None
        self._reply = None
        self._fp = None
        self._fp_cm = None

    def __enter__(self):
        """Context manager enter."""
        return self

    def __exit__(self, exc_type, exc, tb):
        """Context manager exit."""
        self.close()

    def __getattr__(self, name):
        """Forward any unknown attribute to the underlying extracted file."""
        return getattr(self._extracted_container_item, name)
