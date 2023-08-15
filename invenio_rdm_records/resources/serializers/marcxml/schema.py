# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""MARCXML based Schema for Invenio RDM Records."""

from copy import deepcopy

import bleach
from dateutil.parser import parse
from flask import current_app, g
from flask_resources.serializers import BaseSerializerSchema
from invenio_access.permissions import system_identity
from invenio_communities import current_communities
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow import fields, missing, post_dump

from ..schemas import CommonFieldsMixin
from ..ui.schema import current_default_locale
from ..utils import get_vocabulary_props


class MARCXMLSchema(BaseSerializerSchema, CommonFieldsMixin):
    """Schema for records in MARC."""

    id = fields.Str()
    doi = fields.Method("get_doi")
    oai = fields.Method("get_oai")
    contributors = fields.Method("get_contributors")
    titles = fields.Method("get_titles")
    first_creator = fields.Method("get_first_creator")
    other_creators = fields.Method("get_other_creators")
    relations = fields.Method("get_relations")
    rights = fields.Method("get_rights")
    dates = fields.Method("get_dates")
    subjects = fields.Method("get_subjects")
    descriptions = fields.Method("get_descriptions")
    publishers = fields.Method("get_publishers")
    types = fields.Method(
        "get_types"
    )  # Corresponds to resource_type in the metadata schema
    # TODO: sources = fields.List(fields.Str(), attribute="metadata.references")
    sources = fields.Constant(
        missing
    )  # Corresponds to references in the metadata schema
    formats = fields.Method("get_formats")
    parent_id = fields.Method("get_parent_id")
    community_ids = fields.Method("get_community_ids")
    last_updated = fields.Method("last_updated")
    sizes = fields.Method("get_sizes")
    version = fields.Method("get_version")
    funding = fields.Method("get_funding")
    updated = fields.Method("get_updated")
    files = fields.Method("get_files")
    access = fields.Method("get_access")
    parent_doi = fields.Method("get_parent_doi")
    related_identifiers = fields.Method("get_related_identifiers")
    imprint = fields.Method("get_imprint")

    def get_imprint(self, obj):
        """Get imprints."""
        custom_fields = obj.get("custom_fields", {})
        imprint_data = custom_fields.get("imprint:imprint", {})

        if not imprint_data:
            return missing

        imprint_dict = dict()

        title = imprint_data.get("title")
        isbn = imprint_data.get("isbn")
        pages = imprint_data.get("pages")
        place = imprint_data.get("place")
        publisher = obj["metadata"].get("publisher")

        list_of_values = [
            ("t", title),
            ("z", isbn),
            ("g", pages),
            ("a", place),
            ("b", publisher),
        ]
        for values in list_of_values:
            if values[1]:
                imprint_dict[values[0]] = values[1]

        return [imprint_dict]

    def get_related_identifiers(self, obj):
        """Get alternate identifiers."""
        related_identifiers = obj["metadata"].get("related_identifiers", [])
        related_identifiers_list = []
        for related_identifier in related_identifiers:
            related_identifier_dict = dict(
                a=related_identifier["identifier"],
                i=related_identifier["relation_type"]["title"]["en"],
                u=related_identifier["scheme"],
            )
            related_identifiers_list.append(related_identifier_dict)
        return related_identifiers_list or missing

    def get_parent_doi(self, obj):
        """Get parent doi."""
        parent_pids = obj["parent"].get("pids", {})
        for key, value in parent_pids.items():
            if key == "doi":
                return dict(n="doi", a=value["identifier"])

        return missing

    def get_access(self, obj):
        """Get access rights."""
        return dict(a=obj["access"]["record"])

    def get_files(self, obj):
        """Get files."""
        files_enabled = obj["files"].get("enabled", False)
        if not files_enabled:
            return missing
        files_entries = obj["files"].get("entries")
        record_id = obj["id"]
        files_list = []
        for key, value in files_entries.items():
            url = f"{current_app.config['SITE_UI_URL']}/records/{record_id}/files/{value['key']}"
            files_list.append(dict(s=str(value["size"]), z=value["checksum"], u=url))

        return files_list or missing

    def get_version(self, obj):
        """Get version."""
        version = obj["metadata"].get("version")
        if version:
            return dict(a=version)
        return missing

    def get_sizes(self, obj):
        """Get sizes."""
        sizes = obj["metadata"].get("sizes", [])
        sizes_list = []
        for sizes in sizes:
            sizes_list.append(dict(a=sizes))
        return sizes_list or missing

    def get_community_ids(self, obj):
        """Get community ids."""
        communities = obj["parent"].get("communities", {}).get("ids", [])
        communities_list = []
        for community_id in communities:
            community = current_communities.service.read(
                id_=community_id, identity=g.identity
            )
            communities_list.append(community.data["slug"])
        return communities_list or missing

    def get_parent_id(self, obj):
        """Get parent id."""
        return dict(a=obj["parent"]["id"])

    def get_formats(self, obj):
        """Get data formats."""
        formats = obj["metadata"].get("formats", [])
        formats_list = []
        for format_value in formats:
            formats_list.append(dict(a=format_value))
        return formats_list or missing

    def get_doi(self, obj):
        """Get DOI."""
        if "doi" in obj["pids"]:
            return dict([("2", "doi"), ("a", obj["pids"]["doi"]["identifier"])])

        for identifier in obj["metadata"].get("identifiers", []):
            if identifier["scheme"] == "doi":
                return dict([("2", "doi"), ("o", identifier["identifier"])])

        return missing

    def get_oai(self, obj):
        """Get OAI."""
        if "oai" in obj["pids"]:
            return [obj["pids"]["oai"]["identifier"]]

        return missing

    def get_other_creators(self, obj):
        """Get other creators."""
        creators = obj["metadata"].get("creators", [])
        creators_list = []
        for index, creator in enumerate(creators):
            if index == 0:
                continue
            name = creator["person_or_org"]["name"]
            creator_dict = dict(a=name)
            affiliations = creator.get("affiliations", [])
            if affiliations:
                # Affiliation is not repeatable, we only get the first
                # (https://www.loc.gov/marc/bibliographic/bd100.html)
                affiliation = affiliations[0]["name"]
                creator_dict["u"] = affiliation
            creators_list.append(creator_dict)
        return creators_list or missing

    def get_contributors(self, obj):
        """Get contributors."""
        contributors = obj["metadata"].get("contributors", [])
        contributors_list = []
        for index, contributor in enumerate(contributors):
            name = contributor["person_or_org"]["name"]
            contributor_dict = dict(a=name)
            affiliations = contributor.get("affiliations", [])
            if affiliations:
                # Affiliation is not repeatable, we only get the first
                # (https://www.loc.gov/marc/bibliographic/bd700.html)
                affiliation = affiliations[0]["name"]
                contributor_dict["u"] = affiliation
            contributors_list.append(contributor_dict)
        return contributors_list or missing

    def get_first_creator(self, obj):
        """Returns the fist autor of the list."""
        name = obj["metadata"].get("creators", [])[0]["person_or_org"]["name"]
        creator_dict = dict(a=name)
        affiliations = obj["metadata"].get("creators", [])[0].get("affiliations", [])
        if affiliations:
            # Affiliation is not repeatable, we only get the first (https://www.loc.gov/marc/bibliographic/bd100.html)
            affiliation = affiliations[0]["name"]
            creator_dict["u"] = affiliation
        return creator_dict

    def get_publishers(self, obj):
        """Get publishers."""
        publisher = obj["metadata"].get("publisher")
        if publisher:
            return [publisher]
        return missing

    def get_titles(self, obj):
        """Get titles."""
        return dict(a=obj["metadata"]["title"])

    def get_updated(self, obj):
        """Gets updated."""
        return str(parse(obj["updated"]).timestamp())

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
            funders.append(dict(a=funder_string))

        return funders

    def last_updated(self, obj):
        """Get date last updated."""
        return [obj["updated"]] or missing

    def get_relations(self, obj):
        """Get relations."""
        rels = []

        # Fundings
        # FIXME: Add after UI support is there

        # Alternate identifiers
        for a in obj["metadata"].get("alternate_identifiers", []):
            rels.append(dict(a=f"{a['scheme']}:{a['identifier']}"))

        # Related identifiers
        for a in obj["metadata"].get("related_identifiers", []):
            rels.append(dict(a=f"{a['scheme']}:{a['identifier']}"))

        return rels or missing

    def get_rights(self, obj):
        """Get rights."""
        rights = []
        access_right = obj.get("access", {}).get("status")

        if access_right:
            rights.append(dict(a=f"info:eu-repo/semantics/{access_right}Access"))

        if access_right == "metadata-only":
            access_right = "closed"

        ids = []
        for right in obj["metadata"].get("rights", []):
            _id = right.get("id")
            if _id:
                ids.append(_id)
            else:
                title = right.get("title").get(current_default_locale())
                right_dict = dict()
                if title:
                    right_dict["a"] = title
                license_url = right.get("link")
                if license_url:
                    right_dict["u"] = license_url
                rights.append(right_dict)

        if ids:
            vocab_rights = vocabulary_service.read_many(
                system_identity, "licenses", ids
            )
            for right in vocab_rights:
                title = right.get("title").get(current_default_locale())
                right_dict = dict()
                if title:
                    right_dict["a"] = title

                license_url = right.get("props").get("url")
                if license_url:
                    right_dict["u"] = license_url

                rights.append(right_dict)

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
            dict(
                a=bleach.clean(
                    desc,
                    strip=True,
                    strip_comments=True,
                    tags=[],
                    attributes=[],
                )
            )
            for desc in descriptions
        ]

        return descriptions or missing

    def get_subjects(self, obj):
        """Get subjects."""
        metadata = obj["metadata"]
        subjects = metadata.get("subjects", [])
        subjects_list = []
        for subject in subjects:
            subjects_list.append(dict(a=subject["subject"]))
        return subjects_list or missing

    def get_types(self, obj):
        """Get resource type."""
        props = get_vocabulary_props(
            "resourcetypes",
            [
                "props.eurepo",
            ],
            obj["metadata"]["resource_type"]["id"],
        )
        resource_type = props.get("eurepo")
        return dict(u=resource_type) if resource_type else missing

    # FIXME should this be a processor? that's somehow the post_dump place
    # otherwise we cannot guarantee order
    @post_dump()
    def keys_to_tags(self, data, many, **kwargs):
        """Changes the key name to the corresponding MARCXML tag (number)."""
        # [!] The datafield value corresponds to  tag[0:3] + ind1[3] + ind2[4]
        # [!] The datafield needs to be length *5* (this is to do with the dojson parser)
        # [!] The subfield code is set in the schema values unless different values have to appear in the same datafield

        # Example:
        # {
        # "other_creators" : {"datafield": "700  "}
        # "contributors" : {"datafield": "700  "}
        # }

        #   <datafield tag="700" ind1=" " ind2=" ">
        #       <subfield code="a">Tarocco, Nicola</subfield>
        #   </datafield>
        #   <datafield tag="700" ind1=" " ind2=" ">
        #       <subfield code="a">Nielsen, Lars</subfield>
        #   </datafield>

        # Example of subfield:
        # {
        #   "publishers" : {"datafield": "260  " ,"subfield": "a"}
        #   "updated" : {"datafield": "260  " ,"subfield": "c"}
        # }

        #   <datafield tag="260" ind1=" " ind2=" ">
        #       <subfield code="a">CERN</subfield>
        #       <subfield code="a">Tarocco, Nicola</subfield>
        #   </datafield>

        # To add support for more tags, use the corresponding codes from here
        # https://scoap3.org/scoap3-repository/marcxml/

        datafield_changes = {
            "contributors": {"datafield": "700  "},
            "other_creators": {"datafield": "700  "},  # Abstract
            "titles": {"datafield": "245  "},  # Title
            "first_creator": {"datafield": "100  "},  # First author
            "oai": {"datafield": "909CO", "subfield": "o"},  # OAI
            "community_ids": {"datafield": "909CO", "subfield": "a"},  # OAI
            "relations": {"datafield": "856 2"},  # Related Resource
            "rights": {"datafield": "540  "},  # License
            "dates": {
                "datafield": "260  ",
                "subfield": "c",
            },  # Publication Information - Date of Publication
            "subjects": {"datafield": "653  "},  # Keywords
            "descriptions": {"datafield": "520  "},  # Abstract
            "publishers": {
                "datafield": "260  ",
                "subfield": "a",
            },  # Publication Information - Publisher Name
            "types": {"datafield": "901  "},  # Local Implementation
            "sources": {"datafield": "246i "},  # Source
            "coverage": {"datafield": "510  "},  # Location
            "formats": {"datafield": "520 1"},  # Formats
            "parent_id": {"datafield": "024 1"},  # ID
            "last_updated": {
                "datafield": "260  ",
                "subfield": "c",
            },  # Publication Information - Date of Publication
            "sizes": {"datafield": "520 2"},  # Abstract
            "version": {"datafield": "024 3"},  # ID
            "funding": {"datafield": "856 1"},  # Related Resource
            "files": {"datafield": "8564 "},  # Files
            "access": {"datafield": "542  "},  # Related Resource
            "doi": {"datafield": "024  "},  # Related Resource
            "parent_doi": {"datafield": "773  "},  # Parent doi
            "related_identifiers": {"datafield": "773  "},  # Related identifiers
            "imprint": {"datafield": "773  "},  # Imprint
        }

        controlfield_changes = {
            "updated": {"controlfield": "005"},
            "id": {"controlfield": "001"},
        }

        data_copy = deepcopy(data)
        for key in data_copy:
            if key in datafield_changes:
                subfield = datafield_changes[key].get("subfield")
                if subfield:
                    datafield = datafield_changes[key]["datafield"]
                    subfield_key = datafield_changes[key]["subfield"]

                    data.setdefault(datafield, {})
                    data[datafield].setdefault(subfield_key, [])
                    data[datafield][subfield_key].extend(data.pop(key))
                else:
                    field_changes = datafield_changes[key]
                    datafield = field_changes["datafield"]
                    if isinstance(data_copy[key], list):
                        data.setdefault(datafield, []).extend(data.pop(key))
                    else:
                        data[datafield] = [data.pop(key)]
            elif key in controlfield_changes:
                controlfield = controlfield_changes[key]["controlfield"]
                data[controlfield] = data.pop(key)

        # Adds community ids here to avoid fetching them again
        if data_copy.get("community_ids"):
            communities_980 = []
            for community_id in data_copy.get("community_ids"):
                communities_980.append(dict(a=community_id))
            data["980  "] = communities_980

        return data
