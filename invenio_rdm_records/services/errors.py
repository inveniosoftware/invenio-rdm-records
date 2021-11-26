# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service Errors."""

from flask_babelex import lazy_gettext as _


class RDMRecordsException(Exception):
    """Base exception for RDMRecords errors."""


class EmbargoNotLiftedError(RDMRecordsException):
    """Embargo could not be lifted ."""

    def __init__(self, record_id):
        """Initialise error."""
        super().__init__(
            f"Embargo could not be lifted for record: {record_id}"
        )


class ReviewException(RDMRecordsException):
    """Base class for review errors."""


class ReviewNotFoundError(ReviewException):
    """Review was not found for record/draft."""

    def __init__(self, *args, **kwargs):
        """Initialize exception."""
        super().__init__(_("Review not found."), *args, **kwargs)


class ReviewStateError(ReviewException):
    """Review was not found for record/draft."""


class ReviewExistsError(ReviewException):
    """Review exists - for operations which should when a review exists."""
