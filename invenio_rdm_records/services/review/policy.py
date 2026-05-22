# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Policy configuration to define which versions of records require community review."""


class NewRecordVersionReviewPolicy:
    """
    Base class for defining a policy for whether new versions of records require community review.

    A new record submitted to a community for the first time (via a community submission request) will always
    require a review regardless of this policy (subject to the community's settings).
    """

    @classmethod
    def requires_review(cls, identity, draft) -> bool:
        """
        Returns whether the draft needs to be submitted for a review.

        If the first draft of a new parent record is submitted to a community, it will always trigger a review
        (subject to the community's settings).
        The return value of this method only applies to new version drafts created for existing records.

        The default behaviour is to return False, meaning new versions of existing records will never require
        a community review.
        """
        return False
