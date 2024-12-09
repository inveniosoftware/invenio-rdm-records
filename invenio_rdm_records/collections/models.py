# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections models."""

from invenio_communities.communities.records.models import CommunityMetadata
from invenio_db import db
from invenio_records.models import Timestamp
from sqlalchemy import UniqueConstraint
from sqlalchemy_utils.types import UUIDType


# CollectionTree Table
class CollectionTree(db.Model, Timestamp):
    """Collection tree model."""

    __tablename__ = "collections_collection_tree"

    __table_args__ = (
        # Unique constraint on slug and community_id. Slugs should be unique within a community.
        UniqueConstraint(
            "slug",
            "community_id",
            name="uq_collections_collection_tree_slug_community_id",
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    community_id = db.Column(
        UUIDType,
        db.ForeignKey(CommunityMetadata.id, ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=True)
    slug = db.Column(db.String(255), nullable=False)

    # Relationship to Collection
    collections = db.relationship("Collection", back_populates="collection_tree")
    community = db.relationship(CommunityMetadata, backref="collection_trees")

    @classmethod
    def create(cls, title, slug, community_id=None, order=None):
        """Create a new collection tree."""
        with db.session.begin_nested():
            collection_tree = cls(
                title=title, slug=slug, community_id=community_id, order=order
            )
            db.session.add(collection_tree)
        return collection_tree

    @classmethod
    def get(cls, id_):
        """Get a collection tree by ID."""
        return cls.query.get(id_)

    @classmethod
    def get_by_slug(cls, slug, community_id):
        """Get a collection tree by slug."""
        return cls.query.filter(
            cls.slug == slug, cls.community_id == community_id
        ).one_or_none()

    @classmethod
    def get_community_trees(cls, community_id):
        """Get all collection trees of a community."""
        return cls.query.filter(cls.community_id == community_id).order_by(cls.order)

    @classmethod
    def get_collections(cls, model, max_depth):
        """Get collections under a tree."""
        return Collection.query.filter(
            Collection.tree_id == model.id, Collection.depth < max_depth
        ).order_by(Collection.path, Collection.order)


# Collection Table
class Collection(db.Model, Timestamp):
    """Collection model.

    Indices:
    - id
    - collection_tree_id
    - path
    - slug
    """

    __tablename__ = "collections_collection"
    __table_args__ = (
        # Unique constraint on slug and tree_id. Slugs should be unique within a tree.
        UniqueConstraint(
            "slug", "tree_id", name="uq_collections_collection_slug_tree_id"
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(255), nullable=False)
    path = db.Column(db.Text, nullable=False, index=True)
    tree_id = db.Column(
        db.Integer, db.ForeignKey("collections_collection_tree.id"), nullable=False
    )
    title = db.Column(db.String(255), nullable=False)
    search_query = db.Column("query", db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=True)
    # TODO index depth
    depth = db.Column(db.Integer, nullable=False)
    num_records = db.Column(db.Integer, nullable=False, default=0)

    # Relationship to CollectionTree
    collection_tree = db.relationship("CollectionTree", back_populates="collections")

    @classmethod
    def create(cls, slug, path, title, search_query, ctree_or_id, **kwargs):
        """Create a new collection."""
        depth = len([int(part) for part in path.split(",") if part.strip()])
        with db.session.begin_nested():
            if isinstance(ctree_or_id, CollectionTree):
                collection = cls(
                    slug=slug,
                    path=path,
                    title=title,
                    search_query=search_query,
                    collection_tree=ctree_or_id,
                    depth=depth,
                    **kwargs,
                )
            elif isinstance(ctree_or_id, int):
                collection = cls(
                    slug=slug,
                    path=path,
                    title=title,
                    search_query=search_query,
                    tree_id=ctree_or_id,
                    depth=depth,
                    **kwargs,
                )
            else:
                raise ValueError(
                    "Either `collection_tree` or `collection_tree_id` must be provided."
                )
            db.session.add(collection)
        return collection

    @classmethod
    def get(cls, id_):
        """Get a collection by ID."""
        return cls.query.get(id_)

    @classmethod
    def get_by_slug(cls, slug, tree_id):
        """Get a collection by slug."""
        return cls.query.filter(cls.slug == slug, cls.tree_id == tree_id).one_or_none()

    @classmethod
    def read_many(cls, ids_):
        """Get many collections by ID."""
        return cls.query.filter(cls.id.in_(ids_)).order_by(cls.path, cls.order)

    @classmethod
    def read_all(cls):
        """Get all collections.

        The collections are ordered by ``path`` and ``order``, which means:

        - By path: the collections are ordered in a breadth-first manner (first come the root collection, then the next level, and so on)
        - By order: between the same level collections, they are ordered by the specified order field.
        """
        return cls.query.order_by(cls.path, cls.order)

    def update(self, **kwargs):
        """Update a collection."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def get_children(cls, model):
        """Get children collections of a collection."""
        return cls.query.filter(
            cls.path == f"{model.path}{model.id},", cls.tree_id == model.tree_id
        ).order_by(cls.path, cls.order)

    @classmethod
    def get_subcollections(cls, model, max_depth):
        """Get subcollections of a collection.

        This query will return all subcollections of a collection up to a certain depth.
        It can be used for max_depth=1, however it is more efficient to use get_children.
        """
        return cls.query.filter(
            cls.path.like(f"{model.path}{model.id},%"),
            cls.tree_id == model.tree_id,
            cls.depth < model.depth + max_depth,
        ).order_by(cls.path, cls.order)
