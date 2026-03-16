# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

import logging
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_search.engine import dsl
from invenio_rdm_records.records.models import RDMRecordQuota

logger = logging.getLogger(__name__)

class StorageService:
    """Service providing per-user storage quota information."""

    def __init__(self, records_service):
        """Constructor."""
        self.records_service = records_service

    @property
    def default_quota(self):
        """Get the default quota size from config."""
        return current_app.config.get("RDM_FILES_DEFAULT_QUOTA_SIZE", 50 * 10**9)

    @property
    def max_additional_quota(self):
        """Get the maximum additional quota allowed per user."""
        return current_app.config.get("RDM_FILES_DEFAULT_MAX_ADDITIONAL_QUOTA_SIZE") or 150 * 10**9

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
        cls = self.records_service.draft_cls if draft else self.records_service.record_cls

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

    def _compute_usage(self, records, quotas):
        """Compute quota usage."""
        results = []
        total_extra = 0
        total_used = 0

        for item, record in records:
            pid = record.parent.id
            quota = quotas.get(pid, self.default_quota)

            if quota <= self.default_quota:
                continue

            used_bytes = record.files.total_bytes or 0
            extra_quota = quota - self.default_quota
            excess_usage = max(used_bytes - self.default_quota, 0)
            additional_used = min(excess_usage, extra_quota)

            total_extra += extra_quota
            total_used += additional_used

            results.append({
                "item": item,
                "record": record,
                "quota": quota,
                "used_bytes": used_bytes,
                "extra_quota": extra_quota,
                "additional_used": additional_used,
            })

        return results, total_extra, total_used

    def _process_resources(self, items, draft=False):
        """Resolve + compute in one step."""
        resolved, quotas = self._resolve_records_and_quotas(items, draft=draft)
        return self._compute_usage(resolved, quotas)

    def get_user_storage_usage(self, user, include_drafts=True):
        """Return raw storage usage data."""
        record_data, extra_r, used_r = self._process_resources(
            self._search_user_resources(user)
        )

        draft_data, extra_d, used_d = [], 0, 0
        if include_drafts:
            draft_data, extra_d, used_d = self._process_resources(
                self._search_user_resources(user, drafts=True),
                draft=True
            )

        return {
            "default_quota": self.default_quota,
            "max_additional_quota": self.max_additional_quota,
            "total_extra": extra_r + extra_d,
            "total_used": used_r + used_d,
            "entries": record_data + draft_data,
        }
