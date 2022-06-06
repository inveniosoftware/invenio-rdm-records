# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Access system field."""

from invenio_records.systemfields import SystemField

from ..grants import Grants
from ..links import Links
from ..owners import Owners


class ParentRecordAccess:
    """Access management for all versions of a record."""

    grant_cls = Grants
    links_cls = Links
    owners_cls = Owners

    def __init__(
        self,
        owned_by=None,
        grants=None,
        links=None,
        owners_cls=None,
        grants_cls=None,
        links_cls=None,
    ):
        """Create a new Access object for a record.

        If ``owned_by``, ``grants`` or ``links`` are not specified,
        a new instance of ``owners_cls``, ``grants_cls`` or ``links_cls``
        will be used, respectively.
        :param owned_by: The set of record owners
        :param grants: The grants permitting access to the record
        :param links: The secret links permitting access to the record
        """
        owners_cls = owners_cls or ParentRecordAccess.owners_cls
        grants_cls = grants_cls or ParentRecordAccess.grant_cls
        links_cls = links_cls or ParentRecordAccess.links_cls

        # since owned_by and grants are basically sets and empty sets
        # evaluate to False, assigning 'self.x = x or x_cls()' could lead to
        # unwanted results
        self.owned_by = owned_by if owned_by else owners_cls()
        self.grants = grants if grants else grants_cls()
        self.links = links if links else links_cls()
        self.errors = []

    @property
    def owners(self):
        """An alias for the owned_by property."""
        return self.owned_by

    def dump(self):
        """Dump the field values as dictionary."""
        access = {
            "owned_by": self.owned_by.dump(),
            "links": self.links.dump(),
            # "grants": self.grants.dump(),  # TODO enable again when ready
        }

        return access

    def refresh_from_dict(self, access_dict):
        """Re-initialize the Access object with the data in the access_dict."""
        new_access = self.from_dict(access_dict)
        self.errors = new_access.errors
        self.owned_by = new_access.owned_by
        self.grants = new_access.grants
        self.links = new_access.links

    @classmethod
    def from_dict(
        cls,
        access_dict,
        owners_cls=None,
        grants_cls=None,
        links_cls=None,
    ):
        """Create a new Access object from the specified 'access' property.

        The new ``ParentRecordAccess`` object will be populated with new
        instances from the configured classes.
        If ``access_dict`` is empty, the ``ParentRecordAccess`` object will
        be populated with new instances of ``owners_cls``, ``grants_cls``,
        and ``links_cls``.
        """
        grants_cls = grants_cls or cls.grant_cls
        links_cls = links_cls or cls.links_cls
        owners_cls = owners_cls or cls.owners_cls
        errors = []

        # provide defaults in case there is no 'access' property
        owners = owners_cls()
        grants = grants_cls()
        links = links_cls()

        if access_dict:
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

            for link_dict in access_dict.get("links", []):
                try:
                    links.add(links.link_cls(link_dict))
                except Exception as e:
                    errors.append(e)

        access = cls(
            owned_by=owners,
            grants=grants,
            links=links,
        )
        access.errors = errors
        return access

    def __repr__(self):
        """Return repr(self)."""
        return ("<{} (owners: {}, grants: {}, links: {})>").format(
            type(self).__name__,
            len(self.owners or []),
            len(self.grants or []),
            len(self.links or []),
        )


class ParentRecordAccessField(SystemField):
    """System field for managing record access."""

    def __init__(self, key="access", access_obj_class=ParentRecordAccess):
        """Create a new ParentRecordAccessField instance."""
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
