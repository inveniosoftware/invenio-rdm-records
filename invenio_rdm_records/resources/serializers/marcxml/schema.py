# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""MARCXML based Schema for Invenio RDM Records."""

import bleach
from dateutil.parser import parse
from dojson.contrib.to_marc21.fields.bdleader import to_leader
from flask import current_app
from flask_resources.serializers import BaseSerializerSchema
from marshmallow import fields, missing
from marshmallow_utils.html import sanitize_unicode
from pydash import py_

from ..schemas import CommonFieldsMixin
from ..ui.schema import current_default_locale
from ..utils import get_vocabulary_props


class MARCXMLSchema(BaseSerializerSchema, CommonFieldsMixin):
    """Schema for records in MARC."""

    id = fields.Method("get_id", data_key="001")
    doi = fields.Method("get_doi", data_key="024  ")
    oai = fields.Method("get_oai", data_key="909CO")
    contributors = fields.Method("get_contributors", data_key="700  ")
    titles = fields.Method("get_titles", data_key="245  ")
    first_creator = fields.Method("get_first_creator", data_key="100  ")
    relations = fields.Method("get_relations", data_key="856 2")
    rights = fields.Method("get_rights", data_key="540  ")
    license = fields.Method("get_license", data_key="65017")
    subjects = fields.Method("get_subjects", data_key="653  ")
    descriptions = fields.Method("get_descriptions", data_key="520  ")
    additional_descriptions = fields.Method(
        "get_additional_descriptions", data_key="500  "
    )
    languages = fields.Method("get_languages", data_key="041  ")
    references = fields.Method("get_references", data_key="999C5")
    publication_information = fields.Method("get_pub_information", data_key="260  ")
    dissertation_note = fields.Method("get_dissertation_note", data_key="502  ")
    types_and_community_ids = fields.Method(
        "get_types_and_communities", data_key="980  "
    )  # Corresponds to resource_type in the metadata schema
    # TODO: sources = fields.List(fields.Str(), attribute="metadata.references")
    # sources = fields.Constant(missing)  # Corresponds to references in the metadata schema
    formats = fields.Method("get_formats", data_key="520 1")
    sizes = fields.Method("get_sizes", data_key="520 2")
    funding = fields.Method(
        "get_funding", data_key="536  "
    )  # TODO this was not implemented on Zenodo, neither specified in marcxml
    updated = fields.Method("get_updated", data_key="005")
    files = fields.Method("get_files", data_key="8564 ")
    access = fields.Method("get_access", data_key="542  ")
    host_information = fields.Method("get_host_information", data_key="773  ")
    leader = fields.Method("get_leader")

    def get_leader(self, obj):
        """Return the leader information."""
        rt = obj["metadata"]["resource_type"]["id"]
        rec_types = {
            "image": "two-dimensional_nonprojectable_graphic",
            "video": "projected_medium",
            "dataset": "computer_file",
            "software": "computer_file",
        }
        type_of_record = rec_types[rt] if rt in rec_types else "language_material"
        res = {
            "record_length": "00000",
            "record_status": "new",
            "type_of_record": type_of_record,
            "bibliographic_level": "monograph_item",
            "type_of_control": "no_specified_type",
            "character_coding_scheme": "marc-8",
            "indicator_count": 2,
            "subfield_code_count": 2,
            "base_address_of_data": "00000",
            "encoding_level": "unknown",
            "descriptive_cataloging_form": "unknown",
            "multipart_resource_record_level": "not_specified_or_not_applicable",
            "length_of_the_length_of_field_portion": 4,
            "length_of_the_starting_character_position_portion": 5,
            "length_of_the_implementation_defined_portion": 0,
            "undefined": 0,
        }
        return to_leader(None, None, res)

    def get_host_information(self, obj):
        """Get host information.

        Contains related identifiers as well as the parent DOI.
        """
        host_information = []

        # Related identifiers
        related_identifiers = obj["metadata"].get("related_identifiers", [])
        for identifier in related_identifiers:
            related_identifier = {
                "a": identifier["identifier"],
                "i": identifier["relation_type"]["title"]["en"],
                "n": identifier["scheme"],
            }
            host_information.append(related_identifier)

        # Parent DOI
        parent_pids = obj["parent"].get("pids", {})
        for key, value in parent_pids.items():
            if key == "doi":
                parent_doi = {
                    "a": value["identifier"],  # identifier
                    "i": "isVersionOf",  # relation type with parent is "isVersionOf"
                    "n": "doi",  # scheme
                }
                host_information.append(parent_doi)
                break

        return host_information or missing

    def get_access(self, obj):
        """Get access rights."""
        access = {"l": obj["access"]["status"]}
        return access

    def get_files(self, obj):
        """Get files."""
        files_enabled = obj["files"].get("enabled", False)
        if not files_enabled:
            return missing
        files_entries = obj["files"].get("entries", {})
        record_id = obj["id"]
        files = []
        for file_entry in files_entries.values():
            file_name = sanitize_unicode(file_entry["key"])
            url = f"{current_app.config['SITE_UI_URL']}/records/{record_id}/files/{file_name}"
            file_ = {
                "s": str(file_entry["size"]),  # file size
                "z": file_entry["checksum"],  # check sum
                "u": url,  # url
            }
            files.append(file_)

        return files or missing

    def get_sizes(self, obj):
        """Get sizes."""
        sizes_list = obj["metadata"].get("sizes", [])
        if not sizes_list:
            return missing

        sizes = [{"a": s} for s in sizes_list]
        return sizes

    def get_communities(self, obj):
        """Get communities."""
        communities = obj["parent"].get("communities", {}).get("entries", [])

        if not communities:
            return missing

        slugs = [community.get("slug") for community in communities]
        # Communities are prefixed with "user-"
        return [{"a": f"user-{slug}"} for slug in slugs]

    def get_formats(self, obj):
        """Get data formats."""
        formats_list = obj["metadata"].get("formats", [])
        if not formats_list:
            return missing

        formats = [{"a": f} for f in formats_list]
        return formats

    def get_doi(self, obj):
        """Get DOI."""
        if "doi" in obj["pids"]:
            return dict([("2", "doi"), ("a", obj["pids"]["doi"]["identifier"])])

        for identifier in obj["metadata"].get("identifiers", []):
            if identifier["scheme"] == "doi":
                return dict([("2", "doi"), ("o", identifier["identifier"])])

        return missing

    def get_oai(self, obj):
        """Get oai information.

        Contains OAI and communities. It should serialize into:

        .. code-block:: xml

            <datafield tag="909" ind1="C" ind2="O">
                <subfield code="p">user-community_name1</subfield>
                <subfield code="p">user-community_name2</subfield>
                <subfield code="o">oai:invenio.org:123456</subfield>
            </datafield>

        Communities slugs are prefixed with ``user-``.
        """
        result = {}

        # OAI
        if "oai" in obj["pids"]:
            identifier = [obj["pids"]["oai"]["identifier"]]
            result.update({"o": identifier})

            # Communities
            communities = obj["parent"].get("communities", {}).get("entries", [])
            if communities:
                for community in communities:
                    slug = community.get("slug")
                    if slug:
                        user_slug = f"user-{slug}"
                        # Add "p": [user_slug] or extend if there are already other communities
                        result.setdefault("p", []).append(user_slug)

        return result or missing

    def _serialize_contributor(self, contributor):
        """Serializes one contributor."""
        name = contributor["person_or_org"]["name"]
        contributor_dict = dict(a=name)

        identifiers = contributor["person_or_org"].get("identifiers", [])
        for identifier in identifiers:
            if identifier["scheme"] in ["gnd", "orcid"]:
                contributor_dict.setdefault("0", []).append(
                    "({0}){1}".format(identifier["scheme"], identifier["identifier"])
                )

        affiliations = contributor.get("affiliations", [])
        if affiliations:
            # Affiliation is not repeatable, we only get the first
            # (https://www.loc.gov/marc/bibliographic/bd700.html)
            affiliation = affiliations[0]["name"]
            contributor_dict["u"] = affiliation

        role_id = contributor.get("role", {}).get("id", "")
        if role_id:
            props = get_vocabulary_props("contributorsroles", ["props.marc"], role_id)
            marc_role = props.get("marc")
            if marc_role:
                contributor_dict["4"] = marc_role

        return contributor_dict

    def get_contributors(self, obj):
        """Get contributors."""
        contrib_list = []

        # Main contributors
        for contributor in obj["metadata"].get("contributors", []):
            serialized_creator = self._serialize_contributor(contributor)
            contrib_list.append(serialized_creator)

        # Other creators
        for index, creator in enumerate(obj["metadata"].get("creators", [])):
            # First creator is serialized in another field
            if index == 0:
                continue
            serialized_creator = self._serialize_contributor(creator)
            contrib_list.append(serialized_creator)

        return contrib_list or missing

    def get_first_creator(self, obj):
        """Returns the fist author of the list."""
        creators = obj["metadata"].get("creators", [])
        if not creators:
            return missing
        creator = creators[0]
        serialized = self._serialize_contributor(creator)
        return serialized

    def get_pub_information(self, obj):
        """Get publication information.

        Includes publication dates and publisher.
        """
        # Publisher
        pub = obj["metadata"].get("publisher")
        dates_list = [obj["metadata"]["publication_date"]]

        if not (pub or dates_list):
            return missing

        pub_information = {}

        if pub:
            pub_information.update({"b": pub})

        # Dates
        pub_date = obj["metadata"]["publication_date"]
        pub_information.setdefault("c", []).append(pub_date)

        access_status = obj.get("access", {}).get("status", "")

        if access_status == "embargoed":
            embargo_date = obj["access"]["embargo"]["until"]
            serialized_date = f"info:eu-repo/date/embargoEnd/{embargo_date}"
            pub_information.setdefault("c", []).append(serialized_date)

        return pub_information

    def get_dissertation_note(self, obj):
        """Get dissertation note."""
        name_of_granting_institution = obj.get("custom_fields", {}).get(
            "thesis:university"
        )
        if not name_of_granting_institution:
            return missing

        dissertation_note = {"c": name_of_granting_institution}
        return dissertation_note

    def get_titles(self, obj):
        """Get titles."""
        title = {"a": obj["metadata"]["title"]}
        return title

    def get_updated(self, obj):
        """Gets updated."""
        updated = parse(obj["updated"]).strftime("%Y%m%d%H%M%S.0")
        return updated

    def get_id(self, obj):
        """Gets id."""
        id_ = obj["id"]
        return id_

    def get_funding(self, obj):
        """Get funding information."""

        def _serialize_funder(funding_object):
            """Serializes one funder."""
            award = funding_object.get("award", {})
            award_title = award.get("title", {}).get("en")
            award_number = award.get("number")

            serialized_funder = {}
            if award_number:
                serialized_funder["c"] = award_number
            if award_title:
                serialized_funder["a"] = award_title

            return serialized_funder

        funders_list = obj["metadata"].get("funding", [])
        if not funders_list:
            return missing

        funding = [_serialize_funder(funder) for funder in funders_list]

        return funding

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

        for right in obj["metadata"].get("rights", []):
            title = right.get("title").get(current_default_locale())
            right_dict = dict()
            if title:
                right_dict["a"] = title
            license_url = right.get("link")
            if license_url:
                right_dict["u"] = license_url
            else:
                props_license_url = right.get("props", {}).get("url")
                if props_license_url:
                    right_dict["u"] = props_license_url
            rights.append(right_dict)

        return rights or missing

    def get_license(self, obj):
        """Get license.

        Same data as get_rights but duplicated for backwards compatibility reasons.
        """
        license = []
        for right in obj["metadata"].get("rights", []):
            license_dict = {}
            id = right.get("id")
            if id:
                license_dict["a"] = id
            scheme = right.get("props", {}).get("scheme")
            if scheme:
                license_dict["2"] = scheme

            license.append(license_dict)

        return license or missing

    def _serialize_description(self, description):
        """Serializes one description.

        The description string is sanitized using ``bleach.clean``.
        """
        return {
            "a": bleach.clean(
                description,
                tags=[],
                attributes=[],
            )
        }

    def get_descriptions(self, obj):
        """Get descriptions."""
        metadata = obj["metadata"]
        descriptions = []

        description = metadata.get("description")
        if description:
            serialized = self._serialize_description(description)
            descriptions.append(serialized)

        return descriptions or missing

    def get_additional_descriptions(self, obj):
        """Get additional descriptions."""
        metadata = obj["metadata"]
        additional_descriptions = []

        for add_desc in metadata.get("additional_descriptions", []):
            serialized = self._serialize_description(add_desc["description"])
            additional_descriptions.append(serialized)

        return additional_descriptions or missing

    def get_languages(self, obj):
        """Get languages."""
        languages = obj["metadata"].get("languages")

        if languages:
            return [{"a": language["id"]} for language in languages]

        return missing

    def get_references(self, obj):
        """Get references."""
        references_list = obj["metadata"].get("references", [])

        if references_list:
            return [{"x": reference["reference"]} for reference in references_list]

        return missing

    def get_subjects(self, obj):
        """Get subjects."""
        metadata = obj["metadata"]
        subjects = metadata.get("subjects", [])

        if not subjects:
            return missing

        subjects_list = []
        for subject in subjects:
            subjects_list.append({"a": subject["subject"]})
        return subjects_list

    def get_types_and_communities(self, obj):
        """Get resource type."""
        output = []
        communities = obj["parent"].get("communities", {}).get("entries", [])
        if communities:
            slugs = [community.get("slug") for community in communities]
            output += [{"a": f"user-{slug}"} for slug in slugs]

        resource_type_id = py_.get(obj, "metadata.resource_type.id")
        if resource_type_id:
            props = get_vocabulary_props(
                "resourcetypes",
                [
                    "props.eurepo",
                    "props.marc21_type",
                    "props.marc21_subtype",
                ],
                resource_type_id,
            )
            props_eurepo = props.get("eurepo")
            if props_eurepo:
                eurepo = {"a": props_eurepo}
                output.append(eurepo)

            resource_types = {}

            resource_type = props.get("marc21_type")
            if resource_type:
                resource_types["a"] = resource_type
            resource_subtype = props.get("marc21_subtype")
            if resource_subtype:
                resource_types["b"] = resource_subtype

            if resource_types:
                output.append(resource_types)

        return output or missing
