# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSL based Schema for Invenio RDM Records."""

from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow import Schema, fields, missing, post_dump
from marshmallow_utils.fields import SanitizedUnicode


class PersonOrOrgSchemaCSL(Schema):
    """Creator/contributor common schema for v4."""

    family = fields.Str(attribute="person_or_org.name")

    @post_dump(pass_many=False)
    def capitalize_name_type(self, data, **kwargs):
        """Capitalize type."""
        if data.get("nameType"):
            data["nameType"] = data["nameType"].capitalize()

        return data


class CreatorSchemaCSL(PersonOrOrgSchemaCSL):
    """Creator schema for v4."""


class FundingSchemaCSL(Schema):
    """Funding schema for v43."""

    funderName = fields.Str(attribute="funder.name")
    funderIdentifier = fields.Str(attribute="funder.identifier")
    funderIdentifierType = fields.Str(attribute="funder.scheme")
    awardTitle = fields.Str(attribute="award.title")
    awardNumber = fields.Str(attribute="award.number")
    # PIDS-FIXME: URI should be processed depending on the schema
    awardURI = fields.Str(attribute="award.identifier")

    @post_dump(pass_many=False)
    def uppercase(self, data, **kwargs):
        """Upper case the type."""
        if data.get("funderIdentifierType"):
            upper_type = data["funderIdentifierType"].upper()
            data["funderIdentifierType"] = upper_type

        return data


class CSLJSONSchema(Schema):
    """DataCite 4.3 Marshmallow Schema."""

    publisher = fields.Str(attribute='metadata.publisher')
    DOI = fields.Method('get_DOI')
    language = fields.Method('get_language')
    title = fields.Method('get_title')
    issued = fields.Method('get_issued')
    abstract = fields.Method('get_abstract')
    author = fields.List(
        fields.Nested(CreatorSchemaCSL), attribute='metadata.creators')
    note = fields.List(
        fields.Nested(FundingSchemaCSL), attribute='metadata.funding')
    version = SanitizedUnicode(attribute="metadata.version")
    # PIDS-FIXME: What about versioning links and related ids
    type = fields.Method('get_type')
    id = fields.Str(attribute='metadata.id')

    def get_DOI(self, obj):
        """Get DOI."""
        metadata = obj["metadata"]
        identifiers = metadata.get("identifiers", [])
        for id_ in identifiers:
            if id_["scheme"] == "DOI":
                return id_["identifier"]

    def get_language(self, obj):
        """Get language."""
        metadata = obj["metadata"]
        languages = metadata.get("languages")

        if languages:
            # PIDS-FIXME: How to choose? the first?
            return languages[0]["id"]

        return missing

    def get_title(self, obj):
        """Get title."""
        metadata = obj["metadata"]
        return metadata.get("title", missing)

    def get_issued(self, obj):
        """Get issued dates."""
        date_parts = []
        publication_date = obj["metadata"].get("publication_date", "")
        for splitedDate in publication_date.split("/"):
            date_parts.append(splitedDate.split("-"))

        return {"date-parts": date_parts}

    def get_abstract(self, obj):
        """Get abstract."""
        metadata = obj["metadata"]
        return metadata.get("description", missing)

    def get_type(self, obj):
        """Get resource type."""
        resource_type = obj["metadata"]["resource_type"]
        resource_type_record = self._read_resource_type(resource_type["id"])
        props = resource_type_record["props"]
        return props.get("datacite_general", "Other")


    def _read_resource_type(self, id_):
        """Retrieve resource type record using service."""
        return vocabulary_service.read(
            ('resource_types', id_),
            system_identity
        )._record
