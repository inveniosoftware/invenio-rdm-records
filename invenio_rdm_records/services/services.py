# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""


import tempfile

import arrow
from elasticsearch_dsl.query import Q
from flask_iiif.api import IIIFImageAPIWrapper
from invenio_drafts_resources.services.records import RecordService
from invenio_records_resources.services import LinksTemplate, Service
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests.services.results import EntityResolverExpandableField

from invenio_rdm_records.services.errors import EmbargoNotLiftedError
from invenio_rdm_records.services.results import \
    ParentCommunitiesExpandableField

try:
    from importlib import metadata
except ImportError:
    # Running on pre-3.8 Python; use importlib-metadata package
    import importlib_metadata as metadata

try:
    metadata.distribution('wand')
    from wand.image import Image
    HAS_IMAGEMAGICK = True
except (metadata.PackageNotFoundError, ImportError):
    # ImageMagick notinstalled
    HAS_IMAGEMAGICK = False


class RDMRecordService(RecordService):
    """RDM record service."""

    def __init__(self, config, files_service=None, draft_files_service=None,
                 secret_links_service=None, pids_service=None,
                 review_service=None):
        """Constructor for RecordService."""
        super().__init__(config, files_service, draft_files_service)
        self._secret_links = secret_links_service
        self._pids = pids_service
        self._review = review_service

    #
    # Subservices
    #
    @property
    def secret_links(self):
        """Record secret link service."""
        return self._secret_links

    @property
    def pids(self):
        """Record PIDs service."""
        return self._pids

    @property
    def review(self):
        """Record PIDs service."""
        return self._review

    #
    # Properties
    #
    @property
    def expandable_fields(self):
        """Get expandable fields.

        Expand community field to return community details.
        """
        return [
            EntityResolverExpandableField("parent.review.receiver"),
            ParentCommunitiesExpandableField("parent.communities.default"),
        ]

    #
    # Service methods
    #
    @unit_of_work()
    def lift_embargo(self, identity, _id, uow=None):
        """Lifts embargo from the record and draft (if exists).

        It's an error if you try to lift an embargo that has not yet expired.
        Use this method in combination with scan_expired_embargos().
        """
        # Get the record
        record = self.record_cls.pid.resolve(_id)

        # Check permissions
        self.require_permission(identity, "lift_embargo", record=record)

        # Modify draft embargo if draft exists and it's the same as the record.
        draft = None
        if record.has_draft:
            draft = self.draft_cls.pid.resolve(_id, registered_only=False)
            if record.access == draft.access:
                if not draft.access.lift_embargo():
                    raise EmbargoNotLiftedError(_id)
                uow.register(RecordCommitOp(draft, indexer=self.indexer))

        if not record.access.lift_embargo():
            raise EmbargoNotLiftedError(_id)

        uow.register(RecordCommitOp(record, indexer=self.indexer))

    def scan_expired_embargos(self, identity):
        """Scan for records with an expired embargo."""
        today = arrow.utcnow().date().isoformat()

        embargoed_q = \
            f"access.embargo.active:true " \
            f"AND access.embargo.until:[* TO {today}]"

        return self.scan(identity=identity, q=embargoed_q)

    def search_community_records(self, identity, community_id, params=None,
                                 es_preference=None, **kwargs):
        """Search for records published in the given community."""
        self.require_permission(identity, "read")

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            "search",
            identity,
            params,
            es_preference,
            record_cls=self.record_cls,
            search_opts=self.config.search,
            extra_filter=Q(
                "term", **{"parent.communities.ids": str(community_id)}
            ),
            permission_action="read",
            **kwargs,
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_community_records,
                context={
                    "args": params,
                    "id": community_id,
                }
            ),
            links_item_tpl=self.links_item_tpl,
        )


class IIIFService(Service):
    """IIIF service.

    This is just a thin layer on top of Flask-IIIF API.
    """

    def __init__(self, config, records_service):
        """Constructor."""
        super().__init__(config)
        self._records_service = records_service

    def _iiif_uuid(self, uuid):
        """Split the uuid content.

        We assume the uuid is build as ``<record|draft>:<pid_value>``.
        """
        type_, id_ = uuid.split(':', 1)
        return type_, id_

    def _iiif_image_uuid(self, uuid):
        """Split the uuid content.

        We assume the uuid is build as ``<record|draft>:<pid_value>:<key>``.
        """
        type_, id_, key = uuid.split(':', 2)
        return type_, id_, key

    def file_service(self, type_):
        """Get the correct instance of the file service, draft vs record."""
        return (
            self._records_service.files
            if type_ == "record"
            else self._records_service.draft_files
        )

    def read_record(self, identity, uuid):
        """Read the correct version of the record and its files."""
        type_, id_ = self._iiif_uuid(uuid)
        read = (
            self._records_service.read
            if type_ == "record"
            else self._records_service.read_draft
        )
        # Kids, don't do this at home
        # If you find yourself wanting to copy this, ask for help first
        record = read(identity=identity, id_=id_)
        file_service = self.file_service(type_)
        files = file_service.list_files(identity=identity, id_=id_)
        record.files = files
        return record

    def _open_image(self, file_):
        fp = file_.get_stream('rb')
        # If ImageMagick with Wand is installed, extract first page
        # for PDF/text.
        pages_mimetypes = {'application/pdf', 'text/plain'}
        if HAS_IMAGEMAGICK and file_.data["mimetype"] in pages_mimetypes:
            first_page = Image(Image(fp).sequence[0])
            tempfile_ = tempfile.TemporaryFile()
            with first_page.convert(format='png') as converted:
                converted.save(file=tempfile_)
            return tempfile_

        return fp

    def get_file(self, identity, uuid, key=None):
        """."""
        if key:
            type_, id_ = self._iiif_uuid(uuid)
        else:
            type_, id_, key = self._iiif_image_uuid(uuid)

        service = self.file_service(type_)
        # TODO: add cache and check if the metadata is present
        return service.get_file_content(
            id_=id_, file_key=key, identity=identity
        )

    def image_api(
        self,
        identity,
        uuid,
        region,
        size,
        rotation,
        quality,
        image_format,
    ):
        """Run the IIIF image API workflow."""
        # Validate IIIF parameters
        IIIFImageAPIWrapper.validate_api(
            uuid=uuid,
            region=region,
            size=size,
            rotation=rotation,
            quality=quality,
            image_format=image_format,
        )

        type_, id_, key = self._iiif_image_uuid(uuid)
        service = self.file_service(type_)
        # TODO: check cache before this
        file_ = service.get_file_content(
            id_=id_, file_key=key, identity=identity
        )
        data = self._open_image(file_)
        # TODO: include image magic for pdf
        image = IIIFImageAPIWrapper.open_image(data)
        image.apply_api(
            region=region,
            size=size,
            rotation=rotation,
            quality=quality,
        )
        # prepare image to be serve
        to_serve = image.serve(image_format=image_format)
        image.close_image()
        return to_serve
