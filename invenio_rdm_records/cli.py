# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Command-line tools for demo module."""

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import \
    current_service as current_vocabularies_service

from invenio_rdm_records.proxies import current_rdm_records

from .fixtures import FixturesEngine
from .fixtures.demo import create_fake_record, create_fake_request
from .fixtures.tasks import create_demo_record, create_demo_request
from invenio_communities.fixtures.demo import create_fake_community
from invenio_communities.fixtures.tasks import create_demo_community
from faker import Faker


@click.group()
def rdm_records():
    """InvenioRDM records commands."""


@rdm_records.command('demo')
@with_appcontext
def demo():
    """Create 100 fake records and requests for demo purposes."""
    click.secho('Creating demo records...', fg='green')

    faker = Faker()
    community = create_fake_community(faker)
    create_demo_community(community)

    for index in range(100):
        fake_data = create_fake_record()
        draft_id = create_demo_record.delay(fake_data)
        fake_data = create_fake_request(draft_id, community.id, index)
        create_demo_request.delay(fake_data)

    click.secho('Created records and requests!', fg='green')


@rdm_records.command('fixtures')
@with_appcontext
def create_fixtures():
    """Create the fixtures required for record creation."""
    click.secho('Creating required fixtures...', fg='green')

    FixturesEngine(system_identity).run()

    click.secho('Created required fixtures!', fg='green')


@rdm_records.command("rebuild-index")
@with_appcontext
def rebuild_index():
    """Reindex all drafts, records and vocabularies."""
    click.secho("Reindexing records and drafts...", fg="green")

    rec_service = current_rdm_records.records_service
    rec_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing vocabularies...", fg="green")

    vocab_service = current_vocabularies_service
    vocab_service.rebuild_index(identity=system_identity)

    click.secho("Reindexed records and vocabularies!", fg="green")
