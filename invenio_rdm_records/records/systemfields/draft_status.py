# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2026 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft status field.

The DraftStatus is used to calculate the status of the draft based on its
associated review request.

For instance:

.. code-block:: python

    class Record():
        draft_status = DraftStatus()

"""

from invenio_i18n import gettext as _
from invenio_records.systemfields import SystemField

from ...services.errors import RDMRecordsException, ReviewStateError


class DraftStatus(SystemField):
    """Draft status field which checks the `parent.review` state."""

    review_to_draft_statuses = dict(
        created="draft_with_review",
        submitted="in_review",
        declined="declined",
        expired="expired",
        published="published",
    )
    """Available statuses that a draft can have. It maps review status to
    draft."""

    new_version_review_to_draft_statuses = dict(
        created="new_version_draft_with_review",
        submitted="in_review",
        declined="declined",
        expired="expired",
        published="published",
    )
    """Same as `review_to_draft_statuses` but for new version drafts."""

    def __init__(self, draft_cls=None, key=None):
        """Initialize the DraftStatus.

        It stores the `draft.draft_status` value in the record metadata.

        :param key: Attribute name to store the DraftStatus value.
        :param draft_cls: The draft class to check against e.g RDMDraft.
        """
        super().__init__(key=key)
        self.draft_cls = draft_cls

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the persistent identifier."""
        if record is None:
            return self  # returns the field itself.

        is_first_version = record.versions.index == 1
        # `record.parent.review` is used for the first draft of a new parent.
        # `record.review` is used for reviews of all subsequent record versions.
        review = (
            getattr(record.parent, "review")
            if is_first_version
            else getattr(record, "review")
        )

        # If this specific record is published (i.e. NOT whether at least one published record exists within the parent)
        is_published = getattr(record, "is_published")
        if is_published:
            return "published"

        # The record is a draft...

        if review is None:
            # If the record is the first draft (i.e. the parent record is not published),
            # record.versions.index will be 1.
            return "draft" if record.versions.index == 1 else "new_version_draft"

        try:
            # The status depends on whether the record is the first version or not
            return (
                self.review_to_draft_statuses[review.status]
                if is_first_version
                else self.new_version_review_to_draft_statuses[review.status]
            )
        except KeyError:
            raise ReviewStateError(
                _(
                    "Unknown draft status for review: {reviewstatus}.".format(
                        reviewstatus=review.status
                    )
                )
            )
