#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Remove PIDRelations tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "a3957490361d"
down_revision = "88d1463de5c0"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    try:
        # The table is not used and has no data.
        op.drop_table("pidrelations_pidrelation")
    except Exception:
        pass


def downgrade():
    """Downgrade database."""
    # no turning back
    pass
