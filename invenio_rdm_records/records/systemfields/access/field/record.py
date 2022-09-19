# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Access system field."""

from enum import Enum

from invenio_records.systemfields import SystemField

from ..embargo import Embargo
from ..protection import Protection


class AccessStatusEnum(Enum):
    """Enum defining access statuses."""

    OPEN = "open"

    EMBARGOED = "embargoed"

    RESTRICTED = "restricted"

    METADATA_ONLY = "metadata-only"


class RecordAccess:
    """Access management per record."""

    protection_cls = Protection
    embargo_cls = Embargo

    def __init__(
        self,
        protection=None,
        embargo=None,
        protection_cls=None,
        embargo_cls=None,
        has_files=None,
    ):
        """Create a new RecordAccess object for a record.

        If ``protection`` or ``embargo`` are not specified,
        a new instance of ``protection_cls`` or ``embargo_cls``
        will be used, respectively.
        :param protection: The record and file protection levels
        :param embargo: The embargo on the record (None means no embargo)
        """
        protection_cls = protection_cls or RecordAccess.protection_cls
        embargo_cls = embargo_cls or RecordAccess.embargo_cls

        public = protection_cls("public", "public")
        self.protection = protection if protection is not None else public
        self.embargo = embargo if embargo is not None else embargo_cls()
        self.has_files = has_files
        self.errors = []

    @property
    def status(self):
        """Record's access status."""
        status = AccessStatusEnum.RESTRICTED

        if self.embargo.active:
            status = AccessStatusEnum.EMBARGOED
        elif self.protection.record == "public" and not self.has_files:
            status = AccessStatusEnum.METADATA_ONLY
        elif self.protection.record == self.protection.files == "public":
            status = AccessStatusEnum.OPEN

        return status

    def dump(self):
        """Dump the field values as dictionary."""
        access = {
            "record": self.protection.record,
            "files": self.protection.files,
            "embargo": self.embargo.dump(),
        }

        return access

    def lift_embargo(self):
        """Update the embargo active status if it has expired.

        Returns ``True`` if the embargo was actually lifted (i.e. it was
        expired but still marked as active).
        """
        if self.embargo._lift():
            self.protection.set(record="public", files="public")
            return True

        return False

    def refresh_from_dict(self, access_dict):
        """Re-initialize the Access object with the data in the access_dict."""
        new_access = self.from_dict(access_dict)
        self.protection = new_access.protection
        self.embargo = new_access.embargo
        self.errors = new_access.errors

    @classmethod
    def from_dict(
        cls, access_dict, protection_cls=None, embargo_cls=None, has_files=None
    ):
        """Create a new Access object from the specified 'access' property.

        The new ``RecordAccess`` object will be populated with new instances
        from the configured classes.
        If ``access_dict`` is empty, the ``Access`` object will be populated
        with new instances of ``protection_cls`` and ``embargo_cls``.
        """
        protection_cls = protection_cls or cls.protection_cls
        embargo_cls = embargo_cls or cls.embargo_cls
        errors = []

        # provide defaults in case there is no 'access' property
        protection = protection_cls()
        embargo = embargo_cls()

        if access_dict:
            try:
                protection = protection_cls(access_dict["record"], access_dict["files"])
            except Exception as e:
                errors.append(e)

            embargo_dict = access_dict.get("embargo")
            if embargo_dict is not None:
                embargo = embargo_cls.from_dict(embargo_dict)

        access = cls(
            protection=protection,
            embargo=embargo,
            has_files=has_files,
        )
        access.errors = errors

        return access

    def __eq__(self, other):
        """Compare access objects."""
        if type(self) != type(other):
            return False

        return self.embargo == other.embargo and self.protection == other.protection

    def __repr__(self):
        """Return repr(self)."""
        protection_str = "{}/{}".format(self.protection.record, self.protection.files)

        return ("<{} (protection: {}, {})>").format(
            type(self).__name__,
            protection_str,
            self.embargo,
        )


class RecordAccessField(SystemField):
    """System field for managing record access."""

    def __init__(self, key="access", access_obj_class=RecordAccess):
        """Create a new RecordAccessField instance."""
        self._access_obj_class = access_obj_class
        super().__init__(key=key)

    def obj(self, instance):
        """Get the access object."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        data = self.get_dictkey(instance)
        if data:
            obj = self._access_obj_class.from_dict(data, has_files=len(instance.files))
        else:
            obj = self._access_obj_class()

        self._set_cache(instance, obj)
        return obj

    def set_obj(self, record, obj):
        """Set the access object."""
        # We accept both dicts and access class objects.
        if isinstance(obj, dict):
            obj = self._access_obj_class.from_dict(obj)

        assert isinstance(obj, self._access_obj_class)

        # We do not dump the object until the pre_commit hook
        # I.e. record.access != record['access']
        self._set_cache(record, obj)

    def __get__(self, record, owner=None):
        """Get the record's access object."""
        if record is None:
            # access by class
            return self

        # access by object
        return self.obj(record)

    def __set__(self, record, obj):
        """Set the records access object."""
        self.set_obj(record, obj)

    def pre_commit(self, record):
        """Dump the configured values before the record is committed."""
        obj = self.obj(record)
        if obj is not None:
            # only set the 'access' property if one was present in the
            # first place -- this was a problem in the unit test:
            # tests/resources/test_resources.py:test_simple_flow
            record["access"] = obj.dump()

    def post_dump(self, record, data, dumper=None):
        """Called before a record is dumped."""
        if data.get("access") and isinstance(data.get("access"), dict):
            data["access"]["status"] = record.access.status.value

    def pre_load(self, data, loader=None):
        """Called before a record is dumped."""
        if data.get("access") and isinstance(data.get("access"), dict):
            data["access"].pop("status", None)
