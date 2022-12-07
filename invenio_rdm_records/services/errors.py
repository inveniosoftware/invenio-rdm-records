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
        super().__init__(f"Embargo could not be lifted for record: {record_id}")


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


class ReviewInconsistentAccessRestrictions(ReviewException):
    """Review has inconsistent record vs community access restrictions."""

    def __init__(self, *args, **kwargs):
        """Initialize exception."""
        super().__init__(
            _("Record submitted to restricted community cannot be public."),
            *args,
            **kwargs,
        )


class ValidationErrorWithMessageAsList(Exception):
    """Record Validation error where the messages are already a list.

    There is a large context around this to understand. Field errors are
    sent to the frontend by either:

    - raising a marshmallow ValidationError that is then caught by an error
      handler and converted to a list of
      `{field: <fieldpath>, messages: <error msg array>}` in the returned JSON.
      (See invenio_records_resources/resources/errors.py)
    - not raising an error but filling out an `errors` list that is
      serialzed out in JSON normally.

    The conversion process in the first case expects a dict of error messages
    inside the ValidationError. But these dict errors are converted to list
    as soon as the schema is loaded. The rest of the codebase works with the
    resulting list of errors. So for an error *raised* after schema
    validation, one would have to construct it by converting the list back to
    a dict, only for the error handler to reconvert it back again to that list
    in the end. (Note that passing the list of errors directly would result in
    `errors: {"_schema": <list of errors>}` passed to the frontend which
    isn't what it expects.)

    This error along with accompanying error_handler foregoes the need for
    that.
    """

    def __init__(self, message):
        """Constructor.

        Note that we keep the `message` parameter as interface to look like
        a marshmallow ValidationError even though it is annoying that the field
        is then called by `self.messages`.

        :param message: list of dicts in the shape:
                        `{"<fieldA>": ["<msgA1>", ...], ...}`
        """
        assert isinstance(message, list)
        self.messages = message
