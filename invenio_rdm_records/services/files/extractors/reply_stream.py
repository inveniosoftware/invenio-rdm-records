# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CESNET i.a.l.e.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""A seekable file-like object that merges a cached header with an underlying stream."""

import os


class ReplyStream:
    """A seekable file-like object that merges a cached header with an underlying stream.

    This class presents a unified seekable interface over a file that is split into
    three logical regions:
    1. Before the cached header (read from underlying stream)
    2. The cached header region (served from memory)
    3. After the cached header (read from underlying stream)

    The cached header acts as a fast in-memory buffer for frequently accessed bytes,
    while the rest of the file is read on-demand from the underlying stream. This is
    particularly useful for archive formats like ZIP that need to seek within headers
    repeatedly, but where the headers have been pre-fetched and cached.

    Attributes:
        self_stream: The underlying file-like object to read from for non-cached regions. For example file_record.open_stream("rb").
        header_pos (int): Byte offset in the file where the cached header begins.
        header (bytes): The cached header bytes stored in memory.
        header_len (int): Length of the cached header in bytes.
        current_pos (int): Current position in the virtual file (0-based).
        file_size (int): Total size of the virtual file in bytes (max offset read).
    """

    def __init__(self, self_stream, header_pos, header, file_size):
        """Initialize a ReplyStream with a cached header region."""
        self.self_stream = self_stream
        self.header_pos = header_pos
        self.header = header
        self.header_len = len(header)
        self.current_pos = 0
        self.file_size = file_size

    def __enter__(self):
        """Context manager enter."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit."""
        pass

    def seekable(self):
        """Return whether the stream is seekable."""
        return True

    def readable(self):
        """Return whether the stream is readable."""
        return True

    def writable(self):
        """Return whether the stream is writable."""
        return False

    def seek(self, offset, whence=os.SEEK_SET):
        """Seek to a position in the stream.

        Use cache when seeking within the cached header region, otherwise seek in the underlying stream.
        """
        match whence:
            case os.SEEK_SET:
                self.current_pos = offset
            case os.SEEK_CUR:
                self.current_pos = self.current_pos + offset
            case os.SEEK_END:
                self.current_pos = self.file_size + offset
            case _:
                raise ValueError("Invalid value for 'whence'.")

        # Only seek in the underlying stream if we're reading outside the cached header region
        if self.current_pos < self.header_pos:
            # Before the cached region - seek in underlying stream
            self.self_stream.seek(self.current_pos, os.SEEK_SET)
        elif self.current_pos >= self.header_pos + self.header_len:
            # After the cached region - seek in underlying stream
            self.self_stream.seek(self.current_pos, os.SEEK_SET)
        # else: within the cached header region, no need to seek in underlying stream

        return self.current_pos

    def read(self, size=-1):
        """Read up to size bytes from the stream.

        Check if the read spans the cached header region and read accordingly.
        """
        if size == -1:
            size = self.file_size - self.current_pos

        if size <= 0:
            return b""

        result = b""
        bytes_to_read = size

        while bytes_to_read > 0:
            # Before cached header
            if self.current_pos < self.header_pos:
                chunk_size = min(bytes_to_read, self.header_pos - self.current_pos)
                chunk = self.self_stream.read(chunk_size)
                result += chunk
                self.current_pos += len(chunk)
                bytes_to_read -= len(chunk)

                if len(chunk) < chunk_size:
                    break

            # Within cached header
            elif self.current_pos < self.header_pos + self.header_len:
                header_offset = self.current_pos - self.header_pos
                chunk_size = min(bytes_to_read, self.header_len - header_offset)
                chunk = self.header[header_offset : header_offset + chunk_size]
                result += chunk
                self.current_pos += len(chunk)
                bytes_to_read -= len(chunk)

            # After cached header
            else:
                chunk = self.self_stream.read(bytes_to_read)
                result += chunk
                self.current_pos += len(chunk)
                bytes_to_read -= len(chunk)

                if len(chunk) == 0:
                    break

        return result

    def tell(self):
        """Return the current position in the stream."""
        return self.current_pos
