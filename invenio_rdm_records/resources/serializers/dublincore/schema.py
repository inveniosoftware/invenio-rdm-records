# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dublin Core based Schema for Invenio RDM Records."""

import bleach
import idutils
from flask_resources.serializers import BaseSerializerSchema
from invenio_base import invenio_url_for
from marshmallow import fields, missing
from pydash import py_

from ..schemas import CommonFieldsMixin
from ..ui.schema import current_default_locale
from ..utils import get_vocabulary_props


class DublinCoreSchema(BaseSerializerSchema, CommonFieldsMixin):
    """Schema for Dublin Core in JSON.

    The identifier handling behavior is determined by the schema's ``context``,
    particularly by the values ``urlize_identifiers`` and ``prefix_identifier_schemes``.
    Both of them are expected to be boolean values, and determine whether or not
    identifiers should be transformed into URLs if possible (like DOIs), and/or
    whether the scheme should be used as prefix (i.e. ``{scheme}:{identifier}``)
    for the identifier as fallback.
    """

    contributors = fields.Method("get_contributors")
    titles = fields.Method("get_titles")
    creators = fields.Method("get_creators")
    identifiers = fields.Method("get_identifiers")
    relations = fields.Method("get_relations")
    rights = fields.Method("get_rights")
    dates = fields.Method("get_dates")
    subjects = fields.Method("get_subjects")
    descriptions = fields.Method("get_descriptions")
    publishers = fields.Method("get_publishers")
    types = fields.Method("get_types")
    # TODO: sources = fields.List(fields.Str(), attribute="metadata.references")
    sources = fields.Constant(
        missing
    )  # Corresponds to references in the metadata schema
    languages = fields.Method("get_languages")
    locations = fields.Method("get_locations")
    formats = fields.Method("get_formats")

    def _transform_identifier(self, identifier, scheme):
        """Transform the raw identifier according to the rules in the ``context``.

        If the identifier can be turned into a URL (like DOIs and handles) and the
        ``context`` doesn't have a falsy ``urlize_identifiers`` value, it will
        be turned into a URL.
        Otherwise, and if the ``context`` has a truthy value for
        ``prefix_identifier_schemes``, the identifier will be prefixed with its scheme
        if it isn't prefixed yet.
        As a last resort, the original identifier will be returned as is.
        """
        urlize = self.context.get("urlize_identifiers", True)
        prefix_scheme = self.context.get("prefix_identifier_schemes", True)
        result = None

        if urlize:
            result = idutils.to_url(identifier, scheme, url_scheme="https")

        if not result and prefix_scheme and not identifier.startswith(scheme):
            result = f"{scheme}:{identifier}"

        return result or identifier

    def get_identifiers(self, obj):
        """Get identifiers."""
        items = []

        for scheme, pid in obj.get("pids", {}).items():
            items.append(self._transform_identifier(pid["identifier"], scheme))

        for id_ in obj["metadata"].get("identifiers", []):
            items.append(self._transform_identifier(id_["identifier"], id_["scheme"]))

        return items or missing

    def get_relations(self, obj):
        """Get relations."""
        rels = []

        # Fundings
        # FIXME: Add after UI support is there

        # Alternate identifiers
        for a in obj.get("metadata", {}).get("alternate_identifiers", []):
            rels.append(self._transform_identifier(a["identifier"], a["scheme"]))

        # Related identifiers
        for a in obj.get("metadata", {}).get("related_identifiers", []):
            rels.append(self._transform_identifier(a["identifier"], a["scheme"]))

        # Communities
        communities = obj.get("parent", {}).get("communities", {}).get("entries", [])
        for community in communities:
            slug = community["slug"]
            url = invenio_url_for(
                "invenio_app_rdm_communities.communities_home",
                pid_value=slug,
            )

            rels.append(self._transform_identifier(url, "url"))

        # Parent doi
        parent_pids = obj.get("parent", {}).get("pids", {})
        for key, value in parent_pids.items():
            if key == "doi":
                rels.append(self._transform_identifier(value["identifier"], key))

        return rels or missing

    def get_rights(self, obj):
        """Get rights."""
        rights = []

        access_right = py_.get(obj, "access.status")
        if access_right:
            if access_right == "metadata-only":
                access_right = "closed"

            rights.append(f"info:eu-repo/semantics/{access_right}Access")

        for right in obj.get("metadata", {}).get("rights", []):
            rights.append(right.get("title").get(current_default_locale()))
            if right.get("id"):
                license_url = right.get("props", {}).get("url")
                if license_url:
                    rights.append(license_url)
            else:
                license_url = right.get("link")
                if license_url:
                    rights.append(license_url)

        return rights or missing

    def get_dates(self, obj):
        """Get dates."""
        dates = []

        publication_date = py_.get(obj, "metadata.publication_date")
        if publication_date:
            dates.append(publication_date)

        access_right = py_.get(obj, "access.status")
        if access_right == "embargoed":
            date = obj["access"]["embargo"]["until"]
            dates.append(f"info:eu-repo/date/embargoEnd/{date}")

        return dates or missing

    def get_descriptions(self, obj):
        """Get descriptions."""
        metadata = obj["metadata"]
        descriptions = []

        description = metadata.get("description")
        if description:
            descriptions.append(description)

        additional_descriptions = metadata.get("additional_descriptions", [])
        for add_desc in additional_descriptions:
            descriptions.append(add_desc["description"])

        descriptions = [
            bleach.clean(
                desc,
                tags=[],
                attributes=[],
            )
            for desc in descriptions
        ]

        return descriptions or missing

    def get_subjects(self, obj):
        """Get subjects."""
        metadata = obj["metadata"]
        subjects = []
        subjects.extend(
            (s["subject"] for s in metadata.get("subjects", []) if s.get("subject"))
        )
        return subjects or missing

    def get_types(self, obj):
        """Get resource type."""
        resource_type_id = py_.get(obj, "metadata.resource_type.id")
        if not resource_type_id:
            return missing

        props = get_vocabulary_props(
            "resourcetypes",
            [
                "props.eurepo",
            ],
            resource_type_id,
        )
        t = props.get("eurepo")
        return [t] if t else missing

    def get_languages(self, obj):
        """Get languages."""
        languages = obj["metadata"].get("languages")

        if languages:
            return [language["id"] for language in languages]

        return missing

    def get_formats(self, obj):
        """Get data formats."""
        formats = obj["metadata"].get("formats", missing)
        return formats
