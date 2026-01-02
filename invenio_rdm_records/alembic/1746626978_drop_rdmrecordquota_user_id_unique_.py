#
# This file is part of Invenio.
# Copyright (C) 2025 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Drop ``RDMRecordQuota.user_id`` unique constraint."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "1746626978"
down_revision = "425b691f768b"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.drop_constraint(
        "uq_rdm_records_quota_user_id", "rdm_records_quota", type_="unique"
    )


def downgrade():
    """Downgrade database."""
    op.create_unique_constraint(
        "uq_rdm_records_quota_user_id", "rdm_records_quota", ["user_id"]
    )
