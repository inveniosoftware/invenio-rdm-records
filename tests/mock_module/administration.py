# SPDX-FileCopyrightText: 2026 Northwestern University.
# SPDX-License-Identifier: MIT

"""Fake administration views."""

from invenio_administration.views.base import (
    AdminResourceListView,
)


class RecordAdminListView(AdminResourceListView):
    """Configuration for the records list view."""

    name = "records"
    resource_config = "records_resource"
    extension_name = "invenio-rdm-records"


class DraftAdminListView(AdminResourceListView):
    """Configuration for the drafts list view."""

    name = "drafts"
    resource_config = "records_resource"
    extension_name = "invenio-rdm-records"


class UserModerationListView(AdminResourceListView):
    """User moderation admin search view."""

    name = "moderation"
    resource_config = "requests_resource"
    extension_name = "invenio-requests"
