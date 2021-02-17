# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Access system field."""

from invenio_records.systemfields import SystemField

from .embargo import Embargo
from .grants import Grants
from .owners import Owners
from .protection import Protection


class Access:
    """Access management per record."""

    grant_cls = Grants
    owners_cls = Owners
    protection_cls = Protection
    embargo_cls = Embargo

    def __init__(
        self,
        owned_by=None,
        grants=None,
        protection=None,
        embargo=None,
        errors=None,
        owners_cls=None,
        grants_cls=None,
        protection_cls=None,
    ):
        """Create a new Access object for a record.

        If ``owned_by``, ``grants`` or ``protection`` are not specified,
        a new instance of ``owners_cls``, ``grants_cls`` or ``protection_cls``
        will be used, respectively.
        :param owned_by: The set of record owners
        :param grants: The grants permitting access to the record
        :param protection: The record and file protection levels
        :param embargo: The embargo on the record (None means no embargo)
        """
        owners_cls = owners_cls or Access.owners_cls
        grants_cls = grants_cls or Access.grant_cls
        protection_cls = protection_cls or Access.protection_cls

        # since owned_by and grants are basically sets and empty sets
        # evaluate to False, assigning 'self.x = x or x_cls()' could lead to
        # unwanted results
        self._owned_by = owned_by
        if owned_by is None:
            self._owned_by = owners_cls()

        self._grants = grants
        if grants is None:
            self._grants = grants_cls()

        self._protection = protection
        if protection is None:
            self._protection = protection_cls("public", "public")

        self.embargo = embargo
        self._errors = errors or []

    def clear_embargo(self):
        """Remove all information about the embargo."""
        if self.embargo is not None:
            # disable the embargo first, for good measure
            self.embargo.active = False

        self._embargo = None

    @property
    def owned_by(self):
        """The set of owners for the record."""
        return self._owned_by

    @property
    def owners(self):
        """An alias for the owned_by property."""
        return self.owned_by

    @property
    def grants(self):
        """The set of permission grants for the record."""
        return self._grants

    @property
    def protection(self):
        """The file & record protection level of the record."""
        return self._protection

    @property
    def embargo(self):
        """The embargo information of the record."""
        return self._embargo

    @property
    def errors(self):
        """Get the list of accumulated validation errors."""
        return self._errors

    @embargo.setter
    def embargo(self, embargo):
        self._embargo = embargo

        if embargo is not None:
            # allow 'clear_embargo()' to be called as 'embargo.clear()'
            self._embargo.clear = lambda: self.clear_embargo()

    def dump(self):
        """Dump the field values as dictionary."""
        access = {
            "record": self.protection.record,
            "files": self.protection.files,
            "owned_by": self.owned_by.dump(),
            # "grants": self.grants.dump(),  # TODO enable again when ready
        }

        if self.embargo is not None:
            access["embargo"] = self.embargo.dump()

        return access

    def refresh_from_dict(self, access_dict):
        """Re-initialize the Access object with the data in the access_dict."""
        new_access = self.from_dict(access_dict)
        self._errors = new_access.errors
        self._owned_by = new_access.owned_by
        self._grants = new_access.grants
        self._protection = new_access.protection
        self.embargo = new_access.embargo

    @classmethod
    def from_dict(
        cls,
        access_dict,
        owners_cls=None,
        grants_cls=None,
        protection_cls=None,
        embargo_cls=None,
    ):
        """Create a new Access object from the specified 'access' property.

        The new ``Access`` object will be populated with new instances from
        the configured classes.
        If ``access_dict`` is empty, the ``Access`` object will be populated
        with new instances of ``owners_cls``, ``grants_cls``, and
        ``protection_cls``.
        """
        grants_cls = grants_cls or cls.grant_cls
        owners_cls = owners_cls or cls.owners_cls
        protection_cls = protection_cls or cls.protection_cls
        embargo_cls = embargo_cls or cls.embargo_cls
        errors = []

        if access_dict:
            owners = owners_cls()
            grants = grants_cls()
            protection = None
            embargo = None

            for owner_dict in access_dict.get("owned_by", []):
                try:
                    owners.add(owners.owner_cls(owner_dict))
                except Exception as e:
                    errors.append(e)

            for grant_dict in access_dict.get("grants", []):
                try:
                    grants.add(grants.grant_cls.from_dict(grant_dict))
                except Exception as e:
                    errors.append(e)

            try:
                protection = protection_cls(
                    access_dict["record"], access_dict["files"]
                )
            except Exception as e:
                errors.append(e)

            embargo_dict = access_dict.get("embargo")
            if embargo_dict is not None:
                embargo = embargo_cls.from_dict(embargo_dict)

        else:
            # if there is no 'access' property, fall back to default values
            owners = owners_cls()
            grants = grants_cls()
            protection = protection_cls()
            embargo = None

        access = cls(
            owned_by=owners,
            grants=grants,
            protection=protection,
            embargo=embargo,
            errors=errors,
        )

        return access

    def __repr__(self):
        """Return repr(self)."""
        protection_str = "{}/{}".format(
            self.protection.record, self.protection.files
        )
        if self.embargo is not None:
            embargo_str = "embargo: {}".format(repr(self.embargo))
        else:
            embargo_str = "no embargo"

        return "<{} (protection: {}, {}, owners: {}, grants: {})>".format(
            type(self).__name__,
            protection_str,
            embargo_str,
            len(self.owners),
            len(self.grants),
        )


class AccessField(SystemField):
    """System field for managing record access."""

    def __init__(self, key="access", access_obj_class=Access):
        """Create a new AccessField instance."""
        self._access_obj_class = access_obj_class
        super().__init__(key=key)

    def obj(self, instance):
        """Get the access object."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        data = self.get_dictkey(instance)
        if data:
            obj = self._access_obj_class.from_dict(data)
            self._set_cache(instance, obj)
            return obj

        return None

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
