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


class ModelField:

    def __init__(self, attr_name):
        self._attr_name = attr_name

    @property
    def attr_name(self):
        """The name of the SQLAlchemy field on the model.

        Defaults to the attribute name used on the class.
        """
        return self._attr_name

    def __get__(self, obj, objtype=None):
        """Descriptor method to get the object."""
        if obj is None:
            return self

        # Try instance access
        try:
            return getattr(obj.model, self.attr_name)
        except AttributeError:
            return None


class Collection:
    """Collection Object."""

    model_cls = CollectionModel

    id = ModelField("id")
    path = ModelField("path")
    ctree_id = ModelField("collection_tree_id")
    order = ModelField("order")
    title = ModelField("title")
    slug = ModelField("slug")
    depth = ModelField("depth")

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
    def resolve(cls, id_=None, slug=None, ctree_id=None):
        """Resolve a collection by ID or slug.

        To resolve by slug, the collection tree ID must be provided.
        """
        if id_:
            return cls(cls.model_cls.get(id_))
        if slug and ctree_id:
            return cls(cls.model_cls.get_by_slug(slug, ctree_id))
        raise ValueError("Either ID or slug and collection tree ID must be provided.")

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
    def collection_tree(self):
        """Get the collection tree object.

        Note: this will execute a query to the collection tree table.
        """
        return CollectionTree(self.model.collection_tree)

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
            cl = Collection.resolve(cid)
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

    id = ModelField("id")
    title = ModelField("title")
    slug = ModelField("slug")
    community_id = ModelField("community_id")
    order = ModelField("order")
    community = ModelField("community")

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
    def resolve(cls, id_=None, slug=None, community_id=None):
        """Resolve a CollectionTree."""
        if id_:
            return cls(cls.model_cls._get(id_))
        elif slug and community_id:
            return cls(cls.model_cls._get_by_slug(slug, community_id))
        else:
            raise ValueError("Either ID or slug and community ID must be provided.")
