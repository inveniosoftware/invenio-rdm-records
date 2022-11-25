# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2022 CERN.
# Copyright (C) 2019-2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Command-line tools for demo module."""

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_communities import current_communities
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.custom_fields.errors import (
    CustomFieldsException,
)
from invenio_records_resources.services.custom_fields.mappings import Mapping
from invenio_records_resources.services.custom_fields.validate import (
    validate_custom_fields,
)
from invenio_search import current_search_client
from invenio_search.engine import dsl, search
from invenio_search.utils import build_alias_name

from invenio_rdm_records.proxies import current_rdm_records, current_rdm_records_service

from .fixtures import FixturesEngine
from .fixtures.demo import (
    create_fake_community,
    create_fake_oai_set,
    create_fake_record,
)
from .fixtures.tasks import (
    create_demo_community,
    create_demo_inclusion_requests,
    create_demo_invitation_requests,
    create_demo_oaiset,
    create_demo_record,
    get_authenticated_identity,
)
from .utils import get_or_create_user

COMMUNITY_OWNER_EMAIL = "community@demo.org"
USER_EMAIL = "user@demo.org"
HELP_MSG_USER = "User e-mail of an already existing user."
ADMIN_EMAIL = "admin@inveniosoftware.org"


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
@click.option(
    "-u",
    "--user",
    "user_email",
    default=USER_EMAIL,
    show_default=True,
    help=HELP_MSG_USER,
)
@click.option(
    "-r",
    "--records",
    "n_records",
    default=100,
    show_default=True,
    help="Number of fake records to create",
)
@with_appcontext
def records(user_email, n_records):
    """Create fake records."""
    user = get_or_create_user(user_email)
    click.secho("Creating demo records for {0}...".format(user), fg="green")

    for _ in range(n_records):
        fake_data = create_fake_record()
        create_demo_record.delay(user.id, fake_data, publish=True)

    click.secho("Demo records task submitted...", fg="green")


@demo.command("oai-sets")
@click.option(
    "-u",
    "--user",
    "user_email",
    default=ADMIN_EMAIL,
    show_default=True,
    help=HELP_MSG_USER,
)
@click.option(
    "-r",
    "--records",
    "n_records",
    default=100,
    show_default=True,
    help="Number of fake oai sets to create",
)
@with_appcontext
def oai_sets(user_email, n_records):
    """Create fake records."""
    user = get_or_create_user(user_email)
    click.secho("Creating demo oaipmh sets for {0}...".format(user), fg="green")

    for _ in range(n_records):
        fake_data = create_fake_oai_set()
        create_demo_oaiset.delay(user.id, fake_data)

    click.secho("Demo records task submitted...", fg="green")


@demo.command("drafts")
@click.option(
    "-u",
    "--user",
    "user_email",
    default=USER_EMAIL,
    show_default=True,
    help=HELP_MSG_USER,
)
@click.option(
    "-d",
    "--drafts",
    "n_drafts",
    default=20,
    show_default=True,
    help="Number of fake drafts to create",
)
@with_appcontext
def drafts(user_email, n_drafts):
    """Create fake drafts."""
    user = get_or_create_user(user_email)
    click.secho("Creating demo drafts for {0}...".format(user), fg="green")

    for _ in range(n_drafts):
        fake_data = create_fake_record()
        create_demo_record.delay(user.id, fake_data, publish=False)

    click.secho("Demo drafts task submitted...", fg="green")


@demo.command("communities")
@click.option(
    "-u",
    "--user",
    "user_email",
    default=COMMUNITY_OWNER_EMAIL,
    show_default=True,
    help=HELP_MSG_USER,
)
@click.option(
    "-c",
    "--communities",
    "n_communities",
    default=5,
    show_default=True,
    help="Number of fake communities to create",
)
@with_appcontext
def communities(user_email, n_communities):
    """Create fake communities."""
    user = get_or_create_user(user_email)
    click.secho("Creating demo communities for owner {0}...".format(user), fg="green")

    for _ in range(n_communities):
        fake_data = create_fake_community()
        create_demo_community.delay(user.id, fake_data)

    click.secho("Demo communities task submitted...", fg="green")


@demo.command("inclusion-requests")
@click.option(
    "-u",
    "--user",
    "user_email",
    default=USER_EMAIL,
    show_default=True,
    help=HELP_MSG_USER,
)
@click.option(
    "-i",
    "--requests",
    "n_requests",
    default=5,
    show_default=True,
    help="Number of fake inclusion requests to create",
)
@with_appcontext
def inclusion_requests(user_email, n_requests):
    """Create fake requests to include drafts to communities."""
    user = get_or_create_user(user_email)
    click.secho("Creating demo inclusions requests for {0}...".format(user), fg="green")

    identity = get_authenticated_identity(user.id)
    drafts = current_rdm_records_service.search_drafts(
        identity, is_published=False, q="versions.index:1"
    )
    if drafts.total == 0:
        click.secho(
            "Failed! Create fake drafts first " "with `rdm-records demo drafts`.",
            fg="red",
        )
        exit(1)

    communities = current_communities.service.search(system_identity)
    if communities.total == 0:
        click.secho(
            "Failed! Create fake communities " "first `rdm-records demo communities`.",
            fg="red",
        )
        exit(1)

    create_demo_inclusion_requests.delay(user.id, n_requests)

    click.secho("Demo inclusion requests task submitted...", fg="green")


