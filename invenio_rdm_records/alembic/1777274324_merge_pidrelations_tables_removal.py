#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Merge PIDRelations tables removal to single head."""

# revision identifiers, used by Alembic.
revision = "1777274324"
down_revision = ("912251a56a49", "a3957490361d")
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""


def downgrade():
    """Downgrade database."""
