#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Remove PIDRelations tables."""

from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "a3957490361d"
down_revision = "88d1463de5c0"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    ctx = op.get_context()
    inspector = Inspector.from_engine(ctx.connection.engine)
    tables = inspector.get_table_names()
    if "pidrelations_pidrelation" in tables:
        op.drop_table("pidrelations_pidrelation")


def downgrade():
    """Downgrade database."""
    # no turning back
    pass
