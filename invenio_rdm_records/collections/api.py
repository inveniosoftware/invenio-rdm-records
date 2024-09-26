# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections programmatic API."""

from types import ClassMethodDescriptorType

from invenio_db import db
from sqlalchemy import select
from werkzeug.utils import cached_property

from .models import Collection as CollectionModel
from .models import CollectionTree as CollectionTreeModel


class Collection:
    """Collection Object."""

    model_cls = CollectionModel

    def __init__(self, model=None):
        """Instantiate a Collection object."""
        self.model = model

    @classmethod
    def create(cls, slug, title, query, ctree=None, parent=None, order=None):
        """Create a new collection."""
        _ctree = None
        if parent:
            path = f"{parent.path}{parent.id},"
            _ctree = parent.collection_tree.model
        elif ctree:
            path = ","
            _ctree = ctree if isinstance(ctree, int) else ctree.model
        else:
            raise ValueError("Either parent or ctree must be set.")

        return cls(
            cls.model_cls.create(
                slug=slug,
                path=path,
                title=title,
                search_query=query,
                order=order,
                ctree_or_id=_ctree,
            )
        )

    @classmethod
    def resolve(cls, id_, ctree_id=None, use_slug=False):
        """Resolve a collection by ID or slug.

        To resolve by slug, the collection tree ID must be provided.
        """
        if not use_slug:
            return cls.get(id_)
        if not ctree_id:
            raise ValueError(
                "Collection tree ID is required to resolve a collection by slug."
            )
        return cls.get_by_slug(id_, ctree_id)

    @classmethod
    def get(cls, id_):
        """Get a collection by ID."""
        model = cls.model_cls.get(id_)
        if not model:
            return None
        return cls(model)

    @classmethod
    def get_by_slug(cls, slug, ctree_id):
        """Get a collection by slug."""
        model = cls.model_cls.get_by_slug(slug, ctree_id)
        if not model:
            return None
        return cls(model)

    def add(
        self,
        slug,
        title,
        query,
        order=None,
    ):
        """Add a subcollection to the collection."""
        return self.create(
            slug=slug,
            title=title,
            query=query,
            parent=self,
            order=order,
        )

    @property
    def id(self):
        """Get the collection ID."""
        return self.model.id

    @property
    def path(self):
        """Get the collection path."""
        return self.model.path

    @property
    def ctree_id(self):
        """Get the collection tree ID."""
        return self.model.tree_id

    @property
    def order(self):
        """Get the collection order."""
        return self.model.order

    @property
    def title(self):
        """Get the collection title."""
        return self.model.title

    @property
    def ctree_title(self):
        """Get the collection tree title."""
        return self.model.collection_tree.title

    @property
    def collection_tree(self):
        """Get the collection tree object.

        Note: this will execute a query to the collection tree table.
        """
        return CollectionTree(self.model.collection_tree)

    @property
    def depth(self):
        """Get the collection depth in its tree."""
        return self.model.depth

    @property
    def slug(self):
        """Get the collection slug."""
        return self.model.slug

    @cached_property
    def community(self):
        """Get the community object."""
        return self.collection_tree.community

    @property
    def query(self):
        """Get the collection query."""
        q = ""
        for _a in self.ancestors:
            q += f"({_a.model.search_query}) AND "
        q += f"({self.model.search_query})"
        return q

    @cached_property
    def ancestors(self):
        """Get the collection ancestors."""
        if not self.model:
            return None

        cps = self.path.split(",")
        ret = []
        for cid in cps:
            if not cid:
                continue
            cl = Collection.get(cid)
            ret.append(cl)
        return list(sorted(ret, key=lambda x: (x.path, x.order)))

    @cached_property
    def sub_collections(self):
        """Fetch all the descendants."""
        return self.get_subcollections()

    @cached_property
    def direct_subcollections(self):
        """Fetch only direct descendants."""
        return self.get_direct_subcollections()

    def get_direct_subcollections(self):
        """Get the collection first level (direct) children.

        More preformant query to retrieve descendants, executes an exact match query.
        """
        if not self.model:
            return None
        stmt = (
            select(self.model_cls)
            .filter(
                self.model_cls.path == f"{self.path}{self.id},",
                self.model_cls.tree_id == self.ctree_id,
            )
            .order_by(self.model_cls.path, self.model_cls.order)
        )
        ret = db.session.execute(stmt).scalars().all()
        return [type(self)(r) for r in ret]

    def get_subcollections(self, max_depth=3):
        """Get the collection subcollections.

        This query executes a LIKE query on the path column.
        """
        if not self.model:
            return None

        stmt = (
            select(self.model_cls)
            .filter(
                self.model_cls.path.like(f"{self.path}{self.id},%"),
                self.model_cls.depth < self.model.depth + max_depth,
            )
            .order_by(self.model_cls.path, self.model_cls.order)
        )
        ret = db.session.execute(stmt).scalars().all()
        return [type(self)(r) for r in ret]

    @classmethod
    def dump(cls, collection):
        """Transform the collection into a dictionary."""
        res = {
            "title": collection.title,
            "slug": collection.slug,
            "depth": collection.depth,
            "order": collection.order,
            "id": collection.id,
            "query": collection.query,
        }
        return res

    def to_dict(self) -> dict:
        """Return a dictionary representation of the collection.

        Uses an adjacency list.
        """
        ret = {
            "root": self.id,
            self.id: {**Collection.dump(self), "children": set()},
        }

        for _c in self.sub_collections:
            # Add the collection itself to the dictionary
            if _c.id not in ret:
                ret[_c.id] = {**Collection.dump(_c), "children": set()}

            # Find the parent ID from the collection's path (last valid ID in the path)
            path_parts = [int(part) for part in _c.path.split(",") if part.strip()]
            if path_parts:
                parent_id = path_parts[-1]
                # Add the collection as a child of its parent
                ret[parent_id]["children"].add(_c.id)
        for k, v in ret.items():
            if isinstance(v, dict):
                v["children"] = list(v["children"])
        return ret

    def __repr__(self) -> str:
        """Return a string representation of the collection."""
        if self.model:
            return f"Collection {self.id} ({self.path})"
        else:
            return "Collection (None)"


