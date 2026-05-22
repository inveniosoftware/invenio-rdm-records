# SPDX-FileCopyrightText: 2016-2025 CERN.
# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alter datetime columns to utc aware datetime columns."""

from invenio_db.utils import (
    update_table_columns_column_type_to_datetime,
    update_table_columns_column_type_to_utc_datetime,
)

# revision identifiers, used by Alembic.
revision = "912251a56a49"
down_revision = "1746626978"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    for table_name in [
        "rdm_records_quota",
        "rdm_users_quota",
        "rdm_parents_metadata",
        "rdm_records_metadata",
        "rdm_records_files",
        "rdm_records_media_files",
        "rdm_drafts_files",
        "rdm_drafts_media_files",
        "rdm_drafts_metadata",
        "rdm_records_files_version",
        "rdm_records_media_files_version",
        "rdm_records_metadata_version",
    ]:
        update_table_columns_column_type_to_utc_datetime(table_name, "created")
        update_table_columns_column_type_to_utc_datetime(table_name, "updated")
    update_table_columns_column_type_to_utc_datetime(
        "rdm_records_secret_links", "created"
    )
    update_table_columns_column_type_to_utc_datetime(
        "rdm_records_secret_links", "expires_at"
    )
    update_table_columns_column_type_to_utc_datetime(
        "rdm_records_access_request_tokens", "created"
    )
    update_table_columns_column_type_to_utc_datetime(
        "rdm_records_access_request_tokens", "expires_at"
    )
    update_table_columns_column_type_to_utc_datetime(
        "rdm_drafts_metadata", "expires_at"
    )


def downgrade():
    """Downgrade database."""
    for table_name in [
        "rdm_records_quota",
        "rdm_users_quota",
        "rdm_parents_metadata",
        "rdm_records_metadata",
        "rdm_records_files",
        "rdm_records_media_files",
        "rdm_drafts_files",
        "rdm_drafts_media_files",
        "rdm_drafts_metadata",
        "rdm_records_files_version",
        "rdm_records_media_files_version",
        "rdm_records_metadata_version",
    ]:
        update_table_columns_column_type_to_datetime(table_name, "created")
        update_table_columns_column_type_to_datetime(table_name, "updated")
    update_table_columns_column_type_to_datetime("rdm_records_secret_links", "created")
    update_table_columns_column_type_to_datetime(
        "rdm_records_secret_links", "expires_at"
    )
    update_table_columns_column_type_to_datetime(
        "rdm_records_access_request_tokens", "created"
    )
    update_table_columns_column_type_to_datetime(
        "rdm_records_access_request_tokens", "expires_at"
    )
    update_table_columns_column_type_to_datetime("rdm_drafts_metadata", "expires_at")
