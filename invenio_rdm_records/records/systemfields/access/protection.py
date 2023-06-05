# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Protection class for the access system field."""

from enum import Enum


class Visibility(Enum):
    """Enum for the available visibility settings of a record's metadata and files."""

    PUBLIC = "public"
    RESTRICTED = "restricted"


class Protection:
    """Protection class for the access system field."""

    def __init__(self, record="public", files="public"):
        """Create a new protection levels instance."""
        self._record, self._files = Visibility.PUBLIC, Visibility.PUBLIC
        self.set(record=record or Visibility.PUBLIC, files=files or Visibility.PUBLIC)

    @property
    def record(self):
        """Get the record's overall protection level."""
        return self._record.value

    @record.setter
    def record(self, value):
        """Set the record's overall protection level."""
        try:
            new_visibility = Visibility(value)
            if new_visibility == Visibility.RESTRICTED:
                self.files = new_visibility

            self._record = new_visibility

        except ValueError:
            raise ValueError(f"unknown record protection level: {value}")

    @property
    def files(self):
        """Get the record's files protection level."""
        return self._files.value

    @files.setter
    def files(self, value):
        """Set the record's files protection level."""
        try:
            new_visibility = Visibility(value)

            if self._record == Visibility.RESTRICTED:
                self._files = Visibility.RESTRICTED
            else:
                self._files = new_visibility

        except ValueError:
            raise ValueError("unknown files protection level: {}".format(value))

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

    def __eq__(self, other):
        """Compare protection objects."""
        if type(self) != type(other):
            return False

        return self.record == other.record and self.files == other.files

    def __repr__(self):
        """Return repr(self)."""
        return "<{} (record: {}, files: {})>".format(
            type(self).__name__,
            self.record,
            self.files,
        )
