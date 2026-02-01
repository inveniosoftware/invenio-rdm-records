# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 CERN.
# Copyright (C) 2020-2025 Northwestern University.
# Copyright (C)      2021 TU Wien.
# Copyright (C) 2021-2026 Graz University of Technology.
# Copyright (C) 2022      Universität Hamburg
# Copyright (C) 2024      KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

import itertools
from copy import deepcopy
from os.path import splitext
from pathlib import Path

from flask import current_app
from invenio_communities.communities.records.api import Community
from invenio_drafts_resources.services.records.components import (
    DraftMediaFilesComponent,
)
from invenio_drafts_resources.services.records.config import (
    RecordServiceConfig,
    SearchDraftsOptions,
    SearchOptions,
    SearchVersionsOptions,
    is_draft,
    is_record,
)
from invenio_drafts_resources.services.records.search_params import AllVersionsParam
from invenio_indexer.api import RecordIndexer
from invenio_records_resources.services import (
    ConditionalLink,
    EndpointLink,
    ExternalLink,
)
from invenio_records_resources.services import (
    FileServiceConfig as BaseFileServiceConfig,
)
from invenio_records_resources.services import (
    NestedLinks,
    RecordEndpointLink,
    pagination_endpoint_links,
)
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfig,
    FromConfigSearchOptions,
    SearchOptionsMixin,
    ServiceConfig,
)
from invenio_records_resources.services.files.links import FileEndpointLink
from invenio_records_resources.services.files.schema import FileSchema
from invenio_records_resources.services.records.config import (
    RecordServiceConfig as BaseRecordServiceConfig,
)
from invenio_records_resources.services.records.params import (
    FacetsParam,
    PaginationParam,
    QueryStrParam,
)
from invenio_requests.services.requests import RequestItem, RequestList
from invenio_requests.services.requests.config import RequestSearchOptions
from requests import Request
from werkzeug.local import LocalProxy

from invenio_rdm_records.records.processors.tiles import TilesProcessor

from ..records import RDMDraft, RDMRecord
from ..records.api import RDMDraftMediaFiles, RDMRecordMediaFiles
from . import facets
from .components import DefaultRecordsComponents
from .customizations import (
    FromConfigConditionalPIDs,
    FromConfigPIDsProviders,
    FromConfigRequiredPIDs,
)
from .permissions import RDMRecordPermissionPolicy
from .request_policies import FileModificationPolicyEvaluator, RDMRecordDeletionPolicy
from .result_items import GrantItem, GrantList, SecretLinkItem, SecretLinkList
from .results import RDMRecordList, RDMRecordRevisionsList
from .schemas import RDMParentSchema, RDMRecordSchema
from .schemas.community_records import CommunityRecordsSchema
from .schemas.parent.access import AccessSettingsSchema
from .schemas.parent.access import Grant as GrantSchema
from .schemas.parent.access import Grants as GrantsSchema
from .schemas.parent.access import RequestAccessSchema
from .schemas.parent.access import SecretLink as SecretLinkSchema
from .schemas.parent.communities import CommunitiesSchema
from .schemas.quota import QuotaSchema
from .schemas.record_communities import RecordCommunitiesSchema
from .schemas.tombstone import TombstoneSchema
from .search_params import (
    MetricsParam,
    PublishedRecordsParam,
    SharedOrMyDraftsParam,
    StatusParam,
)
from .sort import VerifiedRecordsSortParam


def is_draft_and_has_review(record, ctx):
    """Determine if draft has doi."""
    return is_draft(record, ctx) and record.parent.review is not None


def is_record_and_has_doi(record, ctx):
    """Determine if record has doi."""
    return is_record(record, ctx) and has_doi(record, ctx)


def is_published(record, ctx):
    """Determine if record is published record's draft."""
    return record.is_published


def is_record_or_draft_and_has_parent_doi(record, ctx):
    """Determine if draft or record has parent doi."""
    return (is_record(record, ctx) or is_draft(record, ctx)) and has_doi(
        record.parent, ctx
    )


def has_doi(record, ctx):
    """Determine if a record has a DOI."""
    pids = record.pids or {}
    return "doi" in pids and pids["doi"].get("identifier") is not None


def is_iiif_compatible(file_, ctx):
    """Determine if a file is IIIF compatible."""
    file_ext = splitext(file_.key)[1].replace(".", "").lower()
    return file_ext in current_app.config["IIIF_FORMATS"]


