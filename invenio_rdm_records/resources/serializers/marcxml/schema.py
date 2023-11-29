# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""MARCXML based Schema for Invenio RDM Records."""

import bleach
from dateutil.parser import parse
from flask import current_app, g
from flask_resources.serializers import BaseSerializerSchema
from invenio_access.permissions import system_identity
from invenio_communities import current_communities
from invenio_communities.communities.services.service import get_cached_community_slug
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow import fields, missing
from marshmallow_utils.html import sanitize_unicode

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
    subjects = fields.Method("get_subjects", data_key="653  ")
    descriptions = fields.Method("get_descriptions", data_key="520  ")
    publication_information = fields.Method("get_pub_information", data_key="260  ")
    types = fields.Method(
        "get_types", data_key="901  "
    )  # Corresponds to resource_type in the metadata schema
    # TODO: sources = fields.List(fields.Str(), attribute="metadata.references")
    # sources = fields.Constant(missing)  # Corresponds to references in the metadata schema
    formats = fields.Method("get_formats", data_key="520 1")
    parent_id = fields.Method("get_parent_id", data_key="024 1")
    community_ids = fields.Method("get_communities", data_key="980  ")
    sizes = fields.Method("get_sizes", data_key="520 2")
    version = fields.Method("get_version", data_key="024 3")
    funding = fields.Method(
        "get_funding", data_key="856 1"
    )  # TODO this was not implemented on Zenodo, neither specified in marcxml
    updated = fields.Method("get_updated", data_key="005")
    files = fields.Method("get_files", data_key="8564 ")
    access = fields.Method("get_access", data_key="542  ")
    host_information = fields.Method("get_host_information", data_key="773  ")

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
        access = {"a": obj["access"]["record"]}
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

    def get_version(self, obj):
        """Get version."""
        v_ = obj["metadata"].get("version")
        if not v_:
            return missing

        version = {"a": v_}
        return version

    def get_sizes(self, obj):
        """Get sizes."""
        sizes_list = obj["metadata"].get("sizes", [])
        if not sizes_list:
            return missing

        sizes = [{"a": s} for s in sizes_list]
        return sizes

    def _get_communities_slugs(self, ids):
        """Get communities slugs."""
        service_id = current_communities.service.id
        return [
            get_cached_community_slug(community_id, service_id) for community_id in ids
        ]

    def get_communities(self, obj):
        """Get communities."""
        ids = obj["parent"].get("communities", {}).get("ids", [])
        if not ids:
            return missing
        # Communities are prefixed with ``user-``
        return [{"a": f"user-{slug}"} for slug in self._get_communities_slugs(ids)]

    def get_parent_id(self, obj):
        """Get parent id."""
        parent_id = {"a": obj["parent"]["id"]}
        return parent_id

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
            ids = obj["parent"].get("communities", {}).get("ids", [])
            for slug in self._get_communities_slugs(ids):
                user_slug = f"user-{slug}"
                # Add "p": [user_slug] or extend if there are already other communities
                result.setdefault("p", []).append(user_slug)

        return result or missing

    def _serialize_contributor(self, contributor):
        """Serializes one contributor."""
        name = contributor["person_or_org"]["name"]
        contributor_dict = dict(a=name)
        affiliations = contributor.get("affiliations", [])
        if affiliations:
            # Affiliation is not repeatable, we only get the first
            # (https://www.loc.gov/marc/bibliographic/bd700.html)
            affiliation = affiliations[0]["name"]
            contributor_dict["u"] = affiliation
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
        """Returns the fist autor of the list."""
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

    def get_titles(self, obj):
        """Get titles."""
        title = {"a": obj["metadata"]["title"]}
        return title

    def get_updated(self, obj):
        """Gets updated."""
        updated = str(parse(obj["updated"]).timestamp())
        return updated

    def get_id(self, obj):
        """Gets id."""
        id_ = obj["id"]
        return id_

    def get_funding(self, obj):
        """Get funding information."""

        def _serialize_funder(funding_object):
            """Serializes one funder."""
            funder = funding_object["funder"]
            award = funding_object.get("award", {})

            funder_string = ""

            if award:
                identifiers = award.get("identifiers", [])
                title = award.get("title", {})
                title = list(title.values())[0] if title else "null"
                number = award.get("number", "null")

                funder_string += f"award_title={title}; "
                funder_string += f"award_number={number}; "

                if identifiers:
                    identifier = identifiers[0]
                    scheme = identifier.get("scheme", "null")
                    identifier_value = identifier.get("identifier", "null")

                    funder_string += f"award_identifiers_scheme={scheme}; "
                    funder_string += (
                        f"award_identifiers_identifier={identifier_value}; "
                    )

            funder_id = funder["id"]
            funder_name = funder.get("name", "null")

            # Serialize funder
            funder_string += f"funder_id={funder_id}; "
            funder_string += f"funder_name={funder_name}; "

            return funder_string

        funders_list = obj["metadata"].get("funding", [])
        if not funders_list:
            return missing

        funding = [{"a": _serialize_funder(funder)} for funder in funders_list]

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

    def get_descriptions(self, obj):
        """Get descriptions."""

        def _serialize_description(description):
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

        metadata = obj["metadata"]
        descriptions = []

        description = metadata.get("description")
        if description:
            serialized = _serialize_description(description)
            descriptions.append(serialized)

        additional_descriptions = metadata.get("additional_descriptions", [])
        for add_desc in additional_descriptions:
            serialized = _serialize_description(add_desc["description"])
            descriptions.append(serialized)

        return descriptions or missing

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
        types = {"u": resource_type}
        return types or missing
