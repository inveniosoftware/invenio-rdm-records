# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Mixin for cleaning the `review` field on parent/draft records."""

from marshmallow import post_dump, pre_load


class CleanReviewMixin:
    """Clean the `review` field from dumped/loaded schemas if it is None."""

    @pre_load
    def clean_review(self, data, **kwargs):
        """Clear review if None."""
        # draft.review/draft.parent.review returns None when not set, causing the serializer
        # to dump {'review': None}. As a workaround we pop it if it's none
        # here.
        if data.get("review", None) is None:
            data.pop("review", None)
        return data

    @post_dump()
    def pop_review_if_none(self, data, many, **kwargs):
        """Clear review if None."""
        if data.get("review", None) is None:
            data.pop("review", None)
        return data
