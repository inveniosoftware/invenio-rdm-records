# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2022 CERN.
# Copyright (C) 2019-2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Command-line tools for demo module."""

import click
from flask.cli import with_appcontext
from flask_security.utils import hash_password
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_communities import current_communities
from invenio_db import db
from invenio_records_resources.proxies import current_service_registry

from invenio_rdm_records.proxies import current_rdm_records, \
    current_rdm_records_service

from .fixtures import FixturesEngine
from .fixtures.demo import create_fake_community, create_fake_record
from .fixtures.tasks import create_demo_community, \
    create_demo_inclusion_requests, create_demo_invitation_requests, \
    create_demo_record, get_authenticated_identity

COMMUNITY_OWNER_EMAIL = "community@demo.org"
USER_EMAIL = "user@demo.org"
HELP_MSG_USER = "User e-mail of an already existing user."


def _get_or_create_user(email):
    user = current_datastore.get_user(email)
    if not user:
        with db.session.begin_nested():
            user = current_datastore.create_user(
                email=email,
                password=hash_password("123456"),
                active=True
            )
        db.session.commit()
    return user


@click.group()
def rdm_records():
    """InvenioRDM records commands."""


@rdm_records.group(invoke_without_command=True)
@click.pass_context
def demo(ctx):
    """Create fake demo data."""
    # The `demo` cmd is now a `group` with multiple subcmds, instead of
    # creating records as before.
    # To ensure backward compat, when invoked without subcmds it will run
    # the `demo records` cmd.
    if ctx.invoked_subcommand is None:
        ctx.invoke(records)


@demo.command("records")
@click.option("-u", "--user", "user_email", default=USER_EMAIL,
              show_default=True, help=HELP_MSG_USER)
@click.option("-r", "--records", "n_records", default=100,
              show_default=True, help="Number of fake records to create")
@with_appcontext
def records(user_email, n_records):
    """Create fake records."""
    user = _get_or_create_user(user_email)
    click.secho("Creating demo records for {0}...".format(user), fg="green")

    for _ in range(n_records):
        fake_data = create_fake_record()
        create_demo_record.delay(user.id, fake_data, publish=True)

    click.secho("Demo records task submitted...", fg="green")


@demo.command("drafts")
@click.option("-u", "--user", "user_email", default=USER_EMAIL,
              show_default=True, help=HELP_MSG_USER)
@click.option("-d", "--drafts", "n_drafts", default=20,
              show_default=True, help="Number of fake drafts to create")
@with_appcontext
def drafts(user_email, n_drafts):
    """Create fake drafts."""
    user = _get_or_create_user(user_email)
    click.secho("Creating demo drafts for {0}...".format(user), fg="green")

    for _ in range(n_drafts):
        fake_data = create_fake_record()
        create_demo_record.delay(user.id, fake_data, publish=False)

    click.secho("Demo drafts task submitted...", fg="green")


@demo.command("communities")
@click.option("-u", "--user", "user_email", default=COMMUNITY_OWNER_EMAIL,
              show_default=True, help=HELP_MSG_USER)
@click.option("-c", "--communities", "n_communities", default=5,
              show_default=True, help="Number of fake communities to create")
@with_appcontext
def communities(user_email, n_communities):
    """Create fake communities."""
    user = _get_or_create_user(user_email)
    click.secho("Creating demo communities for owner {0}...".format(user),
                fg="green")

    for _ in range(n_communities):
        fake_data = create_fake_community()
        create_demo_community.delay(user.id, fake_data)

    click.secho("Demo communities task submitted...", fg="green")


@demo.command("inclusion-requests")
@click.option("-u", "--user", "user_email", default=USER_EMAIL,
              show_default=True, help=HELP_MSG_USER)
@click.option("-i", "--requests", "n_requests", default=5,
              show_default=True,
              help="Number of fake inclusion requests to create")
@with_appcontext
def inclusion_requests(user_email, n_requests):
    """Create fake requests to include drafts to communities."""
    user = _get_or_create_user(user_email)
    click.secho("Creating demo inclusions requests for {0}...".format(user),
                fg="green")

    identity = get_authenticated_identity(user.id)
    drafts = current_rdm_records_service.search_drafts(identity,
                                                       is_published=False,
                                                       q="versions.index:1")
    if drafts.total == 0:
        click.secho("Failed! Create fake drafts first "
                    "with `rdm-records demo drafts`.", fg="red")
        return

    communities = current_communities.service.search(system_identity)
    if communities.total == 0:
        click.secho("Failed! Create fake communities "
                    "first `rdm-records demo communities`.", fg="red")
        return

    create_demo_inclusion_requests.delay(user.id, n_requests)

    click.secho("Demo inclusion requests task submitted...", fg="green")


@demo.command("invitation-requests")
@click.option("-u", "--user", "user_email", default=USER_EMAIL,
              show_default=True, help=HELP_MSG_USER)
@click.option("-m", "--requests", "n_requests", default=5,
              show_default=True,
              help="Number of fake invitation requests to create")
@with_appcontext
def invitation_requests(user_email, n_requests):
    """Create fake invitation requests to a community."""
    user = _get_or_create_user(user_email)
    click.secho("Creating demo invitation requests for {0}...".format(user),
                fg="green")

    communities = current_communities.service.search(system_identity)
    if communities.total == 0:
        click.secho(
            "Failed! Create fake communities "
            "first `rdm-records demo communities`.",
            fg="red")
        return

    create_demo_invitation_requests.delay(user.id, n_requests)

    click.secho("Demo invitation requests task submitted...", fg="green")


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

    vocab_service = current_service_registry.get("vocabularies")
    vocab_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing subjects...", fg="green")

    subj_service = current_service_registry.get("subjects")
    subj_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing affiliations...", fg="green")

    affs_service = current_service_registry.get("affiliations")
    affs_service.rebuild_index(identity=system_identity)

    click.secho("Reindexed records and vocabularies!", fg="green")
