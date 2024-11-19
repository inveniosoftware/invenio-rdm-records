# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections programmatic API."""
from invenio_records.systemfields import ModelField
from luqum.parser import parser as luqum_parser
from werkzeug.utils import cached_property

from .errors import CollectionNotFound, CollectionTreeNotFound, InvalidQuery
from .models import Collection as CollectionModel
from .models import CollectionTree as CollectionTreeModel


class Collection:
    """Collection Object."""

    model_cls = CollectionModel

    id = ModelField()
    path = ModelField()
    ctree_id = ModelField("collection_tree_id")
    order = ModelField()
    title = ModelField()
    slug = ModelField()
    depth = ModelField()
    search_query = ModelField()
    num_records = ModelField()

    def __init__(self, model=None, max_depth=2):
        """Instantiate a Collection object."""
        self.model = model
        self.max_depth = max_depth

    @classmethod
    def validate_query(cls, query):
        """Validate the collection query."""
        try:
            luqum_parser.parse(query)
        except Exception:
            raise InvalidQuery()

    @classmethod
    def create(cls, slug, title, query, ctree=None, parent=None, order=None, depth=2):
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

        Collection.validate_query(query)
        return cls(
            cls.model_cls.create(
                slug=slug,
                path=path,
                title=title,
                search_query=query,
                order=order,
                ctree_or_id=_ctree,
            ),
            depth,
        )

    @classmethod
    def read(cls, *, id_=None, slug=None, ctree_id=None, depth=2):
        """Read a collection by ID or slug.

        To read by slug, the collection tree ID must be provided.
        """
        res = None
        if id_:
            res = cls(cls.model_cls.get(id_), depth)
        elif slug and ctree_id:
            res = cls(cls.model_cls.get_by_slug(slug, ctree_id), depth)
        else:
            raise ValueError(
                "Either ID or slug and collection tree ID must be provided."
            )

        if res.model is None:
            raise CollectionNotFound()
        return res

    @classmethod
    def read_many(cls, ids_, depth=2):
        """Read many collections by ID."""
        return [cls(c, depth) for c in cls.model_cls.read_many(ids_)]

    @classmethod
    def read_all(cls, depth=2):
        """Read all collections."""
        return [cls(c, depth) for c in cls.model_cls.read_all()]

    def update(self, **kwargs):
        """Update the collection."""
        if "search_query" in kwargs:
            Collection.validate_query(kwargs["search_query"])
        self.model.update(**kwargs)
        return self

    def add(self, slug, title, query, order=None, depth=2):
        """Add a subcollection to the collection."""
        return self.create(
            slug=slug, title=title, query=query, parent=self, order=order, depth=depth
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
        import operator
        from functools import reduce

        from invenio_search.engine import dsl

        queries = [dsl.Q("query_string", query=a.search_query) for a in self.ancestors]
        queries.append(dsl.Q("query_string", query=self.search_query))
        return reduce(operator.and_, queries)

    @cached_property
    def ancestors(self):
        """Get the collection ancestors."""
        ids_ = self.split_path_to_ids()
        if not ids_:
            return []
        return Collection.read_many(ids_)

    @cached_property
    def subcollections(self):
        """Fetch descendants.

        If the max_depth is 1, fetch only direct descendants.
        """
        if self.max_depth == 0:
            return []

        if self.max_depth == 1:
            return self.get_children()

        return self.get_subcollections()

    @cached_property
    def children(self):
        """Fetch only direct descendants."""
        return self.get_children()

    def split_path_to_ids(self):
        """Return the path as a list of integers."""
        if not self.model:
            return None
        return [int(part) for part in self.path.split(",") if part.strip()]

    def get_children(self):
        """Get the collection first level (direct) children.

        More preformant query to retrieve descendants, executes an exact match query.
        """
        if not self.model:
            return None
        res = self.model_cls.get_children(self.model)
        return [type(self)(r) for r in res]

    def get_subcollections(self):
        """Get the collection subcollections.

        This query executes a LIKE query on the path column.
        """
        if not self.model:
            return None

        res = self.model_cls.get_subcollections(self.model, self.max_depth)
        return [type(self)(r) for r in res]

    def __repr__(self) -> str:
        """Return a string representation of the collection."""
        if self.model:
            return f"Collection {self.id} ({self.path})"
        else:
            return "Collection (None)"

    def __eq__(self, value: object) -> bool:
        """Check if the value is equal to the collection."""
        return isinstance(value, Collection) and value.id == self.id


class CollectionTree:
    """Collection Tree Object."""

    model_cls = CollectionTreeModel

    id = ModelField("id")
    title = ModelField("title")
    slug = ModelField("slug")
    community_id = ModelField("community_id")
    order = ModelField("order")
    community = ModelField("community")
    collections = ModelField("collections")

    def __init__(self, model=None, max_depth=2):
        """Instantiate a CollectionTree object."""
        self.model = model
        self.max_depth = max_depth

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
        res = None
        if id_:
            res = cls(cls.model_cls.get(id_))
        elif slug and community_id:
            res = cls(cls.model_cls.get_by_slug(slug, community_id))
        else:
            raise ValueError("Either ID or slug and community ID must be provided.")

        if res.model is None:
            raise CollectionTreeNotFound()
        return res

    @cached_property
    def collections(self):
        """Get the collections under this tree."""
        root_collections = CollectionTreeModel.get_collections(self.model, 1)
        return [Collection(c, self.max_depth) for c in root_collections]

    @classmethod
    def get_community_trees(cls, community_id, depth=2):
        """Get all the collection trees for a community."""
        return [cls(c, depth) for c in cls.model_cls.get_community_trees(community_id)]
