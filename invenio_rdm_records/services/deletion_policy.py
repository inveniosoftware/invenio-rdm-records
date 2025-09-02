# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record deletion policies."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from flask import current_app
from invenio_i18n import lazy_gettext as _


class BasePolicy:
    """Base class for defining deletion policies."""

    id: str
    description: str

    def is_allowed(self, identity, record):
        """Whether the identity is allowed to delete the record."""
        raise NotImplementedError

    def evaluate(self, identity, record):
        """Whether the record meets the conditions to be deleted."""
        raise NotImplementedError

    @property
    def to_dict(self):
        """Get the policy as a dict."""
        return {"id": self.id, "description": self.description}


class GracePeriodPolicy(BasePolicy):
    """Deletion policy which depends on a number of days since publishing."""

    id = "grace-period-v1"

    def __init__(self, grace_period=timedelta(days=30)):
        """Initialise the policy with a grace_period."""
        self.grace_period = grace_period
        self.description = _(
            "You can delete your records within {grace_period} days of publishing."
        ).format(grace_period=grace_period.days)

    def is_allowed(self, identity, record):
        """Whether the identity is allowed to delete the record."""
        is_record_owner = identity.user.id == record.parent.access.owned_by.owner_id
        return is_record_owner

    def evaluate(self, identity, record):
        """Whether the record is within the grace period."""
        expiration_time = record.created + self.grace_period
        expiration_time = expiration_time.replace(tzinfo=timezone.utc)
        is_record_within_grace_period = expiration_time > datetime.now(timezone.utc)

        return is_record_within_grace_period


class RequestDeletionPolicy(BasePolicy):
    """Deletion policy which only depends on the identity."""

    id = "request-deletion-v1"

    def __init__(self, grace_period=timedelta(days=30)):
        """Initialise the policy with a grace_period."""
        self.grace_period = grace_period
        self.description = _(
            "You must submit a deletion request with a detailed justification "
            "because the record has been "
            "published for more than {grace_period} days."
        ).format(grace_period=grace_period.days)

    def is_allowed(self, identity, record):
        """Whether the identity is allowed to delete the record."""
        is_record_owner = identity.user.id == record.parent.access.owned_by.owner_id
        return is_record_owner

    def evaluate(self, identity, record):
        """Request deletion is possible for all records."""
        return True


class RDMRecordDeletionPolicy:
    """Record deletion policy for both immediate and request deletions."""

    @dataclass
    class Result:
        """Result object for both front and backend."""

        enabled: bool
        valid_user: bool = False  # so we can show the button as disabled
        allowed: bool = False
        policy: Optional[BasePolicy] = None

    @classmethod
    def evaluate_policies(cls, enabled, policy_config, identity, record):
        """Evaluate whether deletion is allowed for a given policy, identity and record."""
        result = cls.Result(current_app.config[enabled])
        if not result.enabled:
            return result

        policies = current_app.config[policy_config]

        for policy in policies:
            if policy.is_allowed(identity, record):
                result.valid_user = True
                if policy.evaluate(identity, record):
                    result.allowed = True
                    result.policy = policy.to_dict
                    return result  # early return, do not evaluate all policies

        return result

    @classmethod
    def evaluate(cls, identity, record):
        """Evaluate both immediate and request deletion for an identity and record."""
        return {
            "immediate_deletion": cls.evaluate_policies(
                "RDM_IMMEDIATE_RECORD_DELETION_ENABLED",
                "RDM_IMMEDIATE_RECORD_DELETION_POLICIES",
                identity,
                record,
            ),
            "request_deletion": cls.evaluate_policies(
                "RDM_REQUEST_RECORD_DELETION_ENABLED",
                "RDM_REQUEST_RECORD_DELETION_POLICIES",
                identity,
                record,
            ),
        }