class CollectionTree:
    """Collection Tree Object."""

    model_cls = CollectionTreeModel

    def __init__(self, model):
        """Instantiate a CollectionTree object."""
        self.model = model

    @classmethod
    def create(cls, title, slug, community_id=None, order=None):
        """Create a new collection tree."""
        return cls(
            cls.model_cls.create(
                title=title, slug=slug, community_id=community_id, order=order
            )
        )

    @classmethod
    def resolve(cls, id_, community_id=None, use_slug=False):
        """Resolve a CollectionTree."""
        if not use_slug:
            return cls.get(id_)

        if not community_id:
            raise ValueError(
                "Community ID is required to resolve a collection tree by slug."
            )
        return cls.get_by_slug(id_, community_id)

    @classmethod
    def get(cls, id_):
        """Get a collection tree by ID."""
        model = cls.model_cls.get(id_)
        if not model:
            return None
        return cls(model)

    @classmethod
    def get_by_slug(cls, slug, community_id):
        """Get a collection tree by slug.

        Community ID is required to avoid ambiguity.
        """
        model = cls.model_cls.get_by_slug(slug, community_id)
        if not model:
            return None
        return cls(model)

    @property
    def id(self):
        """Get the collection tree ID."""
        return self.model.id

    @property
    def title(self):
        """Get the collection tree title."""
        return self.model.title

    @property
    def slug(self):
        """Get the collection tree slug."""
        return self.model.slug

    @property
    def community_id(self):
        """Get the community ID."""
        return self.model.community_id

    @property
    def order(self):
        """Get the collection tree order."""
        return self.model.order

    @property
    def community(self):
        """Get the community object."""
        return self.model.community
