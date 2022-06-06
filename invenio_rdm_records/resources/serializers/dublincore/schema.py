# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dublin Core based Schema for Invenio RDM Records."""

import bleach
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow import Schema, fields, missing

from ..ui.schema import current_default_locale
from ..utils import get_vocabulary_props


class DublinCoreSchema(Schema):
    """Schema for Dublin Core in JSON."""

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
    sources = fields.Method("get_sources")
    languages = fields.Method("get_languages")
    coverage = fields.Method("get_locations")
    formats = fields.Method("get_formats")

    def get_titles(self, obj):
        """Get titles."""
        return [obj["metadata"]["title"]]

    def get_identifiers(self, obj):
        """Get identifiers."""
        items = []
        items.extend(i["identifier"] for i in obj["metadata"].get("identifiers", []))
        items.extend(p["identifier"] for p in obj.get("pids", {}).values())

        return items or missing

    def get_creators(self, obj):
        """Get creators."""
        return [c["person_or_org"]["name"] for c in obj["metadata"].get("creators", [])]

    def get_relations(self, obj):
        """Get relations."""
        rels = []

        # Fundings
        # FIXME: Add after UI support is there

        # Alternate identifiers
        for a in obj["metadata"].get("alternate_identifiers", []):
            rels.append(f"{a['scheme']}:{a['identifier']}")

        # Related identifiers
        for a in obj["metadata"].get("related_identifiers", []):
            rels.append(f"{a['scheme']}:{a['identifier']}")

        return rels or missing

    def get_rights(self, obj):
        """Get rights."""
        rights = []

        access_right = obj["access"]["status"]
        if access_right == "metadata-only":
            access_right = "closed"

        rights.append(f"info:eu-repo/semantics/{access_right}Access")

        ids = []
        for right in obj["metadata"].get("rights", []):
            _id = right.get("id")
            if _id:
                ids.append(_id)
            else:
                title = right.get("title").get(current_default_locale())
                if title:
                    rights.append(title)

                license_url = right.get("link")
                if license_url:
                    rights.append(license_url)

        if ids:
            vocab_rights = vocabulary_service.read_many(
                system_identity, "licenses", ids
            )
            for right in vocab_rights:
                title = right.get("title").get(current_default_locale())
                if title:
                    rights.append(title)

                license_url = right.get("props").get("url")
                if license_url:
                    rights.append(license_url)

        return rights or missing

    def get_dates(self, obj):
        """Get dates."""
        dates = [obj["metadata"]["publication_date"]]

        if obj["access"]["status"] == "embargoed":
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
                strip=True,
                strip_comments=True,
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

    def get_publishers(self, obj):
        """Get publishers."""
        publisher = obj["metadata"].get("publisher")
        if publisher:
            return [publisher]

        return missing

    def get_contributors(self, obj):
        """Get contributors."""
        return [
            c["person_or_org"]["name"] for c in obj["metadata"].get("contributors", [])
        ] or missing

    def get_types(self, obj):
        """Get resource type."""
        props = get_vocabulary_props(
            "resourcetypes",
            [
                "props.eurepo",
            ],
            obj["metadata"]["resource_type"]["id"],
        )
        t = props.get("eurepo")
        return [t] if t else missing

    def get_sources(self, obj):
        """Get sources."""
        return missing

    def get_languages(self, obj):
        """Get languages."""
        languages = obj["metadata"].get("languages")

        if languages:
            return [language["id"] for language in languages]

        return missing

    def get_locations(self, obj):
        """Get locations."""
        # FIXME: Add after UI support is there
        # locations = []
        # for location in obj['metadata'].get('locations', []):
        #     location_string = ""
        #     place = location.get('place')
        #     if place:
        #         location_string += f"name={place}"

        #     geometry = location.get('geometry')
        #     if geometry:
        #         geo_type = geometry['type']
        #         if geo_type == "Point":
        #             coords = geometry['coordinates']
        #             location_string += f"; lat={coords[0]}; lon={coords[1]}"

        #     locations.append(location_string)
        return missing

    def get_formats(self, obj):
        """Get data formats."""
        formats = obj["metadata"].get("formats", missing)
        return formats
