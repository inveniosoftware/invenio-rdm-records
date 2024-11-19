# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""System field for managing the record deletion status."""

import enum

from invenio_records.systemfields import SystemField


class RecordDeletionStatusEnum(enum.Enum):
    """Enumeration of a record's possible deletion states."""

    PUBLISHED = "P"
    DELETED = "D"
    MARKED = "X"


class RecordDeletionStatus:
    """The deletion status of the record."""

    def __init__(self, status):
        """Constructor."""
        self.status = status

    @property
    def status(self):
        """Get the deletion status."""
        return self._status.value

    @status.setter
    def status(self, value):
        """Set the deletion status."""
        if value is None:
            self._status = RecordDeletionStatusEnum.PUBLISHED

        elif isinstance(value, str):
            self._status = RecordDeletionStatusEnum(value)

        elif isinstance(value, RecordDeletionStatusEnum):
            self._status = value

        else:
            raise ValueError(f"Invalid value for record deletion status: {value}")

    @property
    def is_deleted(self):
        """Check if the record is deleted."""
        return self._status != RecordDeletionStatusEnum.PUBLISHED

    def __repr__(self):
        """Return repr(self)."""
        return f"<RecordDeletionStatus {self._status.name}: '{self._status.value}'>"

    def __str__(self):
        """Return str(self)."""
        return self.status

    def __eq__(self, other):
        """Check if self and other are equal.

        This allows checking against other instances of the same type, strings,
        and ``RecordDeletionStatusEnum`` values.
        """
        if isinstance(other, type(self)):
            return self.status == other.status

        elif isinstance(other, RecordDeletionStatusEnum):
            return self.status == other.value

        elif isinstance(other, str):
            return self.status == other

        return False


class RecordDeletionStatusField(SystemField):
    """System field for accessing a record's deletion status."""

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the deletion status of the record."""
        if record is None:
            return self  # returns the field itself.

        status = self._get_cache(record) or RecordDeletionStatus(
            record.model.deletion_status
        )
        self._set_cache(record, status)
        return status

    def __set__(self, record, value):
        """Set the deletion status of the record."""
        status = RecordDeletionStatus(value)
        record.model.deletion_status = status._status
        self._set_cache(record, status)

    def pre_commit(self, record):
        """Dump the deletion status to the record before committing."""
        status = self._get_cache(record) or RecordDeletionStatus(None)
        record.model.deletion_status = record.get("deletion_status", status._status)

    def pre_dump(self, record, data, **kwargs):
        """Dump the deletion status information."""
        status = RecordDeletionStatus(record.model.deletion_status)
        # mitigation of deletion_status.is_deleted missing from the mapping
        # currently it is a string
        # don't confuse with record.model.is_deleted!
        data["is_deleted"] = status.is_deleted
        data["deletion_status"] = status.status

    def post_load(self, record, data, **kwargs):
        """After loading, set the deletion status."""
        deletion_status = data.get("deletion_status", None)
        self.__set__(record, deletion_status)
        # mitigation of deletion_status.is_deleted missing from the mapping
        # currently it is a string
        # don't confuse with record.model.is_deleted!
        record.pop("is_deleted", None)
        record.pop("deletion_status", None)
