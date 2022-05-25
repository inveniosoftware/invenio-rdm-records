# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
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

from flask_babelex import gettext as _
from invenio_records.systemfields import SystemField

from invenio_rdm_records.services.errors import RDMRecordsException, \
    ReviewStateError


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

        review = getattr(record.parent, "review")
        is_published = getattr(record, "is_published")

        if is_published:
            return "published"

        is_new_version_draft = not is_published and record.versions.index > 1
        if is_new_version_draft:
            return "new_version_draft"

        is_draft = not is_published and record.versions.index == 1
        if is_draft:
            if review is None:
                return "draft"

            try:
                return self.review_to_draft_statuses[review.status]
            except KeyError:
                raise ReviewStateError(
                    _("Unknown draft status for review: {reviewstatus}."
                      .format(reviewstatus=review.status))
                )

        raise RDMRecordsException(_("Unknown draft status."))
