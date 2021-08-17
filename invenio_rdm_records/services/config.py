# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C)      2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from functools import partial

from flask_babelex import gettext as _
from invenio_drafts_resources.services.records.components import \
    DraftFilesComponent, PIDComponent
from invenio_drafts_resources.services.records.config import \
    RecordServiceConfig, SearchDraftsOptions, SearchOptions, \
    SearchVersionsOptions, is_draft, is_record
from invenio_records_resources.services import ConditionalLink, \
    FileServiceConfig
from invenio_records_resources.services.base.links import Link
from invenio_records_resources.services.files.links import FileLink
from invenio_records_resources.services.records.links import RecordLink

from ..records import RDMDraft, RDMRecord
from . import facets
from .components import AccessComponent, ExternalPIDsComponent, \
    MetadataComponent, RelationsComponent
from .customizations import FileConfigMixin, RecordConfigMixin, \
    SearchOptionsMixin
from .permissions import RDMRecordPermissionPolicy
from .pids.providers import DOIDataCiteClient, DOIDataCitePIDProvider, \
    UnmanagedPIDProvider
from .result_items import SecretLinkItem, SecretLinkList
from .schemas import RDMParentSchema, RDMRecordSchema
from .schemas.parent.access import SecretLink


#
# Default search configuration
#
class RDMSearchOptions(SearchOptions, SearchOptionsMixin):
    """Search options for record search."""

    facets = {
        'resource_type': facets.resource_type,
        'languages': facets.language,
        'access_status': facets.access_status,
    }


class RDMSearchDraftsOptions(SearchDraftsOptions, SearchOptionsMixin):
    """Search options for drafts search."""

    facets = {
        'resource_type': facets.resource_type,
        'languages': facets.language,
        'access_status': facets.access_status,
        'is_published': facets.is_published,
    }


class RDMSearchVersionsOptions(SearchVersionsOptions, SearchOptionsMixin):
    """Search options for record versioning search."""


#
# Default service configuration
#
class RDMRecordServiceConfig(RecordServiceConfig, RecordConfigMixin):
    """RDM record draft service config."""

    # Record and draft classes
    record_cls = RDMRecord
    draft_cls = RDMDraft

    # Schemas
    schema = RDMRecordSchema
    schema_parent = RDMParentSchema
    schema_secret_link = SecretLink

    # Permission policy
    permission_policy_cls = RDMRecordPermissionPolicy

    # Result classes
    link_result_item_cls = SecretLinkItem
    link_result_list_cls = SecretLinkList

    # Search configuration
    search = RDMSearchOptions
    search_drafts = RDMSearchDraftsOptions
    search_versions = RDMSearchVersionsOptions

    # PIDs providers
    pids_providers = {
        "doi": {
            "datacite": {
                "provider": DOIDataCitePIDProvider,
                "required": True,
                "system_managed": True,
            },
            "external": {
                "provider": partial(UnmanagedPIDProvider, pid_type="doi"),
                "required": False,
                "system_managed": False,
            },
        },
    }

    pids_providers_clients = {
        "datacite": DOIDataCiteClient
    }

    # Components - order matters!
    components = [
        MetadataComponent,
        AccessComponent,
        DraftFilesComponent,
        # for the internal `pid` field
        PIDComponent,
        # for the `pids` field (external PIDs)
        ExternalPIDsComponent,
        RelationsComponent,
    ]

    # Links
    links_item = {
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/records/{id}"),
            else_=RecordLink("{+api}/records/{id}/draft"),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+ui}/records/{id}"),
            else_=RecordLink("{+ui}/uploads/{id}"),
        ),
        # TODO: only include link when DOI support is enabled.
        "self_doi": Link(
            "{+ui}/doi/{pid_doi}",
            # when=lambda record, ctx: "doi" in record.pids.keys(),
            when=is_record,
            vars=lambda record, vars: vars.update({
                f"pid_{scheme}": pid["identifier"]
                for (scheme, pid) in record.pids.items()
            })
        ),
        "files": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/records/{id}/files"),
            else_=RecordLink("{+api}/records/{id}/draft/files"),
        ),
        "latest": RecordLink(
            "{+api}/records/{id}/versions/latest",
            when=is_record
        ),
        "latest_html": RecordLink(
            "{+ui}/records/{id}/latest",
            when=is_record
        ),
        "draft": RecordLink("{+api}/records/{id}/draft", when=is_record),
        "record": RecordLink("{+api}/records/{id}", when=is_draft),
        # TODO: record_html temporarily needed for DOI registration, until
        # problems with self_doi has been fixed
        "record_html": RecordLink("{+ui}/records/{id}", when=is_draft),
        "publish": RecordLink(
            "{+api}/records/{id}/draft/actions/publish",
            when=is_draft
        ),
        "versions": RecordLink("{+api}/records/{id}/versions"),
        "access_links": RecordLink("{+api}/records/{id}/access/links"),
        # TODO: only include link when DOI support is enabled.
        "reserve_doi": RecordLink("{+api}/records/{id}/draft/pids/doi")
    }


class RDMFileRecordServiceConfig(FileServiceConfig, FileConfigMixin):
    """Configuration for record files."""

    record_cls = RDMRecord
    permission_policy_cls = RDMRecordPermissionPolicy


class RDMFileDraftServiceConfig(FileServiceConfig, FileConfigMixin):
    """Configuration for draft files."""

    record_cls = RDMDraft
    permission_action_prefix = "draft_"
    permission_policy_cls = RDMRecordPermissionPolicy

    file_links_list = {
        "self": RecordLink("{+api}/records/{id}/draft/files"),
    }

    file_links_item = {
        "self": FileLink("{+api}/records/{id}/draft/files/{key}"),
        "content": FileLink("{+api}/records/{id}/draft/files/{key}/content"),
        "commit": FileLink("{+api}/records/{id}/draft/files/{key}/commit"),
    }
