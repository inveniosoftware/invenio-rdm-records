# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from flask import current_app
from flask_security import current_user
from invenio_access.permissions import system_identity
from invenio_search.engine import dsl

from invenio_rdm_records.records.models import RDMRecordQuota

DEFAULT_TOTAL_ALLOWED_QUOTA = 150 * 10**9  # 150 GB

class StorageService:
    """Service providing per-user storage quota information."""

    def __init__(self, records_service):
        self.records_service = records_service

    @property
    def default_quota(self):
        return current_app.config.get("RDM_FILES_DEFAULT_QUOTA_SIZE", 50 * 10**9)

    def _search_user_items(self, user, drafts=False):
        """Get all records or drafts for a user."""
        filters = [dsl.Q("term", **{"parent.access.owned_by.user": user.id})]

        if drafts:
            filters.append(dsl.Q("term", is_published=False))
            combined_filter = dsl.Q("bool", must=filters)
            return self.records_service.search_drafts(
                system_identity,
                extra_filter=combined_filter,
                size=1000
            )

        combined_filter = dsl.Q("bool", must=filters)
        return self.records_service.search(
            system_identity,
            extra_filter=combined_filter,
            size=1000
        )

    def _get_entities_and_quotas(self, items, draft=False):
        cls = self.records_service.draft_cls if draft else self.records_service.record_cls
        results = []
        parent_ids = []

        for item in items:
            try:
                entity = cls.pid.resolve(item["id"], registered_only=not draft)
                results.append((item, entity))
                parent_ids.append(entity.parent.id)
            except Exception:
                continue

        # fetch all quotas in one go
        quotas = {q.parent_id: q.quota_size for q in RDMRecordQuota.query.filter(
            RDMRecordQuota.parent_id.in_(parent_ids)
        ).all()}

        return results, quotas

    def _calculate_rows(self, items_with_entities, quotas):
        rows, total_extra, total_used = [], 0, 0
        default_quota = self.default_quota

        for item, entity in items_with_entities:
            pid = entity.parent.id
            quota = quotas.get(pid, default_quota)
            if quota <= default_quota:
                continue

            used_bytes = entity.files.total_bytes or 0
            extra_quota = quota - default_quota
            additional_used = max(min(used_bytes - default_quota, extra_quota), 0)

            total_extra += extra_quota
            total_used += additional_used

            rows.append({
                "title": item.get("metadata", {}).get("title", "Empty title"),
                "url": item["links"]["self_html"],
                "additional_quota": round(extra_quota / 1e9, 2),
                "used": round(used_bytes / 1e9, 2),
                "total": round((default_quota + extra_quota) / 1e9, 2),
                "date": item.get("metadata", {}).get("publication_date", ""),
                "status": "Draft" if not entity.is_published else "Published"
            })

        return rows, total_extra, total_used

    def get_user_storage(self, user=None):
        user = user or current_user

        records = self._search_user_items(user)
        drafts = self._search_user_items(user, drafts=True)

        record_entities, record_quotas = self._get_entities_and_quotas(records)
        draft_entities, draft_quotas = self._get_entities_and_quotas(drafts, draft=True)

        record_rows, extra_r, used_r = self._calculate_rows(record_entities, record_quotas)
        draft_rows, extra_d, used_d = self._calculate_rows(draft_entities, draft_quotas)

        total_extra = extra_r + extra_d
        total_used = used_r + used_d

        return {
            "default_quota": round(self.default_quota / 1e9, 2),
            "total_allowed_quota": round(DEFAULT_TOTAL_ALLOWED_QUOTA / 1e9, 2),
            "additional_granted_quota": round(total_extra / 1e9, 2),
            "additional_used_quota": round(total_used / 1e9, 2),
            "additional_available_quota": round((DEFAULT_TOTAL_ALLOWED_QUOTA - total_extra) / 1e9, 2),
            "records": record_rows + draft_rows
        }