@demo.command("invitation-requests")
@click.option(
    "-u",
    "--user",
    "user_email",
    default=USER_EMAIL,
    show_default=True,
    help=HELP_MSG_USER,
)
@click.option(
    "-m",
    "--requests",
    "n_requests",
    default=5,
    show_default=True,
    help="Number of fake invitation requests to create",
)
@with_appcontext
def invitation_requests(user_email, n_requests):
    """Create fake invitation requests to a community."""
    user = get_or_create_user(user_email)
    click.secho("Creating demo invitation requests for {0}...".format(user), fg="green")

    communities = current_communities.service.search(system_identity)
    if communities.total == 0:
        click.secho(
            "Failed! Create fake communities " "first `rdm-records demo communities`.",
            fg="red",
        )
        exit(1)

    create_demo_invitation_requests.delay(user.id, n_requests)

    click.secho("Demo invitation requests task submitted...", fg="green")


@rdm_records.command("fixtures")
@with_appcontext
def create_fixtures():
    """Create the fixtures required for record creation."""
    click.secho("Creating required fixtures...", fg="green")

    FixturesEngine(system_identity).run()

    click.secho("Created required fixtures!", fg="green")


@rdm_records.command("rebuild-index")
@with_appcontext
def rebuild_index():
    """Reindex all drafts, records and vocabularies."""
    click.secho("Reindexing vocabularies...", fg="green")
    vocab_service = current_service_registry.get("vocabularies")
    vocab_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing names...", fg="green")
    names_service = current_service_registry.get("names")
    names_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing funders...", fg="green")
    funders_service = current_service_registry.get("funders")
    funders_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing awards...", fg="green")
    awards_service = current_service_registry.get("awards")
    awards_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing subjects...", fg="green")
    subj_service = current_service_registry.get("subjects")
    subj_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing affiliations...", fg="green")
    affs_service = current_service_registry.get("affiliations")
    affs_service.rebuild_index(identity=system_identity)

    click.secho("Reindexing records and drafts...", fg="green")
    rec_service = current_rdm_records.records_service
    rec_service.rebuild_index(identity=system_identity)

    click.secho("Reindexed records and vocabularies!", fg="green")


# CUSTOM FIELDS


@rdm_records.group()
def custom_fields():
    """InvenioRDM custom fields commands."""


@custom_fields.command("init")
@click.option(
    "-f",
    "--field-name",
    type=str,
    required=False,
    multiple=True,
    help="A custom field name to create. If not provided, all custom fields will be created.",
)
@with_appcontext
def create_records_custom_field(field_name):
    """Creates one or all custom fields for records.

    $ invenio custom-fields records create [field].
    """
    available_fields = current_app.config.get("RDM_CUSTOM_FIELDS")
    if not available_fields:
        click.secho("No custom fields were configured. Exiting...", fg="green")
        exit(0)

    namespaces = set(current_app.config.get("RDM_NAMESPACES").keys())
    try:
        validate_custom_fields(
            given_fields=field_name,
            available_fields=available_fields,
            namespaces=namespaces,
        )
    except CustomFieldsException as e:
        click.secho(
            f"Custom fields configuration is not valid. {e.description}", fg="red"
        )
        exit(1)

    click.secho("Creating custom fields...", fg="green")
    # multiple=True makes it an iterable
    properties = Mapping.properties_for_fields(field_name, available_fields)

    try:
        record_index = dsl.Index(
            build_alias_name(
                current_rdm_records.records_service.config.record_cls.index._name,
            ),
            using=current_search_client,
        )
        draft_index = dsl.Index(
            build_alias_name(
                current_rdm_records.records_service.config.draft_cls.index._name,
            ),
            using=current_search_client,
        )

        record_index.put_mapping(body={"properties": properties})
        draft_index.put_mapping(body={"properties": properties})
        click.secho("Created all custom fields!", fg="green")
    except search.RequestError as e:
        click.secho("An error occured while creating custom fields.", fg="red")
        click.secho(e.info["error"]["reason"], fg="red")


@custom_fields.command("exists")
@click.option(
    "-f",
    "--field-name",
    type=str,
    required=True,
    multiple=False,
    help="A custom field name to check.",
)
@with_appcontext
def custom_field_exists_in_records(field_name):
    """Checks if a custom field exists in records search mapping.

    $ invenio custom-fields records exists <field name>.
    """
    click.secho("Checking custom field...", fg="green")
    record_index = dsl.Index(
        build_alias_name(
            current_rdm_records.records_service.config.record_cls.index._name,
        ),
        using=current_search_client,
    )
    draft_index = dsl.Index(
        build_alias_name(
            current_rdm_records.records_service.config.draft_cls.index._name,
        ),
        using=current_search_client,
    )

    # check if exists in all both records and draft indices
    exists_in_record = Mapping.field_exists(f"custom_fields.{field_name}", record_index)
    exists_in_draft = Mapping.field_exists(f"custom_fields.{field_name}", draft_index)
    if exists_in_record and exists_in_draft:
        click.secho(f"Field {field_name} exists", fg="green")
    else:
        click.secho(f"Field {field_name} does not exist", fg="red")
