# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Storage Service."""

import logging
from math import ceil

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_search.engine import dsl
from sqlalchemy import func

from invenio_rdm_records.records.models import (
    RDMDraftMetadata,
    RDMRecordMetadata,
    RDMRecordQuota,
    RDMUserQuota,
)

logger = logging.getLogger(__name__)


class StorageService:
    """Service providing per-user storage quota information."""

    def __init__(self, records_service):
        """Constructor."""
        self.records_service = records_service

    def default_quota(self, user=None):
        """Default quota for user."""
        user_id = user.id if isinstance(user, User) else user

        user_quota = (
            getattr(
                RDMUserQuota.query.filter(
                    RDMUserQuota.user_id == user_id
                ).one_or_none(),
                "quota_size",
                None,
            )
            if user
            else None
        )

        return user_quota or current_app.config.get(
            "RDM_FILES_DEFAULT_QUOTA_SIZE", 10 * 10**9
        )

    def record_draft_quota_size(self, record, user_id):
        """Current quota for a draft."""
        if record:
            return record.bucket.quota_size
        else:
            return self.default_quota(user_id)

    def _get_max_bucket_size(self, parent_id, metadata_model):
        """Get maximum bucket size for given parent and metadata model."""
        result = (
            db.session.query(func.coalesce(func.max(Bucket.size), 0))
            .join(metadata_model, Bucket.id == metadata_model.bucket_id)
            .filter(metadata_model.parent_id == parent_id)
            .scalar()
        )
        return int(result) if result else 0

    def record_draft_used_quota(self, record):
        """Calculate maximum used quota across all versions of a record and its drafts."""
        if record:
            parent_id = record.parent.id

            return max(
                self._get_max_bucket_size(parent_id, RDMRecordMetadata),
                self._get_max_bucket_size(parent_id, RDMDraftMetadata),
            )
        else:
            return 0

    def additional_storage(self, user_id, record):
        """Additional quota for a specific draft."""
        return max(
            self.record_draft_quota_size(record, user_id) - self.default_quota(user_id),
            0,
        )

    def min_additional_quota_value(self, user_id, record=None):
        """Minimum additional quota value for a specific draft."""
        # size of uploaded files so that they can't request less than that
        bytes_usage = self.record_draft_used_quota(record) - self.default_quota(user_id)
        gb_usage = bytes_usage / 10**9
        gb_ceil_usage = ceil(gb_usage)
        bytes_ceil_usage = gb_ceil_usage * 10**9
        return max(bytes_ceil_usage, 0)

    @property
    def max_additional_quota(self):
        """Get the maximum additional quota allowed."""
        return current_app.config.get("RDM_FILES_DEFAULT_MAX_ADDITIONAL_QUOTA_SIZE", 0)

    def max_additional_quota_value(self, user_id, record=None):
        """Maximum additional quota value for a specific draft."""
        return min(self.max_additional_quota, self.remaining_storage(user_id, record))

    def remaining_storage(self, user_id, record):
        """Remaining storage for this draft and user."""
        additional_storage_user = (
            RDMRecordQuota.query.with_entities(
                func.coalesce(
                    func.sum(RDMRecordQuota.quota_size - self.default_quota(user_id)), 0
                )
            )
            .filter(RDMRecordQuota.user_id == user_id)
            .scalar()
        )

        return max(
            (self.max_additional_quota - int(additional_storage_user))
            + self.additional_storage(user_id, record),
            0,
        )

    def _search_user_resources(self, user, drafts=False):
        """Fetch user records or drafts."""
        filters = [dsl.Q("term", **{"parent.access.owned_by.user": user.id})]

        if drafts:
            filters.append(dsl.Q("term", is_published=False))
            search_fn = self.records_service.search_drafts
        else:
            search_fn = self.records_service.search

        return search_fn(
            system_identity,
            extra_filter=dsl.Q("bool", must=filters),
        )

    def _resolve_records_and_quotas(self, items, draft=False):
        """Resolve search hits and fetch quotas."""
        cls = (
            self.records_service.draft_cls if draft else self.records_service.record_cls
        )

        records = []
        parent_ids = set()

        for item in items:
            try:
                record = cls.pid.resolve(item["id"], registered_only=not draft)
                records.append((item, record))
                parent_ids.add(record.parent.id)
            except Exception as e:
                logger.warning("Failed to resolve record %s: %s", item.get("id"), e)

        quotas = {
            q.parent_id: q.quota_size
            for q in RDMRecordQuota.query.filter(
                RDMRecordQuota.parent_id.in_(parent_ids)
            ).all()
        }

        return records, quotas

    def _compute_usage(self, user, records, quotas):
        """Compute quota usage."""
        results = []
        total_extra = 0
        total_used = 0
        default_quota = self.default_quota(user)
        for item, record in records:
            pid = record.parent.id
            quota = quotas.get(pid, default_quota)

            if quota <= default_quota:
                continue

            used_bytes = record.files.total_bytes or 0
            extra_quota = quota - default_quota
            excess_usage = max(used_bytes - default_quota, 0)
            additional_used = min(excess_usage, extra_quota)

            total_extra += extra_quota
            total_used += additional_used

            results.append(
                {
                    "item": item,
                    "record": record,
                    "quota": quota,
                    "used_bytes": used_bytes,
                    "extra_quota": extra_quota,
                    "additional_used": additional_used,
                }
            )

        return results, total_extra, total_used

    def _process_resources(self, user, items, draft=False):
        """Resolve + compute in one step."""
        resolved, quotas = self._resolve_records_and_quotas(items, draft=draft)
        return self._compute_usage(user, resolved, quotas)

    def get_user_storage_usage(self, user, include_drafts=True):
        """Return raw storage usage data."""
        record_data, extra_r, used_r = self._process_resources(
            user, self._search_user_resources(user)
        )

        draft_data, extra_d, used_d = [], 0, 0
        if include_drafts:
            draft_data, extra_d, used_d = self._process_resources(
                user, self._search_user_resources(user, drafts=True), draft=True
            )
        default_quota = self.default_quota(user)
        return {
            "default_quota": default_quota,
            "max_additional_quota": self.max_additional_quota,
            "total_extra": extra_r + extra_d,
            "total_used": used_r + used_d,
            "entries": record_data + draft_data,
        }
