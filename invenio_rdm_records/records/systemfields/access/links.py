# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Links class for the access system field."""

from ....links.models import SecretLink


class Link:
    """An abstraction between SecretLink entities and dict representations."""

    def __init__(self, link):
        """Create a link from either a dictionary or a SecretLink."""
        self._entity = None
        self.link_id = None

        if isinstance(link, dict):
            self.link_id = str(link.get("id"))

        elif isinstance(link, SecretLink):
            self._entity = link
            self.link_id = str(link.id)

        else:
            raise TypeError("invalid link type: {}".format(type(link)))

    def dump(self):
        """Dump the link to a dictionary."""
        return {"id": str(self.link_id)}

    def resolve(self, raise_exc=False):
        """Resolve the link entity (e.g. SecretLink) via a database query."""
        if self._entity is None:
            self._entity = SecretLink.query.get(self.link_id)

            if self._entity is None and raise_exc:
                raise LookupError(
                    "could not find link: {}".format(self.dump())
                )

        return self._entity

    def __hash__(self):
        """Return hash(self)."""
        return hash(self.link_id)

    def __eq__(self, other):
        """Return self == other."""
        if type(self) != type(other):
            return False

        return self.link_id == other.link_id

    def __ne__(self, other):
        """Return self != other."""
        return not self == other

    def __str__(self):
        """Return str(self)."""
        return str(self.resolve())

    def __repr__(self):
        """Return repr(self)."""
        return repr(self.resolve())


class Links(list):
    """List of links for various permission levels on a record."""

    link_cls = Link

    def __init__(self, grants=None):
        """Create a new list of Grants."""
        for grant in grants or []:
            self.add(grant)

    def append(self, link):
        """Add the grant to the list of grants."""
        if not isinstance(link, self.link_cls):
            link = self.link_cls(link)

        if link not in self:
            super().append(link)

    def add(self, link):
        """Alias for self.append(link)."""
        self.append(link)

    def extend(self, links):
        """Add all new items from the specified links to this list."""
        for link in links:
            self.add(link)

    def remove(self, link):
        """Remove the specified link from the list of links."""
        if not isinstance(link, self.link_cls):
            link = self.link_cls(link)

        super().remove(link)

    def create(
        self,
        permission_level,
        extra_data=dict(),
        expires_at=None,
        commit=False,
    ):
        """Create a new secret link and add it to the list of links."""
        link = SecretLink.create(
            permission_level=permission_level,
            extra_data=extra_data,
            expires_at=expires_at,
            commit=commit,
        )
        self.add(link)
        return link

    def needs(self, permission):
        """Get allowed needs for the given permission level."""
        needs = {link.need for link in self if link.covers(permission)}
        return needs

    def dump(self):
        """Dump the links as a list of link IDs."""
        return [link.dump() for link in self]
