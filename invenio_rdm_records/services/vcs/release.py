# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""VCS release API implementation."""

from __future__ import annotations

from flask import current_app
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_db import db
from invenio_drafts_resources.resources.records.errors import DraftNotCreatedError
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.uow import UnitOfWork
from invenio_vcs.api import VCSRelease
from invenio_vcs.errors import CustomVCSReleaseNoRetryError
from invenio_vcs.models import Release, ReleaseStatus
from invenio_vcs.providers import RepositoryServiceProvider
from invenio_vocabularies.proxies import current_service as current_vocabularies_service
from sqlalchemy.exc import NoResultFound

from invenio_rdm_records.notifications.vcs import (
    RepositoryReleaseCommunityRequiredNotificationBuilder,
    RepositoryReleaseCommunitySubmittedNotificationBuilder,
    RepositoryReleaseFailureNotificationBuilder,
    RepositoryReleaseSuccessNotificationBuilder,
)
from invenio_rdm_records.requests.community_submission import CommunitySubmission

from ...proxies import current_rdm_records_service
from ...resources.serializers.ui import UIJSONSerializer
from ..errors import CommunityRequiredError, RecordDeletedException
from .metadata import RDMReleaseMetadata
from .utils import retrieve_recid_by_uuid


def _get_user_identity(user):
    """Get user identity."""
    identity = get_identity(user)
    identity.provides.add(authenticated_user)
    return identity


def _format_error_message(ex):
    """Format an exception into a user-readable message."""
    if hasattr(ex, "message"):
        # Some errors have a 'message' attribute or a 'description' attribute, which is not the value that gets used
        # when the error is stringified.
        # Need to stringify the LazyString, otherwise serialisation will fail
        return str(ex.message)
    elif hasattr(ex, "description"):
        return str(ex.description)
    elif str(ex) != "":
        return str(ex)
    else:
        # Some errors might not have any accessible message, so we use the class name as a last resort.
        return type(ex).__name__


