# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create parent record table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy_utils import JSONType, UUIDType

# revision identifiers, used by Alembic.
revision = '88d1463de5c0'
down_revision = '4a15e8671f4d'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        'rdm_parents_metadata',
        sa.Column(
            'created',
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'),
            nullable=False,
        ),
        sa.Column(
            'updated',
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'),
            nullable=False,
        ),
        sa.Column(
            'id',
            UUIDType(),
            nullable=False,
        ),
        sa.Column(
            'json',
            sa.JSON()
            .with_variant(JSONType(), 'mysql')
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
                'postgresql'
            )
            .with_variant(JSONType(), 'sqlite'),
            nullable=True,
        ),
        sa.Column(
            'version_id',
            sa.Integer(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            'id',
            name=op.f('pk_rdm_parents_metadata'),
        ),
    )

    # Drafts table FK to parent
    op.add_column(
        'rdm_drafts_metadata',
        sa.Column('parent_id', UUIDType(), nullable=True)
    )
    op.create_foreign_key(
        op.f('fk_rdm_drafts_metadata_parent_id_rdm_parents_metadata'),
        'rdm_drafts_metadata',
        'rdm_parents_metadata',
        ['parent_id'],
        ['id'],
        ondelete='RESTRICT',
    )
    op.add_column(
        'rdm_drafts_metadata',
        sa.Column('index', sa.Integer, nullable=True)
    )

    # Records table FK to parent
    op.add_column(
        'rdm_records_metadata',
        sa.Column('parent_id', UUIDType(), nullable=True)
    )
    op.create_foreign_key(
        op.f('fk_rdm_records_metadata_parent_id_rdm_parents_metadata'),
        'rdm_records_metadata',
        'rdm_parents_metadata',
        ['parent_id'],
        ['id'],
        ondelete='RESTRICT',
    )
    op.add_column(
        'rdm_records_metadata',
        sa.Column('index', sa.Integer, nullable=True)
    )

    # Records revisions table FK to parent
    op.add_column(
        'rdm_records_metadata_version',
        sa.Column('parent_id', UUIDType(), nullable=True)
    )
    op.add_column(
        'rdm_records_metadata_version',
        sa.Column('index', sa.Integer, nullable=True)
    )

    # Create versions state table
    op.create_table(
        'rdm_versions_state',
        sa.Column('latest_index', sa.Integer(), nullable=True),
        sa.Column('parent_id', UUIDType(), nullable=False),
        sa.Column('latest_id', UUIDType(), nullable=True),
        sa.Column('next_draft_id', UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ['latest_id'],
            ['rdm_records_metadata.id'],
            name=op.f('fk_rdm_versions_state_latest_id_rdm_records_metadata'),
        ),
        sa.ForeignKeyConstraint(
            ['next_draft_id'],
            ['rdm_drafts_metadata.id'],
            name=op.f(
                'fk_rdm_versions_state_next_draft_id_rdm_drafts_metadata'),
        ),
        sa.ForeignKeyConstraint(
            ['parent_id'],
            ['rdm_parents_metadata.id'],
            name=op.f('fk_rdm_versions_state_parent_id_rdm_parents_metadata'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint(
            'parent_id',
            name=op.f('pk_rdm_versions_state')
        ),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('rdm_versions_state')
    op.drop_column('rdm_records_metadata_version', 'parent_id')
    op.drop_column('rdm_records_metadata_version', 'index')
    op.drop_constraint(
        op.f('fk_rdm_records_metadata_parent_id_rdm_parents_metadata'),
        'rdm_records_metadata',
        type_='foreignkey'
    )
    op.drop_column('rdm_records_metadata', 'parent_id')
    op.drop_column('rdm_records_metadata', 'index')
    op.drop_constraint(
        op.f('fk_rdm_drafts_metadata_parent_id_rdm_parents_metadata'),
        'rdm_drafts_metadata',
        type_='foreignkey'
    )
    op.drop_column('rdm_drafts_metadata', 'parent_id')
    op.drop_column('rdm_drafts_metadata', 'index')
    op.drop_table('rdm_parents_metadata')
