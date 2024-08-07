# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM github release metadata."""

import yaml
from flask import current_app
from invenio_github.errors import CustomGitHubMetadataError
from invenio_i18n import _
from marshmallow import Schema, ValidationError
from mistune import markdown


class RDMReleaseMetadata(object):
    """Wraps a realease object to extract its data to meet RDM specific needs."""

    def __init__(self, rdm_github_release):
        """Constructor."""
        self.rdm_release = rdm_github_release

    @property
    def related_identifiers(self):
        """Return related identifiers."""
        repo_name = self.rdm_release.repository_payload["full_name"]
        release_tag_name = self.rdm_release.release_payload["tag_name"]
        return {
            "identifier": "https://github.com/{}/tree/{}".format(
                repo_name, release_tag_name
            ),
            "scheme": "url",
            "relation_type": {"id": "issupplementto"},
            "resource_type": {"id": "software"},
        }

    @property
    def title(self):
        """Generate a title from a release and its repository name."""
        repo_name = self.rdm_release.repository_payload["full_name"]
        release_name = (
            self.rdm_release.release_payload.get("name")
            or self.rdm_release.release_payload["tag_name"]
        )
        return f"{repo_name}: {release_name}"

    @property
    def description(self):
        """Extract description from a release.

        If the relesae does not have any body, the repository description is used.
        Falls back for "No description provided".
        """
        if self.rdm_release.release_payload.get("body"):
            return markdown(self.rdm_release.release_payload["body"])
        elif self.rdm_release.repository_payload.get("description"):
            return self.rdm_release.repository_payload["description"]
        return _("No description provided.")

    @property
    def default_metadata(self):
        """Return default metadata for a release."""
        # Get default right from app config or use cc-by-4.0 if default is not set in app
        # TODO use the default software license
        default_right = "cc-by-4.0"
        version = self.rdm_release.release_payload.get("tag_name", "")

        return dict(
            description=self.description,
            rights=[{"id": default_right}],
            publication_date=self.rdm_release.release_payload["published_at"][:10],
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
    def contributors(self):
        """Serializes contributors retrieved from github.

        .. note::

            `self.rdm_release.contributors` might fail with a `UnexpectedGithubResponse`. This is an error from which the RDM release
            processing can't recover since `creators` is a mandatory field.
        """

        def serialize_author(gh_data):
            """Serializes github contributor data into RDM author."""
            gh_username = gh_data["login"]
            # Default name to the user's login
            name = gh_data.get("name") or gh_username
            company = gh_data.get("company")

            rdm_contributor = {
                "person_or_org": {"type": "personal", "family_name": name},
            }
            if company:
                rdm_contributor.update({"affiliations": [{"name": company}]})
            return rdm_contributor

        contributors = []

        # Get contributors from api
        for c in self.rdm_release.contributors:
            rdm_author = serialize_author(c)
            if rdm_author:
                contributors.append(rdm_author)

        return contributors

    @property
    def citation_metadata(self):
        """Get citation metadata for file in repository."""
        citation_file_path = current_app.config.get("GITHUB_CITATION_FILE")

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
        content = self.rdm_release.retrieve_remote_file(citation_file_name)

        data = (
            yaml.safe_load(content.decoded.decode("utf-8"))
            if content is not None
            else None
        )

        return data

    def load_citation_metadata(self, citation_data):
        """Get the metadata file."""
        if not citation_data:
            return {}

        citation_schema = current_app.config.get("GITHUB_CITATION_METADATA_SCHEMA")

        assert issubclass(citation_schema, Schema), _(
            "Citation schema is needed to load citation metadata."
        )

        data = citation_schema().load(citation_data)

        return data
