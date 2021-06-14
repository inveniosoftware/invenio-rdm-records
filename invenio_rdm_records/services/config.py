# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C)      2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

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
from invenio_records_resources.services.records.facets import \
    RecordRelationLabels, TermsFacet
from invenio_records_resources.services.records.links import RecordLink
from invenio_vocabularies.services.facets import NestedVocabularyTermsFacet, \
    VocabularyLabels

from ..records import RDMDraft, RDMRecord
from ..records.systemfields.access.field.record import AccessStatusEnum
from .components import AccessComponent, ExternalPIDsComponent, \
    MetadataComponent, RelationsComponent
from .permissions import RDMRecordPermissionPolicy
from .pids.providers import DOIDataCiteClient, DOIDataCitePIDProvider, \
    UnmanagedPIDProvider
from .result_items import SecretLinkItem, SecretLinkList
from .schemas import RDMParentSchema, RDMRecordSchema
from .schemas.parent.access import SecretLink

#
# Facet definitions
#
resource_type_facet = NestedVocabularyTermsFacet(
    field='metadata.resource_type.id',
    label=_("Resource types"),
    value_labels=VocabularyLabels('resource_types')
)

language_facet = TermsFacet(
    field='metadata.languages.id',
    label=_('Languages'),
    value_labels=VocabularyLabels('languages')
)

subject_facet = TermsFacet(
    field='metadata.subjects.id',
    label=_('Subjects'),
    value_labels=VocabularyLabels('subjects')
)

access_status_facet = TermsFacet(
    field='access.status',
    label=_("Access status"),
    value_labels={
        AccessStatusEnum.OPEN.value: _("Open"),
        AccessStatusEnum.EMBARGOED.value: _("Embargoed"),
        AccessStatusEnum.RESTRICTED.value: _("Restricted"),
        AccessStatusEnum.METADATA_ONLY.value: _("Metadata-only"),
    }
)

is_published_facet = TermsFacet(
    field='is_published',
    label=_('State'),
    value_labels={"true": _("Published"), "false": _("Unpublished")}
)


#
# Search options
#
class RDMSearchOptions(SearchOptions):
    """Search options for record search."""

    facets = {
        'resource_type': resource_type_facet,
        'languages': language_facet,
        'subjects': subject_facet,
    }


class RDMSearchDraftsOptions(SearchDraftsOptions):
    """Search options for drafts search."""

    facets = {
        'resource_type': resource_type_facet,
        'languages': language_facet,
        'subjects': subject_facet,
        'access_status': access_status_facet,
        'is_published': is_published_facet,
    }


#
# Service configuration
#
class RDMRecordServiceConfig(RecordServiceConfig):
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
    search_versions = SearchVersionsOptions

    # PIDs providers
    pids_providers = {
        "doi": {
            "datacite": {
                "provider": DOIDataCitePIDProvider,
                "required": True,
                "system_managed": True,
            },
            "unmanaged": {
                "provider": UnmanagedPIDProvider,
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
        "latest": RecordLink("{+api}/records/{id}/versions/latest"),
        "latest_html": RecordLink("{+ui}/records/{id}/latest"),
        "draft": RecordLink("{+api}/records/{id}/draft", when=is_record),
        "record": RecordLink("{+api}/records/{id}", when=is_draft),
        "publish": RecordLink(
            "{+api}/records/{id}/draft/actions/publish",
            when=is_draft
        ),
        "versions": RecordLink("{+api}/records/{id}/versions"),
        "access_links": RecordLink("{+api}/records/{id}/access/links"),
        # TODO: only include link when DOI support is enabled.
        "reserve_doi": RecordLink("{+api}/records/{id}/draft/pids/doi")
    }


class RDMFileRecordServiceConfig(FileServiceConfig):
    """Configuration for record files."""

    record_cls = RDMRecord
    permission_policy_cls = RDMRecordPermissionPolicy


class RDMFileDraftServiceConfig(FileServiceConfig):
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
