# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Protection class for the access system field."""


class Protection:
    """Protection class for the access system field."""

    def __init__(self, record="public", files="public"):
        """Create a new protection levels instance."""
        self.set(record=record, files=files)

    def _validate_protection_level(self, level):
        return level in ("public", "restricted")

    def set(self, record, files=None):
        """Set the protection level for record and files."""
        if not self._validate_protection_level(record):
            raise ValueError(
                "unknown record protection level: {}".format(record)
            )
        elif files is not None and not self._validate_protection_level(files):
            raise ValueError(
                "unknown files protection level: {}".format(files)
            )

        self.record = record
        if files is not None:
            self.files = files

    def __get__(self):
        """Get the protection level of the record and its files."""
        return {
            "record": self.record,
            "files": self.files,
        }

    def __repr__(self):
        """Return repr(self)."""
        return "<{} (record: {}, files: {})>".format(
            type(self).__name__,
            self.record,
            self.files,
        )
