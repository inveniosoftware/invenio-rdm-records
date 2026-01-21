# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Policies for self-service user actions."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from flask import current_app
from invenio_access.permissions import authenticated_user, system_permission
from invenio_administration.permissions import administration_permission
from invenio_i18n import lazy_gettext as _


class BasePolicy:
    """Base class for defining policies."""

    id: str
    description: str
    tombstone_description: str

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
        self.tombstone_description = _(
            "Record owners can delete their records within {grace_period} days of publishing."
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


class FileModificationGracePeriodPolicy(BasePolicy):
    """File modification policy which depends on a number of days since publishing."""

    id = "file-modification-grace-period-v1"

    def __init__(self, grace_period=timedelta(days=30)):
        """Initialise the policy with a grace_period."""
        self.grace_period = grace_period
        self.description = _(
            "You can edit the files of your records within {grace_period} days of publishing."
        ).format(grace_period=grace_period.days)

    def is_allowed(self, identity, record):
        """Whether the identity is allowed to modify files."""
        is_record_owner = identity.user.id == record.parent.access.owned_by.owner_id
        return is_record_owner

    def evaluate(self, identity, record):
        """Whether the record is within the grace period."""
        expiration_time = record.created + self.grace_period
        expiration_time = expiration_time.replace(tzinfo=timezone.utc)
        is_record_within_grace_period = expiration_time > datetime.now(timezone.utc)

        return is_record_within_grace_period


class FileModificationAdminPolicy(BasePolicy):
    """File modification policy which allows admins to modify files of all records."""

    id = "file-modification-admin-v1"
    description = _("You can edit the files of the record as you are an admin.")

    def is_allowed(self, identity, record):
        """Admins are allowed."""
        is_admin = administration_permission.allows(identity)
        is_system = system_permission.allows(identity)
        return is_admin or is_system

    def evaluate(self, identity, record):
        """All records are valid."""
        return True


class PolicyEvaluator:
    """Base class for policy evaluator classes."""

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
        raise NotImplementedError


class RDMRecordDeletionPolicy(PolicyEvaluator):
    """Record deletion policy for both immediate and request deletions."""

    @classmethod
    def evaluate(cls, identity, record):
        """Evaluate both immediate and request deletion for an identity and record."""
        if authenticated_user not in identity.provides:
            # only authenticated users can delete records
            return {
                "immediate_deletion": cls.Result(False),
                "request_deletion": cls.Result(False),
            }

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

    @classmethod
    def get_policy_description(cls, policy_id):
        """Get deletion policy description."""
        if not policy_id:
            return None

        policies = current_app.config.get("RDM_IMMEDIATE_RECORD_DELETION_POLICIES", [])
        for policy in policies:
            if policy.id == policy_id:
                return policy.tombstone_description
        return None


class FileModificationPolicyEvaluator(PolicyEvaluator):
    """Published record file modification policy."""

    @classmethod
    def evaluate(cls, identity, record):
        """Evaluate file modification for an identity and record."""
        if authenticated_user not in identity.provides:
            # only authenticated users can modify files of records
            return {
                "immediate_file_modification": cls.Result(False),
            }

        return {
            "immediate_file_modification": cls.evaluate_policies(
                "RDM_IMMEDIATE_FILE_MODIFICATION_ENABLED",
                "RDM_IMMEDIATE_FILE_MODIFICATION_POLICIES",
                identity,
                record,
            ),
        }
