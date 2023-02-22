# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""MARCXML based Schema for Invenio RDM Records."""

import bleach
from copy import deepcopy
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow import Schema, fields, missing, post_dump

from ..ui.schema import current_default_locale
from ..utils import get_vocabulary_props


class MARCXMLSchema(Schema):
    """Schema for records in MARC."""

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
    types = fields.Method(
        "get_types"
    )  # Corresponds to ressource_type in the metadata schema
    sources = fields.Method(
        "get_sources"
    )  # Corresponds to references in the metadata schema
    coverage = fields.Method(
        "get_locations"
    )  # Corresponds to locations in the metadata schema
    formats = fields.Method("get_formats")
    parent_id = fields.Method("get_id")  # No GOOD
    community_id = fields.Method("get_id_community")
    last_updated = fields.Method("last_updated")
    sizes = fields.Method("get_sizes")
    version = fields.Method("get_version")
    funding = fields.Method("get_funding")

    def get_version(self, obj):
        """Get the version of the record."""
        return obj["metadata"].get("version", missing)

    def get_sizes(self, obj):
        """Get the size of the record."""
        return obj["metadata"].get("sizes", missing)

    def get_funding(self, obj):
        """Get funding information."""
        if "funding" not in obj["metadata"]:
            return missing

        funders = []
        all_funders = obj["metadata"].get("funding", [])

        for funder in all_funders:
            funder_string = ""

            award = funder.get("award", {})

            identifier = award.get("identifiers", [{}])[0]
            scheme = identifier.get("scheme", "null")
            identifier_value = identifier.get("identifier", "null")

            title = award.get("title", {})
            title = list(title.values())[0] if title else "null"

            number = award.get("number", "null")
            id = funder["funder"]["id"]
            name = funder["funder"].get("name", "null")

            funder_string += f"award_identifiers_scheme={scheme}; "
            funder_string += f"award_identifiers_identifier={identifier_value}; "
            funder_string += f"award_title={title}; "
            funder_string += f"award_number={number}; "
            funder_string += f"funder_id={id}; "
            funder_string += f"funder_name={name}; "
            funders.append(funder_string)

        return funders

    def last_updated(self, obj):
        """Get date last updated."""
        return [obj["updated"]]

    def get_locations(self, obj):
        """Get locations."""
        locations = []

        access_location = obj["metadata"].get("locations", [])
        if not access_location:
            return missing

        for location in access_location.get("features", []):
            location_string = ""

            place = location.get("place")
            description = location.get("description")
            if place:
                location_string += f"name={place}; "
            if description:
                location_string += f"description={description}"
            geometry = location.get("geometry")
            if geometry:
                geo_type = geometry["type"]
                if geo_type == "Point":
                    coords = geometry["coordinates"]
                    location_string += f"; lat={coords[0]}; lon={coords[1]}"

            locations.append(location_string)

        return locations

    def get_id_community(self, obj):
        """Get community IDs."""
        if "parent" in obj:
            return obj["parent"]["communities"].get("ids", missing)
        return missing

    def get_id(self, obj):
        """Get ID."""
        if "parent" in obj:
            return obj["parent"]["id"]
        return missing

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
        access_right = obj.get("access", {}).get("status")

        if access_right:
            rights.append(f"info:eu-repo/semantics/{access_right}Access")

        if access_right == "metadata-only":
            access_right = "closed"

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

        access_status = obj.get("access", {}).get("status", {})

        if access_status == "embargoed":
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

    def get_formats(self, obj):
        """Get data formats."""
        formats = obj["metadata"].get("formats", missing)
        return formats

    @post_dump()
    def changeKeysToTags(self, data, many, **kwargs):
        """Changes the key name to the corresponding MARCXML tag (number)."""
        # [!] The string in the first array corresponds to the tag[0:4] + ind1[4] + ind2[5]
        # [!] The first string needs to be length *5* (this is to do with the dojson parser)
        # [!] The second string corresponds to the subfield code

        # Example: "creators" : ["100a ", "a"]

        #   <datafield tag="100" ind1="a" ind2=" ">
        #       <subfield code="a">Tarocco, Nicola</subfield>
        #   </datafield>

        # To add support for more tags, use the corresponding codes from here
        # https://scoap3.org/scoap3-repository/marcxml/

        changes = {
            "contributors": ["700a ", "u"],  # Abstract
            "titles": ["245a ", "a"],  # Title
            "creators": ["100a ", "a"],  # First author
            "identifiers": ["024  ", "a"],  # DOI
            "relations": ["856 2", "a"],  # Related Ressource
            "rights": ["540  ", "a"],  # License
            "dates": [
                "260c ",
                "c",
            ],  # Publication Information - Date of Publication
            "subjects": ["653  ", "a"],  # Keywords
            "descriptions": ["520  ", "a"],  # Abstract
            "publishers": [
                "260b ",
                "a",
            ],  # Publication Information - Publisher Name
            "types": ["901  ", "u"],  # Local Implementation
            "sources": ["246i ", "x"],  # Source
            "coverage": ["510  ", "a"],  # Location
            "formats": ["520 1", "a"],  # Abstract
            "parent_id": ["024 1", "a"],  # ID
            "community_id": ["024 2", "a"],  # ID
            "last_updated": [
                "260ca",
                "c",
            ],  # Publication Information - Date of Publication
            "sizes": ["520 2", "a"],  # Abstract
            "version": ["024 3", "a"],  # ID
            "funding": ["856 1", "a"],  # Related Ressource
        }

        data_copy = deepcopy(data)
        for key in data_copy:
            if key in changes:
                data[changes[key][0]] = {changes[key][1]: data.pop(key)}

        return data