def archive_download_enabled(record, ctx):
    """Return if the archive download feature is enabled."""
    return current_app.config["RDM_ARCHIVE_DOWNLOAD_ENABLED"]


def _groups_enabled(record, ctx):
    """Return if groups are enabled."""
    return current_app.config.get("USERS_RESOURCES_GROUPS_ENABLED", False)


def is_datacite_test(record, ctx):
    """Return if the datacite test mode is being used."""
    return current_app.config["DATACITE_TEST_MODE"]


def lock_edit_published_files(service, identity, record=None, draft=None):
    """Return if files once published should be locked when editing the record.

    Return False to allow editing of published files or True otherwise.
    """
    return True


def has_image_files(record, ctx):
    """Return if the record has any image file."""
    for file in record.files.entries:
        file_ext = splitext(file)[1].replace(".", "").lower()
        if file_ext in current_app.config["IIIF_FORMATS"]:
            return True


def record_thumbnail_sizes():
    """Return configured sizes for thumbnails."""
    return current_app.config.get("APP_RDM_RECORD_THUMBNAIL_SIZES", [])


def get_record_thumbnail_file(record, **kwargs):
    """Generate the URL for a record's thumbnail."""
    files = record.files
    default_preview = files.get("default_preview")
    file_entries = files.entries
    image_extensions = current_app.config["IIIF_FORMATS"]
    if file_entries:
        # Verify file has allowed extension and select the default preview file if present else the first valid file
        file_key = next(
            (
                key
                for key in itertools.chain([default_preview], file_entries)
                if key and Path(key).suffix[1:] in image_extensions
            ),
            None,
        )
        return file_key


#
# Default search configuration
#
class RDMSearchOptions(SearchOptions, SearchOptionsMixin):
    """Search options for record search."""

    verified_sorting_enabled = True

    facets = {
        "resource_type": facets.resource_type,
        "languages": facets.language,
        "access_status": facets.access_status,
    }

    # Override params interpreters to avoid having duplicated SortParam.
    params_interpreters_cls = [
        AllVersionsParam.factory("versions.is_latest"),
        QueryStrParam,
        PaginationParam,
        FacetsParam,
        VerifiedRecordsSortParam,
        StatusParam,
        PublishedRecordsParam,
        MetricsParam,
    ]


class RDMCommunityRecordSearchOptions(RDMSearchOptions):
    """Search options for community record search."""

    verified_sorting_enabled = False


class RDMSearchDraftsOptions(SearchDraftsOptions, SearchOptionsMixin):
    """Search options for drafts search."""

    facets = {
        "resource_type": facets.resource_type,
        "languages": facets.language,
        "access_status": facets.access_status,
        "is_published": facets.is_published,
    }

    params_interpreters_cls = [
        SharedOrMyDraftsParam
    ] + SearchDraftsOptions.params_interpreters_cls


class RDMSearchVersionsOptions(SearchVersionsOptions, SearchOptionsMixin):
    """Search options for record versioning search."""

    params_interpreters_cls = [
        PublishedRecordsParam
    ] + SearchVersionsOptions.params_interpreters_cls


#
# Helper link definitions
#


class RecordPIDLink(ExternalLink):
    """Record external PID link."""

    def vars(self, record, vars):
        """Add record PID to vars."""
        vars.update(
            {
                f"pid_{scheme}": pid["identifier"]
                for (scheme, pid) in record.pids.items()
            }
        )
        vars.update(
            {
                f"parent_pid_{scheme}": pid["identifier"]
                for (scheme, pid) in record.parent.pids.items()
            }
        )


class ThumbnailLinks:
    """RDM thumbnail links dictionary.

    Adopts the interface of an EndpointLink but not one.
    """

    link_for_thumbnail = EndpointLink(
        "iiif.image_api",
        params=["uuid", "region", "size", "rotation", "quality", "image_format"],
    )

    def __init__(self, sizes=None, when=None):
        """Constructor."""
        self._sizes = sizes
        self._when_func = when

    def should_render(self, obj, context):
        """Determine if the dictionary of links should be rendered."""
        if self._when_func:
            return bool(self._when_func(obj, context))
        else:
            return True

    def expand(self, obj, context):
        """Expand the thumbs size dictionary of URIs."""
        vars = {}
        vars.update(deepcopy(context))
        record = obj
        pid_value = record.pid.pid_value
        file_key = get_record_thumbnail_file(record=record)
        vars.update(
            {
                "uuid": f"record:{pid_value}:{file_key}",
                "region": "full",
                "rotation": "0",
                "quality": "default",
                "image_format": "jpg",
            }
        )
        links = {}
        for size in self._sizes:
            vars["size"] = f"^{size},"  # IIIF syntax
            links[str(size)] = self.link_for_thumbnail.expand(record, vars)
        return links


