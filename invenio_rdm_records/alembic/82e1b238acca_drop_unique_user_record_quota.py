#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Remove user unique constraint from record quotas."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "82e1b238acca"
down_revision = "ff9bec971d30"
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
