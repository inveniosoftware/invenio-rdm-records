# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service Errors."""

from flask_principal import PermissionDenied
from invenio_i18n import lazy_gettext as _


class RDMRecordsException(Exception):
    """Base exception for RDMRecords errors."""


class GrantExistsError(RDMRecordsException):
    """Exception raised when trying to create a grant that already exists for user/role."""

    description = _("Grant for this user/role already exists within this record.")


class RecordDeletedException(RDMRecordsException):
    """Exception denoting that the record was deleted."""

    def __init__(self, record, result_item=None):
        """Constructor."""
        self.record = record
        self.result_item = result_item


class DeletionStatusException(RDMRecordsException):
    """Indicator for the record being in the wrong deletion status for the action."""

    def __init__(self, record, expected_status):
        """Constructor."""
        self.expected_status = expected_status
        self.record = record


class EmbargoNotLiftedError(RDMRecordsException):
    """Embargo could not be lifted ."""

    def __init__(self, record_id):
        """Initialise error."""
        self.record_id = record_id

    @property
    def description(self):
        """Exception's description."""
        return _(
            "Embargo could not be lifted for record: %(record_id)s",
            record_id=self.record_id,
        )


class ReviewException(RDMRecordsException):
    """Base class for review errors."""


class ReviewNotFoundError(ReviewException):
    """Review was not found for record/draft."""

    description = _("Review not found.")


class ReviewStateError(ReviewException):
    """Review was not found for record/draft."""


class ReviewExistsError(ReviewException):
    """Review exists - for operations which should when a review exists."""


class CommunitySubmissionException(Exception):
    """Base exception for community submission requests."""


class CommunityAlreadyExists(CommunitySubmissionException):
    """The record is already in the community."""

    description = _("The record is already included in this community.")


class CommunityInclusionException(Exception):
    """Base exception for community inclusion requests."""


class InvalidAccessRestrictions(CommunityInclusionException):
    """Invalid access restrictions for record and community."""

    description = _("A public record cannot be included in a restricted community.")


class OpenRequestAlreadyExists(CommunitySubmissionException):
    """An open request already exists."""

    def __init__(self, request_id):
        """Initialize exception."""
        self.request_id = request_id

    @property
    def description(self):
        """Exception's description."""
        return _("There is already an open inclusion request for this community.")


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


class RecordCommunityMissing(Exception):
    """Record does not belong to the community."""

    def __init__(self, record_id, community_id):
        """Initialise error."""
        self.record_id = record_id
        self.community_id = community_id

    @property
    def description(self):
        """Exception description."""
        return _(
            "The record %(rec_id)s in not included in the community %(com_id)s.",
            rec_id=self.record_id,
            com_id=self.community_id,
        )


class InvalidCommunityVisibility(Exception):
    """Community visibility does not match the content."""

    def __init__(self, reason):
        """Constructor."""
        self.reason = reason

    @property
    def description(self):
        """Exception description."""
        return _("Cannot modify community visibility: %(reason)s", reason=self.reason)


class AccessRequestException(RDMRecordsException):
    """Base class for errors related to access requests."""


class AccessRequestExistsError(AccessRequestException):
    """An identical access request already exists."""

    def __init__(self, request_id):
        """Constructor."""
        self.request_id = request_id

    @property
    def description(self):
        """Exception description."""
        if self.request_id:
            return _(
                "Identical access requests already exist: %(request_id)s",
                request_id=self.request_id,
            )
        else:
            return _("The access request is a duplicate")


class RecordSubmissionClosedCommunityError(PermissionDenied):
    """Record submission policy forbids non-members from submitting records to community."""

    description = _(
        "Submission to this community is only allowed to community members."
    )


class CommunityRequiredError(Exception):
    """Error thrown when a record is being created/updated with less than 1 community."""

    description = _("Cannot publish without a community.")


class CannotRemoveCommunityError(Exception):
    """Error thrown when the last community is being removed from the record."""

    description = _("A record should be part of at least 1 community.")
