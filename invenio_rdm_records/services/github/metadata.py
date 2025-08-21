# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM github release metadata."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

import yaml
from flask import current_app
from invenio_i18n import _
from invenio_vcs.errors import CustomGitHubMetadataError
from invenio_vcs.providers import GenericContributor
from marshmallow import Schema, ValidationError
from mistune import markdown

if TYPE_CHECKING:
    from invenio_rdm_records.services.github.release import RDMVCSRelease


class RDMReleaseMetadata(object):
    """Wraps a realease object to extract its data to meet RDM specific needs."""

    def __init__(self, rdm_vcs_release: "RDMVCSRelease"):
        """Constructor."""
        self.rdm_release = rdm_vcs_release

    @property
    def related_identifiers(self):
        """Return related identifiers."""
        repo_name = self.rdm_release.generic_repo.full_name
        release_tag_name = self.rdm_release.generic_release.tag_name
        return {
            "identifier": self.rdm_release.provider.factory.url_for_tag(
                repo_name, release_tag_name
            ),
            "scheme": "url",
            "relation_type": {"id": "issupplementto"},
            "resource_type": {"id": "software"},
        }

    @property
    def title(self):
        """Generate a title from a release and its repository name."""
        repo_name = self.rdm_release.generic_repo.full_name
        release_name = (
            self.rdm_release.generic_release.name
            or self.rdm_release.generic_release.tag_name
        )
        return f"{repo_name}: {release_name}"

    @property
    def description(self):
        """Extract description from a release.

        If the relesae does not have any body, the repository description is used.
        Falls back for "No description provided".
        """
        if self.rdm_release.generic_release.body:
            return markdown(self.rdm_release.generic_release.body)
        elif self.rdm_release.generic_repo.description:
            return self.rdm_release.generic_repo.description
        return _("No description provided.")

    @property
    def default_metadata(self):
        """Return default metadata for a release."""
        # Get default right from app config or use cc-by-4.0 if default is not set in app
        # TODO use the default software license
        version = self.rdm_release.generic_release.tag_name

        publication_date = self.rdm_release.generic_release.published_at
        if publication_date is None:
            publication_date = datetime.now(tz=timezone.utc)
        publication_date = publication_date.date().isoformat()

        return dict(
            description=self.description,
            publication_date=publication_date,
            related_identifiers=[self.related_identifiers],
            version=version,
            title=self.title,
            resource_type={"id": "software"},
            creators=self.contributors,
            publisher=current_app.config.get("APP_RDM_DEPOSIT_FORM_DEFAULTS").get(
                "publisher", "CERN"
            ),
        )

    @property
    def repo_license(self):
        """Get license from repository, if any."""
        return self.rdm_release.generic_repo.license_spdx

    @property
    def contributors(self):
        """Serializes contributors retrieved from github.

        .. note::

            `self.rdm_release.contributors` might fail with a `UnexpectedGithubResponse`. This is an error from which the RDM release
            processing can't recover since `creators` is a mandatory field.
        """

        def serialize_author(contributor: GenericContributor):
            """Serializes github contributor data into RDM author."""
            # Default name to the user's login
            name = contributor.display_name or contributor.username
            company = contributor.company

            rdm_contributor: dict = {
                "person_or_org": {"type": "personal", "family_name": name},
            }
            if company:
                rdm_contributor.update({"affiliations": [{"name": company}]})
            return rdm_contributor

        contributors = []
        provider_contributors = self.rdm_release.contributors

        if provider_contributors is not None:
            # Get contributors from api
            for c in provider_contributors:
                rdm_author = serialize_author(c)
                if rdm_author:
                    contributors.append(rdm_author)

        return contributors

    @property
    def citation_metadata(self):
        """Get citation metadata for file in repository."""
        citation_file_path = current_app.config.get("VCS_CITATION_FILE")

        if not citation_file_path:
            return {}

        try:
            # Read raw data from file
            data = self.load_citation_file(citation_file_path)

            # Load metadata from citation file and serialize it
            return self.load_citation_metadata(data)
        except ValidationError as e:
            # Wrap the error into CustomGitHubMetadataError() so it can be handled upstream
            raise CustomGitHubMetadataError(file=citation_file_path, message=e.messages)

    @property
    def extra_metadata(self):
        """Get extra metadata for the release."""
        return self.load_extra_metadata()

    def load_extra_metadata(self):
        """Get extra metadata for the release."""
        return {}

    def load_citation_file(self, citation_file_name):
        """Returns the citation file data."""
        if not citation_file_name:
            return {}

        # Fetch the citation file and load it
        content = self.rdm_release.provider.retrieve_remote_file(
            self.rdm_release.generic_repo.id,
            self.rdm_release.generic_release.tag_name,
            citation_file_name,
        )

        data = yaml.safe_load(content.decode("utf-8")) if content is not None else None

        return data

    def load_citation_metadata(self, citation_data):
        """Get the metadata file."""
        if not citation_data:
            return {}

        citation_schema = current_app.config.get("VCS_CITATION_METADATA_SCHEMA")

        assert issubclass(citation_schema, Schema), _(
            "Citation schema is needed to load citation metadata."
        )

        data = citation_schema().load(citation_data)

        return data