record_doi_link = ConditionalLink(
    cond=is_datacite_test,
    if_=RecordPIDLink("https://handle.test.datacite.org/{+pid_doi}", when=has_doi),
    else_=RecordPIDLink("https://doi.org/{+pid_doi}", when=has_doi),
)


def vars_preview_html(drafcord, vars):
    """Update vars in place for variable expansion."""
    vars_args = vars.setdefault("args", {})
    vars_args["preview"] = 1


def get_pid_value(drafcord):
    """Get the pid_value or None of draft or record."""
    return getattr(drafcord.pid, "pid_value", None)


def is_record_or_draft(drafcord):
    """Return if input is a draft or a record."""
    return "record" if is_record(drafcord, {}) else "draft"


def get_iiif_uuid_of_drafcord_from_file_drafcord(file_drafcord, vars):
    """Return IIIF uuid of draft or record associated with RDMFile{Record,Draft}."""
    # Rely on being called with a context (vars) containing pid_value
    # which was a pre-existing assumption at time of writing
    r_or_d = is_record_or_draft(file_drafcord.record)
    return f"{r_or_d}:{vars['pid_value']}"


def get_iiif_uuid_of_file_drafcord(file_drafcord, vars):
    """Return IIIF uuid of a RDMFileRecord or RDMFileDraft."""
    # Rely on being called with a context (vars) containing pid_value
    # which was a pre-existing assumption at time of writing
    prefix = get_iiif_uuid_of_drafcord_from_file_drafcord(file_drafcord, vars)
    return f"{prefix}:{file_drafcord.key}"


def get_iiif_uuid_of_drafcord(drafcord, vars):
    """Return IIIF uuid of draft or record."""
    # Rely on being called with a context (vars) containing pid_value
    # which was a pre-existing assumption at time of writing
    r_or_d = is_record_or_draft(drafcord)
    return f"{r_or_d}:{vars['pid_value']}"


def vars_self_iiif(drafcord, vars):
    """Update in-place `vars` with variables for endpoint expansion."""
    # In this context -generating links from a resource retrieved by its pid_value-
    # a pid_value is necessarily present
    vars["pid_value"] = drafcord.pid.pid_value
    vars["uuid"] = get_iiif_uuid_of_drafcord(drafcord, vars)


#
# Default service configuration
#
class RDMRecordCommunitiesConfig(ServiceConfig, ConfiguratorMixin):
    """Record communities service config."""

    service_id = "record-communities"

    record_cls = FromConfig("RDM_RECORD_CLS", default=RDMRecord)
    draft_cls = FromConfig("RDM_DRAFT_CLS", default=RDMDraft)
    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=RDMRecordPermissionPolicy, import_string=True
    )

    schema = RecordCommunitiesSchema
    communities_schema = CommunitiesSchema

    indexer_cls = RecordIndexer
    indexer_queue_name = service_id
    index_dumper = None

    # Max n. communities that can be added at once
    max_number_of_additions = 10
    # Max n. communities that can be removed at once
    max_number_of_removals = 10

    components = FromConfig(
        "RDM_RECORD_COMMUNITIES_SERVICE_COMPONENTS",
        default=[],
    )


class RDMRecordRequestsConfig(ServiceConfig, ConfiguratorMixin):
    """Record community inclusion config."""

    request_record_cls = FromConfig("RDM_RECORD_CLS", default=RDMRecord)
    service_id = "record-requests"
    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=RDMRecordPermissionPolicy, import_string=True
    )
    result_item_cls = RequestItem
    result_list_cls = RequestList
    search = RequestSearchOptions

    # request-specific configuration
    record_cls = Request  # needed for model queries
    schema = None  # stored in the API classes, for customization
    indexer_queue_name = "requests"
    index_dumper = None


