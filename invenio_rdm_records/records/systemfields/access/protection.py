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

    @property
    def record(self):
        """Get the record's overall protection level."""
        return self._record

    @record.setter
    def record(self, value):
        """Set the record's overall protection level."""
        if not self._validate_protection_level(value):
            raise ValueError(
                "unknown record protection level: {}".format(value)
            )

        if value == "restricted":
            self._files = "restricted"

        self._record = value

    @property
    def files(self):
        """Get the record's files protection level."""
        return self._files

    @files.setter
    def files(self, value):
        """Set the record's files protection level."""
        if not self._validate_protection_level(value):
            raise ValueError(
                "unknown files protection level: {}".format(value)
            )

        if self.record == "restricted":
            self._files = "restricted"
        else:
            self._files = value

    def set(self, record, files=None):
        """Set the protection level for record and files."""
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
