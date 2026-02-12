# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM service component for updating VCS release models when drafts are published."""

from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_vcs.models import Release, ReleaseStatus


class VCSComponent(ServiceComponent):
    """Service component for VCS."""

    def publish(self, identity, draft=None, record=None):
        """Publish."""
        if record is None:
            return

        record_model_id = record.model.id
        # See if there's a release that originally failed to publish but was saved in a draft state
        db_release = Release.get_for_record(record_model_id, only_draft=True)
        # If this record didn't come from a VCS release or the release originally succeeded, we won't find anything.
        if db_release is None:
            return
        if (
            db_release.status != ReleaseStatus.FAILED
            and db_release.status != ReleaseStatus.PUBLISH_PENDING
        ):
            return

        # We are now publishing it, so we can correct the release's status
        db_release.status = ReleaseStatus.PUBLISHED
        db_release.record_is_draft = False
        # We can delete the error that originally happened during publish
        db_release.errors = None