class WithFileLinks(type):
    """Metaclass to dynamically generate file_links_{list,item} at class level.

    This approach is needed to make use of the current config's
    allow_upload OR the parent's allow_upload in the construction of the file_links.
    It also makes further inheritance work as expected without additional code
    (as would be the case with a class decorator).
    """

    def __init__(cls, *args, **kwargs):
        """Constructor."""
        cls.file_links_list = {
            "self": EndpointLink(
                f"{cls.name_of_file_blueprint}.search", params=["pid_value"]
            ),
            "archive": EndpointLink(
                f"{cls.name_of_file_blueprint}.read_archive",
                params=["pid_value"],
                when=archive_download_enabled,
            ),
        }

        cls.file_links_item = {
            "self": FileEndpointLink(
                f"{cls.name_of_file_blueprint}.read", params=["pid_value", "key"]
            ),
            "content": FileEndpointLink(
                f"{cls.name_of_file_blueprint}.read_content",
                params=["pid_value", "key"],
            ),
            "commit": FileEndpointLink(
                f"{cls.name_of_file_blueprint}.create_commit",
                params=["pid_value", "key"],
                when=lambda file_draft, ctx: (
                    cls.allow_upload and is_draft(file_draft.record, ctx)
                ),
            ),
            "iiif_canvas": FileEndpointLink(
                "iiif.canvas",
                params=["uuid", "file_name"],
                when=is_iiif_compatible,
                vars=lambda file_drafcord, vars: vars.update(
                    {
                        "uuid": get_iiif_uuid_of_drafcord_from_file_drafcord(
                            file_drafcord, vars
                        ),
                        "file_name": vars["key"],  # Because of FileEndpointLink
                    }
                ),
            ),
            "iiif_base": EndpointLink(
                "iiif.base",
                params=["uuid"],
                when=is_iiif_compatible,
                vars=lambda file_drafcord, vars: vars.update(
                    {"uuid": get_iiif_uuid_of_file_drafcord(file_drafcord, vars)}
                ),
            ),
            "iiif_info": EndpointLink(
                "iiif.info",
                params=["uuid"],
                when=is_iiif_compatible,
                vars=lambda file_drafcord, vars: vars.update(
                    {"uuid": get_iiif_uuid_of_file_drafcord(file_drafcord, vars)}
                ),
            ),
            "iiif_api": EndpointLink(
                "iiif.image_api",
                params=[
                    "uuid",
                    "region",
                    "size",
                    "rotation",
                    "quality",
                    "image_format",
                ],
                when=is_iiif_compatible,
                vars=lambda file_drafcord, vars: vars.update(
                    {
                        "uuid": get_iiif_uuid_of_file_drafcord(file_drafcord, vars),
                        "region": "full",
                        "size": "full",
                        "rotation": "0",
                        "quality": "default",
                        "image_format": "png",
                    }
                ),
            ),
        }


class FileServiceConfig(
    BaseFileServiceConfig, ConfiguratorMixin, metaclass=WithFileLinks
):
    """Common File Service configuration.

    Injects file_links dynamically via metaclass (to all descendants).

    If a descendant wants to override the file_links, a new metaclass inheriting
    from WithFileLinks and containing the desired changes has to be created, and then
    used by the descendant.
    """

    name_of_file_blueprint = ""  # Has to be overridden by descendants
    allow_archive_download = FromConfig("RDM_ARCHIVE_DOWNLOAD_ENABLED", True)


class RDMFileRecordServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Configuration for record files."""

    record_cls = FromConfig("RDM_RECORD_CLS", default=RDMRecord)

    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=RDMRecordPermissionPolicy
    )

    max_files_count = FromConfig("RDM_RECORDS_MAX_FILES_COUNT", 100)

    # For blueprint/link serialization
    allow_upload = False
    name_of_file_blueprint = "record_files"

    file_schema = FileSchema

    components = FromConfig(
        "RDM_FILES_SERVICE_COMPONENTS", default=FileServiceConfig.components
    )


class RDMRecordServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """RDM record draft service config."""

    # Record and draft classes
    record_cls = FromConfig("RDM_RECORD_CLS", default=RDMRecord)
    draft_cls = FromConfig("RDM_DRAFT_CLS", default=RDMDraft)

    # Schemas
    schema = FromConfig("RDM_RECORD_SCHEMA", default=RDMRecordSchema)
    schema_parent = RDMParentSchema
    schema_access_settings = AccessSettingsSchema
    schema_secret_link = SecretLinkSchema
    schema_grant = GrantSchema
    schema_grants = GrantsSchema
    schema_request_access = RequestAccessSchema
    schema_tombstone = TombstoneSchema
    schema_quota = QuotaSchema

    # Permission policy
    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=RDMRecordPermissionPolicy, import_string=True
    )

    # Policies
    deletion_policy = FromConfig(
        "RDM_RECORD_DELETION_POLICY", default=RDMRecordDeletionPolicy
    )
    file_modification_policy = FromConfig(
        "RDM_FILE_MODIFICATION_POLICY", default=FileModificationPolicyEvaluator
    )

    # Result classes
    link_result_item_cls = SecretLinkItem
    link_result_list_cls = SecretLinkList
    grant_result_item_cls = GrantItem
    grant_result_list_cls = GrantList
    result_list_cls = RDMRecordList
    revision_result_list_cls = RDMRecordRevisionsList

    default_files_enabled = FromConfig("RDM_DEFAULT_FILES_ENABLED", default=True)

    # we disable by default media files. The feature is only available via REST API
    # and they should be enabled before an upload is made i.e update the draft to
    # set `media_files.enabled` to True
    default_media_files_enabled = False

    lock_edit_published_files = FromConfig(
        "RDM_LOCK_EDIT_PUBLISHED_FILES", default=lock_edit_published_files
    )

    # Search configuration
    search = FromConfigSearchOptions(
        "RDM_SEARCH",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=RDMSearchOptions,
        search_option_cls_key="RDM_SEARCH_OPTIONS_CLS",
    )
    search_drafts = FromConfigSearchOptions(
        "RDM_SEARCH_DRAFTS",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=RDMSearchDraftsOptions,
    )
    search_versions = FromConfigSearchOptions(
        "RDM_SEARCH_VERSIONING",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=RDMSearchVersionsOptions,
    )

    # PIDs configuration
    pids_providers = FromConfigPIDsProviders()
    pids_required = FromConfigRequiredPIDs()

    parent_pids_providers = FromConfigPIDsProviders(
        pids_key="RDM_PARENT_PERSISTENT_IDENTIFIERS",
        providers_key="RDM_PARENT_PERSISTENT_IDENTIFIER_PROVIDERS",
    )
    parent_pids_required = FromConfigRequiredPIDs(
        pids_key="RDM_PARENT_PERSISTENT_IDENTIFIERS",
    )
    parent_pids_conditional = FromConfigConditionalPIDs(
        pids_key="RDM_PARENT_PERSISTENT_IDENTIFIERS",
    )

    # Components - order matters!
    # Service components
    components = FromConfig(
        "RDM_RECORDS_SERVICE_COMPONENTS", default=DefaultRecordsComponents
    )

    # Links
    links_item = {
        # Record
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordEndpointLink("records.read"),
            else_=RecordEndpointLink("records.read_draft"),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordEndpointLink("invenio_app_rdm_records.record_detail"),
            else_=RecordEndpointLink("invenio_app_rdm_records.deposit_edit"),
        ),
        "preview_html": RecordEndpointLink(
            "invenio_app_rdm_records.record_detail",
            vars=vars_preview_html,
        ),
        # DOI
        "doi": record_doi_link,
        "self_doi": record_doi_link,
        "self_doi_html": EndpointLink(
            "invenio_app_rdm_records.record_from_pid",
            params=["pid_value", "pid_scheme"],
            when=is_record_and_has_doi,
            vars=lambda record, vars: vars.update(
                {
                    "pid_scheme": "doi",
                    "pid_value": record.pids["doi"]["identifier"],
                }
            ),
        ),
        # TODO: only include link when DOI support is enabled.
        "reserve_doi": RecordEndpointLink(
            "records.pids_reserve",
            params=["pid_value", "scheme"],
            vars=lambda record, vars: vars.update({"scheme": "doi"}),
        ),
        # Parent
        "parent": EndpointLink(
            "records.read",
            params=["pid_value"],
            when=is_record,
            vars=lambda record, vars: vars.update(
                {"pid_value": record.parent.pid.pid_value}
            ),
        ),
        "parent_html": EndpointLink(
            "invenio_app_rdm_records.record_detail",
            params=["pid_value"],
            when=is_record,
            vars=lambda record, vars: vars.update(
                {"pid_value": record.parent.pid.pid_value}
            ),
        ),
        "parent_doi": ConditionalLink(
            cond=is_datacite_test,
            if_=RecordPIDLink(
                "https://handle.test.datacite.org/{+parent_pid_doi}",
                when=is_record_or_draft_and_has_parent_doi,
            ),
            else_=RecordPIDLink(
                "https://doi.org/{+parent_pid_doi}",
                when=is_record_or_draft_and_has_parent_doi,
            ),
        ),
        "parent_doi_html": EndpointLink(
            "invenio_app_rdm_records.record_from_pid",
            params=["pid_value", "pid_scheme"],
            when=is_record_or_draft_and_has_parent_doi,
            vars=lambda record, vars: vars.update(
                {
                    "pid_scheme": "doi",
                    "pid_value": record.parent.pids["doi"]["identifier"],
                }
            ),
        ),
        # IIIF
        "self_iiif_manifest": EndpointLink(
            "iiif.manifest", params=["uuid"], vars=vars_self_iiif
        ),
        "self_iiif_sequence": EndpointLink(
            "iiif.sequence", params=["uuid"], vars=vars_self_iiif
        ),
        # Files
        "files": ConditionalLink(
            cond=is_record,
            if_=RecordEndpointLink("record_files.search"),
            else_=RecordEndpointLink("draft_files.search"),
        ),
        "media_files": ConditionalLink(
            cond=is_record,
            if_=RecordEndpointLink("record_media_files.search"),
            else_=RecordEndpointLink("draft_media_files.search"),
        ),
        "thumbnails": ThumbnailLinks(
            sizes=LocalProxy(record_thumbnail_sizes),
            when=has_image_files,
        ),
        "archive": ConditionalLink(
            cond=is_record,
            if_=RecordEndpointLink(
                "record_files.read_archive",
                when=archive_download_enabled,
            ),
            else_=RecordEndpointLink(
                "draft_files.read_archive",
                when=archive_download_enabled,
            ),
        ),
        "archive_media": ConditionalLink(
            cond=is_record,
            if_=RecordEndpointLink(
                "record_media_files.read_archive",
                when=archive_download_enabled,
            ),
            else_=RecordEndpointLink(
                "draft_media_files.read_archive",
                when=archive_download_enabled,
            ),
        ),
        # Versioning
        "latest": RecordEndpointLink("records.read_latest", when=is_record),
        "latest_html": RecordEndpointLink(
            "invenio_app_rdm_records.record_latest",
            when=is_record,
        ),
        "versions": RecordEndpointLink("records.search_versions"),
        # Corresponding Draft/Record
        "draft": RecordEndpointLink("records.read_draft", when=is_record),
        "record": RecordEndpointLink("records.read", when=is_draft),
        # TODO: record_html temporarily needed for DOI registration, until
        # problems with self_doi has been fixed
        "record_html": RecordEndpointLink(
            "invenio_app_rdm_records.record_detail", when=is_draft
        ),
        # Actions
        "publish": RecordEndpointLink("records.publish", when=is_draft),
        "review": RecordEndpointLink("records.review_read", when=is_draft),
        "submit-review": RecordEndpointLink(
            "records.review_submit",
            when=is_draft_and_has_review,
        ),
        # Access
        "access_links": RecordEndpointLink("record_links.search"),
        "access_grants": RecordEndpointLink("record_grants.search"),
        "access_users": RecordEndpointLink("record_user_access.search"),
        "access_groups": RecordEndpointLink(
            "record_group_access.search",
            when=_groups_enabled,
        ),
        "access_request": RecordEndpointLink("records.create_access_request"),
        "access": RecordEndpointLink("records.update_access_settings"),
        # Communities
        "communities": RecordEndpointLink("record_communities.search"),
        "communities-suggestions": RecordEndpointLink(  # TODO This is very bad? why hyphen?
            "record_communities.get_suggestions"
        ),
        "request_deletion": RecordEndpointLink(
            "records.request_deletion", when=is_published
        ),
        "file_modification": RecordEndpointLink(
            "records.file_modification", when=is_published
        ),
        # Requests
        # Unfortunately `record_pid`` was used in `RDMRecordRequestsResourceConfig``
        # instead of `pid_value`, so we have to pass a bespoke vars func
        "requests": EndpointLink(
            "record_requests.search",
            params=["record_pid"],
            vars=lambda record, vars: (
                vars.update({"record_pid": get_pid_value(record)})
                if get_pid_value(record)
                else None
            ),
        ),
    }

    nested_links_item = [
        NestedLinks(
            links=RDMFileRecordServiceConfig.file_links_item,
            key="files.entries",
            context_func=lambda identity, record, key, value: {
                "pid_value": record.pid.pid_value,
                "key": key,
            },
        ),
        NestedLinks(
            links=RDMFileRecordServiceConfig.file_links_item,
            key="media_files.entries",
            context_func=lambda identity, record, key, value: {
                "pid_value": record.pid.pid_value,
                "key": key,
            },
        ),
    ]

    record_file_processors = FromConfig(
        "RDM_RECORD_FILE_PROCESSORS", default=[TilesProcessor()]
    )


class RDMCommunityRecordsConfig(BaseRecordServiceConfig, ConfiguratorMixin):
    """Community records service config."""

    service_id = "community-records"
    record_cls = FromConfig("RDM_RECORD_CLS", default=RDMRecord)
    community_cls = Community
    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=RDMRecordPermissionPolicy, import_string=True
    )

    # Search configuration
    search = FromConfigSearchOptions(
        "RDM_SEARCH",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=RDMCommunityRecordSearchOptions,
        search_option_cls_key="RDM_COMMUNITY_RECORD_SEARCH_OPTIONS_CLS",
    )
    search_versions = FromConfigSearchOptions(
        "RDM_SEARCH_VERSIONING",
        "RDM_SORT_OPTIONS",
        "RDM_FACETS",
        search_option_cls=RDMSearchVersionsOptions,
    )

    # Service schemas
    community_record_schema = CommunityRecordsSchema
    schema = FromConfig("RDM_RECORD_SCHEMA", default=RDMRecordSchema)

    # Max n. records that can be removed at once
    max_number_of_removals = 10

    links_search_community_records = pagination_endpoint_links(
        "community-records.search", params=["pid_value"]
    )

    links_item = RDMRecordServiceConfig.links_item


class RDMRecordMediaFilesServiceConfig(RDMRecordServiceConfig):
    """RDM Record with media files service config."""

    service_id = "record-media-files"
    record_cls = RDMRecordMediaFiles
    draft_cls = RDMDraftMediaFiles

    components = [
        DraftMediaFilesComponent,
    ]


class RDMMediaFileRecordServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Configuration for record media files."""

    record_cls = RDMRecordMediaFiles
    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=RDMRecordPermissionPolicy
    )
    permission_action_prefix = "media_"

    max_files_count = FromConfig("RDM_RECORDS_MAX_MEDIA_FILES_COUNT", 100)

    # For blueprint/link serialization
    allow_upload = False
    name_of_file_blueprint = "record_media_files"

    file_schema = FileSchema


class RDMFileDraftServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Configuration for draft files."""

    service_id = "draft-files"

    record_cls = FromConfig("RDM_DRAFT_CLS", default=RDMDraft)

    permission_action_prefix = "draft_"
    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=RDMRecordPermissionPolicy
    )

    max_files_count = FromConfig("RDM_RECORDS_MAX_FILES_COUNT", 100)

    # For blueprint/link serialization
    name_of_file_blueprint = "draft_files"

    file_schema = FileSchema

    components = FromConfig(
        "RDM_DRAFT_FILES_SERVICE_COMPONENTS", default=FileServiceConfig.components
    )


class RDMMediaFileDraftServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Configuration for draft media files."""

    service_id = "draft-media-files"

    record_cls = RDMDraftMediaFiles
    permission_action_prefix = "draft_media_"
    permission_policy_cls = FromConfig(
        "RDM_PERMISSION_POLICY", default=RDMRecordPermissionPolicy
    )

    max_files_count = FromConfig("RDM_RECORDS_MAX_MEDIA_FILES_COUNT", 100)

    # For blueprint/link serialization
    name_of_file_blueprint = "draft_media_files"

    file_schema = FileSchema
