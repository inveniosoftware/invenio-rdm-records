# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Signposting schemas."""

import idutils
from marshmallow import Schema, fields, missing

from ...urls import download_url_for
from ..utils import get_vocabulary_props


class LandingPageSchema(Schema):
    """Schema for serialization of link context object for the landing page.

    Serialization input (`obj`) is a whole record dict projection.
    """

    anchor = fields.Method(serialize="serialize_anchor")
    author = fields.Method(serialize="serialize_author")
    cite_as = fields.Method(data_key="cite-as", serialize="serialize_cite_as")
    describedby = fields.Method(serialize="serialize_describedby")
    item = fields.Method(serialize="serialize_item")
    license = fields.Method(serialize="serialize_license")
    type = fields.Method(serialize="serialize_type")

    def serialize_anchor(self, obj, **kwargs):
        """Seralize to landing page URL."""
        return obj["links"]["self_html"]

    def serialize_author(self, obj, **kwargs):
        """Serialize author(s).

        For now, the first linkable identifier is taken.
        """

        def pick_linkable_id(identifiers):
            for id_dict in identifiers:
                url = idutils.to_url(
                    id_dict["identifier"], id_dict["scheme"], url_scheme="https"
                )
                if url:
                    return url
                else:
                    continue
            return None

        metadata = obj["metadata"]
        result = [
            {"href": pick_linkable_id(c["person_or_org"].get("identifiers", []))}
            for c in metadata.get("creators", [])
        ]
        result = [r for r in result if r["href"]]
        return result or missing

    def serialize_cite_as(self, obj, **kwargs):
        """Serialize cite-as."""
        identifier = obj.get("pids", {}).get("doi", {}).get("identifier")
        if not identifier:
            return missing

        url = idutils.to_url(identifier, "doi", "https")

        return [{"href": url}] if url else missing

    def serialize_describedby(self, obj, **kwargs):
        """Serialize describedby."""
        # Has to be placed here to prevent circular dependency.
        from invenio_rdm_records.resources.config import record_serializers

        result = [
            {"href": obj["links"]["self"], "type": mimetype}
            for mimetype in sorted(record_serializers)
        ]

        return result or missing

    def serialize_item(self, obj, **kwargs):
        """Serialize item."""
        file_entries = obj.get("files", {}).get("entries", {})

        result = [
            {
                "href": download_url_for(pid_value=obj["id"], filename=entry["key"]),
                "type": entry["mimetype"],
            }
            for entry in file_entries.values()
        ]

        return result or missing

    def serialize_license(self, obj, **kwargs):
        """Serialize license.

        Note that we provide an entry for each license (rather than just 1).
        """
        rights = obj["metadata"].get("rights", [])

        def extract_link(right):
            """Return link associated with right.

            There are 2 types of right representations:
             - custom
             - controlled vocabulary

            If no associated link returns None.
            """
            # Custom
            if right.get("link"):
                return right["link"]
            # Controlled vocabulary
            elif right.get("props"):
                return right["props"].get("url")

        result = [extract_link(right) for right in rights]
        result = [{"href": link} for link in result if link]
        return result or missing

    def serialize_type(self, obj, **kwargs):
        """Serialize type."""
        resource_type = obj["metadata"]["resource_type"]

        props = get_vocabulary_props(
            "resourcetypes",
            [
                "props.schema.org",
            ],
            resource_type["id"],
        )
        url_schema_org = props.get("schema.org")

        result = []
        if url_schema_org:
            result.append({"href": url_schema_org})
        # always provide About Page
        result.append({"href": "https://schema.org/AboutPage"})

        return result


class ContentResourceSchema(Schema):
    """Schema for serialization of link context object for the content resource.

    Serialization input (`obj`) is a file entry dict projection.

    Passing a context={"record_dict"} to the constructor is required.
    """

    anchor = fields.Method(serialize="serialize_anchor")
    collection = fields.Method(serialize="serialize_collection")

    def serialize_anchor(self, obj, **kwargs):
        """Serialize to download url."""
        pid_value = self.context["record_dict"]["id"]
        return download_url_for(pid_value=pid_value, filename=obj["key"])

    def serialize_collection(self, obj, **kwargs):
        """Serialize to record landing page url."""
        return [
            {
                "href": self.context["record_dict"]["links"]["self_html"],
                "type": "text/html",
            }
        ]


class MetadataResourceSchema(Schema):
    """Schema for serialization of link context object for the metadata resource.

    Serialization input (`obj`) is a whole record dict projection.

    Passing a context={"record_dict"} to the constructor is required.
    """

    anchor = fields.Method(serialize="serialize_anchor")
    describes = fields.Method(serialize="serialize_describes")

    def serialize_anchor(self, obj, **kwargs):
        """Serialize to API url."""
        return obj["links"]["self"]

    def serialize_describes(self, obj, **kwargs):
        """Serialize to record landing page url."""
        return [
            {
                "href": obj["links"]["self_html"],
                "type": "text/html",
            }
        ]


class FAIRSignpostingProfileLvl2Schema(Schema):
    """FAIR Signposting Profile Lvl 2 Schema.

    See https://signposting.org/FAIR/
    """

    linkset = fields.Method(serialize="serialize_linkset")

    def serialize_linkset(self, obj, **kwargs):
        """Serialize linkset."""
        result = [LandingPageSchema().dump(obj)]

        content_resource_schema = ContentResourceSchema(context={"record_dict": obj})
        result += [
            content_resource_schema.dump(entry)
            for entry in obj.get("files", {}).get("entries", {}).values()
        ]

        # Only a single metadata link context object is appropriate given our usage of
        # content-negotiation per discussion with Signposting authors
        result += [MetadataResourceSchema().dump(obj)]

        return result
