# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""VCS release API implementation."""

from flask import current_app
from invenio_access.permissions import authenticated_user, system_identity
from invenio_access.utils import get_identity
from invenio_db import db
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services.uow import UnitOfWork
from invenio_vcs.errors import CustomVCSReleaseNoRetryError
from invenio_vcs.models import Release, ReleaseStatus
from invenio_vcs.service import VCSRelease
from sqlalchemy import and_, or_

from invenio_rdm_records.notifications.vcs import (
    RepositoryReleaseCommunityRequiredNotificationBuilder,
    RepositoryReleaseFailureNotificationBuilder,
    RepositoryReleaseSuccessNotificationBuilder,
)

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


class RDMVCSRelease(VCSRelease):
    """Implement release API instance for RDM."""

    metadata_cls = RDMReleaseMetadata

    @property
    def metadata(self):
        """Extracts metadata to create an RDM draft."""
        metadata = self.metadata_cls(self)
        output = metadata.default_metadata
        output.update(metadata.extra_metadata)
        output.update(metadata.citation_metadata)

        if not output.get("creators"):
            # Get owner from Github API
            owner = self.get_owner()
            if owner:
                output.update({"creators": [owner]})

        # Default to "Unkwnown"
        if not output.get("creators"):
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

        # Add default license if not yet added
        if not output.get("rights"):
            default_license = "cc-by-4.0"
            if metadata.repo_license:
                default_license = metadata.repo_license.lower()
            output.update({"rights": [{"id": default_license}]})
        return output

    def get_custom_fields(self):
        """Get custom fields."""
        ret = {}
        repo_url = self.provider.factory.url_for_repository(self.generic_repo.full_name)
        ret["code:codeRepository"] = repo_url
        return ret

    def get_owner(self):
        """Retrieves repository owner and its affiliation, if any."""
        # `owner.name` is not required, `owner.login` is.
        output = None
        if self.owner:
            name = getattr(self.owner, "name", self.owner.login)
            company = getattr(self.owner, "company", None)
            output = {"person_or_org": {"type": "personal", "family_name": name}}
            if company:
                output.update({"affiliations": [{"name": company}]})
        return output

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

    def _upload_files_to_draft(self, identity, draft, uow):
        """Upload files to draft."""
        # Validate the release files are fetchable
        self.test_zipball()

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
        self.release_processing()
        # Commit state change, in case the publishing is stuck
        db.session.commit()

        draft_file_service = current_rdm_records_service.draft_files
        draft_record_model_id = None

        try:
            with UnitOfWork(db.session) as uow:
                data = {
                    "metadata": self.metadata,
                    "access": {"record": "public", "files": "public"},
                    "files": {"enabled": True},
                    "custom_fields": self.get_custom_fields(),
                }
                if self.is_first_release():
                    # For the first release, use the repo's owner identity.
                    identity = self.user_identity
                    draft = current_rdm_records_service.create(identity, data, uow=uow)
                    self._upload_files_to_draft(identity, draft, uow)
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

                draft_record_model_id = draft._record.model.id
                draft_file_service.commit_file(
                    identity, draft.id, self.release_file_name, uow=uow
                )

                # UOW must be committed manually since we're not using the decorator
                uow.commit()
        except Exception as ex:
            # Flag release as FAILED and raise the exception
            self.release_failed()
            # Commit the FAILED state, other changes were already rollbacked by the UOW
            db.session.commit()
            raise ex

        # We try to publish the draft in a separate try/except. We want to save the draft even
        # if the publish fails, but we want to notify the user.

        try:
            with UnitOfWork(db.session) as uow:
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
                        )
                    )
                )

                # UOW must be committed manually since we're not using the decorator
                uow.commit()
                return record
        except Exception as ex:
            # Flag release as FAILED and raise the exception
            self.release_failed()

            # Store the ID of the draft so we make sure to add a version instead of a whole new record for future releases.
            if draft_record_model_id is not None:
                self.db_release.record_id = draft_record_model_id
                self.db_release.record_is_draft = True

            # The release publish can fail for a wide range of reasons, each of which have various inconsistent error types.
            # Some errors have a 'message' attribute or a 'description' attribute, which is not the value that gets used
            # when the error is stringified.
            # Some errors might not have any accessible message, so we use the class name as a last resort.
            error_message = str(ex)
            if not error_message:
                if hasattr(ex, "message"):
                    # Need to stringify the LazyString, otherwise serialisation will fail
                    error_message = str(ex.message)
                elif hasattr(ex, "description"):
                    error_message = str(ex.description)
                else:
                    error_message = type(ex).__name__

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
        """Processes a github release.

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