class RDMVCSRelease(VCSRelease):
    """Implement release API instance for RDM."""

    metadata_cls = RDMReleaseMetadata

    def __init__(self, release: Release, provider: RepositoryServiceProvider):
        """Constructor."""
        super().__init__(release, provider)
        self.warnings = []

    def add_warning(self, warning: str):
        """Add a new non-fatal warning."""
        self.warnings.append(warning)

    def build_metadata(self):
        """Extracts metadata to create an RDM draft."""
        metadata = self.metadata_cls(self)
        output: dict = metadata.default_metadata
        output.update(metadata.extra_metadata)
        citation_metadata = metadata.citation_metadata
        if citation_metadata is not None:
            output.update(citation_metadata)

        if not output.get("creators"):
            owner = self.get_owner()
            if owner:
                output.update({"creators": [owner]})

        # Default to "Unkwnown"
        if not output.get("creators"):
            self.add_warning(
                "No contributors were found for the repository. "
                "The record has been created without a list of creators; please edit it to specify them manually."
            )
            output.update(
                {
                    "creators": [
                        {
                            "person_or_org": {
                                "type": "personal",
                                "family_name": _("Unknown"),
                            },
                        }
                    ]
                }
            )

        # Add license if not yet added and available from the repo.
        license_pid = self.get_license_pid()
        if not output.get("rights") and license_pid:
            output.update({"rights": [{"id": license_pid}]})
        return output

    def get_custom_fields(self):
        """Get custom fields."""
        ret = {}
        repo_url = self.provider.factory.url_for_repository(self.generic_repo.full_name)
        ret["code:codeRepository"] = repo_url
        return ret

    def get_owner(self):
        """Retrieves repository owner and its affiliation from the VCS API, if any."""
        # `owner.name` is not required, `owner.login` is.
        output = None
        if self.owner:
            name = getattr(self.owner, "name", self.owner.path_name)
            company = getattr(self.owner, "company", None)
            output = {"person_or_org": {"type": "personal", "family_name": name}}
            if company:
                output.update({"affiliations": [{"name": company}]})
        return output

    def get_license_pid(self) -> str | None:
        """Returns whether the repository's license SPDX (as returned by the VCS) is a valid RDM license."""
        license_spdx_id = self.generic_repo.license_spdx
        if license_spdx_id is None:
            return None

        try:
            # Try reading from the vocab list; it may not exist since the VCS IDs do not map 1-to-1 with the vocabulary IDs
            license_vocab = current_vocabularies_service.read(
                identity=self.user_identity, id_=("licenses", license_spdx_id.lower())
            )
            return license_vocab.pid.id
        except (PIDDoesNotExistError, NoResultFound):
            self.add_warning(
                f"The repository's license '{license_spdx_id}' is not recognised. The record has been created without "
                "a license; please edit it to select one manually.",
            )
            return None

    def resolve_record(self):
        """Resolves an RDM record from a release."""
        if not self.db_release.record_id:
            return None
        recid = retrieve_recid_by_uuid(self.db_release.record_id)
        try:
            if self.db_release.record_is_draft == True:
                return current_rdm_records_service.read_draft(
                    system_identity, recid.pid_value
                )
            else:
                return current_rdm_records_service.read(
                    system_identity, recid.pid_value
                )
        except RecordDeletedException:
            return None
        except DraftNotCreatedError:
            # This error mostly occurs when we tried to read a draft but the record was published.
            # It can happen when the VCSComponent for handling the record publish fails to run for
            # whatever reason. To ensure we can recover and keep the DB consistent, we will update
            # the release here.
            published_record = current_rdm_records_service.read(
                system_identity, recid.pid_value
            )
            self.db_release.record_is_draft = False
            self.release_published()
            db.session.commit()
            return published_record

    def _upload_files_to_draft(self, identity, draft, uow):
        """Upload files to draft."""
        # Validate the release files are fetchable before initialising the draft files.
        self.resolve_zipball_url()

        draft_file_service = current_rdm_records_service.draft_files

        draft_file_service.init_files(
            identity,
            draft.id,
            data=[{"key": self.release_file_name}],
            uow=uow,
        )

        with self.fetch_zipball_file() as file_stream:
            draft_file_service.set_file_content(
                identity,
                draft.id,
                self.release_file_name,
                file_stream,
                uow=uow,
            )

    def publish(self):
        """Publish VCS release as record.

        Drafts and records are created using the current records service.
        The following steps are run inside a single transaction:

        - Check if a published record corresponding to a successful release exists.
        - If so, create a new version draft with the same parent. Otherwise, create a new parent/draft.
        - The draft's ownership is set to the user's id via its parent.
        - Upload files to the draft.
        - Publish the draft.

        In case of failure, the transaction is rolled back and the release status set to 'FAILED'


        :raises ex: any exception generated by the records service (e.g. invalid metadata)
        """
        draft_file_service = current_rdm_records_service.draft_files
        draft = None

        try:
            with UnitOfWork(db.session) as uow:
                data = {
                    "metadata": self.build_metadata(),
                    "access": {"record": "public", "files": "public"},
                    "files": {"enabled": True},
                    "custom_fields": self.get_custom_fields(),
                }
                if self.is_first_release():
                    # For the first release, use the repo's owner identity.
                    identity = self.user_identity
                    draft = current_rdm_records_service.create(identity, data, uow=uow)
                    self._upload_files_to_draft(identity, draft, uow)

                    if self.db_repo.record_community_id is not None:
                        # Create a review request for the repo's configured community ID if any
                        # If RDM_COMMUNITY_REQUIRED_TO_PUBLISH is true and no ID is provided, the publish will fail
                        # and the user will be sent a notification to manually assign a community.
                        current_rdm_records_service.review.create(
                            identity,
                            data={
                                "receiver": {
                                    "community": self.db_repo.record_community_id
                                },
                                "type": CommunitySubmission.type_id,
                            },
                            record=draft._record,
                            uow=uow,
                        )
                else:
                    # Retrieve latest record id and its recid
                    latest_release = self.db_repo.latest_release()
                    assert latest_release is not None
                    latest_record_uuid = latest_release.record_id

                    recid = retrieve_recid_by_uuid(latest_record_uuid)

                    # Use the previous record's owner as the new version owner
                    last_record = current_rdm_records_service.read(
                        system_identity, recid.pid_value, include_deleted=True
                    )
                    owner = last_record._record.parent.access.owner.resolve()

                    identity = _get_user_identity(owner)

                    # Create a new version and update its contents
                    new_version_draft = current_rdm_records_service.new_version(
                        identity, recid.pid_value, uow=uow
                    )

                    self._upload_files_to_draft(identity, new_version_draft, uow)

                    draft = current_rdm_records_service.update_draft(
                        identity, new_version_draft.id, data, uow=uow
                    )

                draft_file_service.commit_file(
                    identity, draft.id, self.release_file_name, uow=uow
                )

                # UOW must be committed manually since we're not using the decorator
                uow.commit()
        except Exception as ex:
            # Flag release as FAILED and raise the exception
            self.release_failed()

            with UnitOfWork(db.session) as uow:
                # Send a notification of the failed draft save.
                # This almost always will be because of a problem with the repository's contents or
                # metadata, and so the user needs to change something and then publish a new release.
                notification = RepositoryReleaseFailureNotificationBuilder.build(
                    provider=self.provider.factory.id,
                    generic_repository=self.generic_repo,
                    generic_release=self.generic_release,
                    error_message=_format_error_message(ex),
                )
                uow.register(NotificationOp(notification))
                uow.commit()

            # Commit the FAILED state, other changes were already rollbacked by the UOW
            db.session.commit()
            raise ex

        # We try to publish the draft in a separate try/except. We want to save the draft even
        # if the publish fails, but we want to notify the user.

        try:
            with UnitOfWork(db.session) as uow:
                if draft._record.parent.review is None:
                    record = current_rdm_records_service.publish(
                        identity, draft.id, uow=uow
                    )
                    # Update release weak reference and set status to PUBLISHED
                    self.db_release.record_id = record._record.model.id
                    self.db_release.record_is_draft = False
                    self.release_published()

                    uow.register(
                        NotificationOp(
                            RepositoryReleaseSuccessNotificationBuilder.build(
                                provider=self.provider.factory.id,
                                generic_repository=self.generic_repo,
                                generic_release=self.generic_release,
                                record=record,
                                warnings=self.warnings,
                            )
                        )
                    )
                else:
                    review_request = current_rdm_records_service.review.submit(
                        identity, draft.id, uow=uow
                    )

                    self.db_release.record_id = draft._record.model.id
                    self.db_release.record_is_draft = True
                    self.release_pending()

                    uow.register(
                        NotificationOp(
                            RepositoryReleaseCommunitySubmittedNotificationBuilder.build(
                                provider=self.provider.factory.id,
                                generic_repository=self.generic_repo,
                                generic_release=self.generic_release,
                                request=review_request._record,
                                community=review_request._record.receiver.resolve(),
                                warnings=self.warnings,
                            )
                        )
                    )

                # UOW must be committed manually since we're not using the decorator
                uow.commit()
                return None
        except Exception as ex:
            # Flag release as FAILED and raise the exception
            self.release_failed()

            # Store the ID of the draft so we make sure to add a version instead of a whole new record for future releases.
            self.db_release.record_id = draft._record.model.id
            self.db_release.record_is_draft = True

            # The release publish can fail for a wide range of reasons, each of which have various inconsistent error types.
            error_message = _format_error_message(ex)

            if isinstance(ex, CommunityRequiredError):
                # Use a special case notification for record's without a community (on mandatory-community instances).
                # This message phrases the error as a "step" the user has to take rather than something they did wrong.
                notification = (
                    RepositoryReleaseCommunityRequiredNotificationBuilder.build(
                        provider=self.provider.factory.id,
                        generic_repository=self.generic_repo,
                        generic_release=self.generic_release,
                        draft=draft,
                    )
                )
            else:
                notification = RepositoryReleaseFailureNotificationBuilder.build(
                    provider=self.provider.factory.id,
                    generic_repository=self.generic_repo,
                    generic_release=self.generic_release,
                    draft=draft,
                    error_message=error_message,
                )

            with UnitOfWork(db.session) as uow:
                uow.register(NotificationOp(notification))
                uow.commit()

            # Commit the FAILED state, other changes were already rollbacked by the UOW
            db.session.commit()

            # Wrap the error to ensure Celery does not attempt to retry it (since user action is needed to resolve the problem)
            raise CustomVCSReleaseNoRetryError(message=error_message)

    def process_release(self):
        """Processes a VCS release.

        The release might be first validated, in terms of sender, and then published.

        :raises ex: any exception generated by the records service when creating a draft or publishing the release record.
        """
        try:
            record = self.publish()
            return record
        except Exception as ex:
            message = (
                f"Error while processing VCS release {self.db_release.id}: {str(ex)}"
            )

            # A CustomVCSReleaseNoRetryError implies that the release failed due to a user error. Therefore, we should not
            # log this as an exception. This error will be caught upstream by InvenioVCS.
            if isinstance(ex, CustomVCSReleaseNoRetryError):
                current_app.logger.info(message)
            else:
                current_app.logger.exception(message)

            raise ex

    def serialize_record(self):
        """Serializes an RDM record."""
        return UIJSONSerializer().serialize_object(self.record.data)

    @property
    def record_url(self):
        """Release self url points to RDM record.

        It points to DataCite URL if the integration is enabled, otherwise it points to the HTML URL.
        """
        if self.record is None:
            return None
        html_url = self.record.data["links"]["self_html"]
        doi_url = self.record.data["links"].get("doi")
        return doi_url or html_url

    @property
    def badge_title(self):
        """Returns the badge title."""
        if current_app.config.get("DATACITE_ENABLED"):
            return "DOI"

    @property
    def badge_value(self):
        """Returns the badge value."""
        if current_app.config.get("DATACITE_ENABLED"):
            return self.record.data.get("pids", {}).get("doi", {}).get("identifier")

    def release_published(self):
        """Mark a release as published."""
        self.db_release.status = ReleaseStatus.PUBLISHED

    def release_failed(self):
        """Mark a release as failed."""
        self.db_release.status = ReleaseStatus.FAILED

    def release_pending(self):
        """Mark a release as pending (waiting for user action before publishing)."""
        self.db_release.status = ReleaseStatus.PUBLISH_PENDING
