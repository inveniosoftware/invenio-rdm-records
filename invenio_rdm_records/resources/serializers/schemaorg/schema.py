# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Schemaorg based Schema for Invenio RDM Records."""
from typing import Optional

import pycountry
from commonmeta import dict_to_spdx, doi_as_url, parse_attributes, unwrap, wrap
from edtf import parse_edtf
from edtf.parser.grammar import ParseException
from flask_resources.serializers import BaseSerializerSchema
from idutils import to_url
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from marshmallow import Schema, ValidationError, fields, missing
from marshmallow_utils.fields import SanitizedUnicode
from pydash import py_

from ..schemas import CommonFieldsMixin
from ..utils import convert_size, get_vocabulary_props


class PersonOrOrgSchema(Schema):
    """Creator/contributor schema for Schemaorg."""

    name = fields.Str(attribute="person_or_org.name")
    givenName = fields.Str(attribute="person_or_org.given_name")
    familyName = fields.Str(attribute="person_or_org.family_name")
    affiliation = fields.Method("get_affiliation")
    id_ = fields.Method("get_name_identifier", data_key="@id")
    type_ = fields.Method("get_name_type", data_key="@type")

    #
    # Private helper functions
    #

    def _serialize_identifier(self, identifier):
        """Format on name identifier."""
        if not identifier.get("identifier"):
            return None

        if identifier.get("scheme") == "isni":
            return "http://isni.org/isni/" + identifier.get("identifier")

        # Schemaorg expects a URL for the identifier
        return to_url(identifier["identifier"], identifier["scheme"], "https")

    #
    # Schema Methods
    #

    def get_name_type(self, obj):
        """Get name type. Schemaorg expects either Person or Organisation.

        Defaults to Person.
        """
        name_type = py_.get(obj, "person_or_org.type")
        return "Organization" if name_type == "organizational" else "Person"

    def get_name_identifier(self, obj):
        """Get name identifier.

        Schemaorg expects a URL for the identifier, and does not support multiple identifiers. Use the first identifier found.
        """
        return (
            next(
                (
                    self._serialize_identifier(i)
                    for i in wrap(obj["person_or_org"].get("identifiers", []))
                ),
                None,
            )
            or missing
        )

    def get_affiliation(self, obj):
        """Get affiliation list."""

        def format_affiliation(affiliation):
            """Format on affiliation."""
            name = affiliation.get("name")
            id_ = affiliation.get("id")
            if not (name or id_):
                raise ValidationError(
                    "Affiliation failed to serialize: one of 'id' or 'name' must be provided."
                )

            serialized_affiliation = {"@type": "Organization"}

            if name:
                serialized_affiliation.update({"name": name})

            # Affiliation comes from a controlled vocabulary
            if id_:
                affiliations_service = current_service_registry.get("affiliations")
                affiliation_vc = affiliations_service.read(
                    system_identity, id_
                ).to_dict()

                # Prioritize the vocabulary name instead of the custom one
                if affiliation_vc.get("name"):
                    serialized_affiliation.update({"name": affiliation_vc["name"]})

                # Retrieve the first identifier
                identifier = next(
                    (
                        idf
                        for idf in affiliation_vc.get("identifiers", [])
                        if (idf.get("identifier") and idf.get("scheme"))
                    ),
                    None,
                )
                if identifier:
                    serialized_affiliation.update(
                        {"@id": self._serialize_identifier(identifier)}
                    )

            return serialized_affiliation

        affiliations = obj.get("affiliations", [])
        return [format_affiliation(a) for a in affiliations] or missing


class SchemaorgSchema(BaseSerializerSchema, CommonFieldsMixin):
    """Schemaorg Marshmallow Schema."""

    context = fields.Constant("http://schema.org", data_key="@context")
    id_ = fields.Method("get_id", data_key="@id")
    type_ = fields.Method("get_type", data_key="@type")
    identifier = fields.Method("get_identifiers")
    name = SanitizedUnicode(attribute="metadata.title")
    author = fields.List(
        fields.Nested(PersonOrOrgSchema), attribute="metadata.creators"
    )
    editor = fields.List(
        fields.Nested(PersonOrOrgSchema), attribute="metadata.contributors"
    )
    publisher = fields.Method("get_publisher")
    keywords = fields.Method("get_keywords")
    datePublished = fields.Method("get_publication_date")
    dateModified = fields.Method("get_modification_date")
    inLanguage = fields.Method("get_language")
    contentSize = fields.Method("get_size")
    encodingFormat = fields.Method("get_format")
    version = SanitizedUnicode(attribute="metadata.version")
    license = fields.Method("get_license")
    description = SanitizedUnicode(attribute="metadata.description")
    # spatialCoverage = fields.Method("get_spatial_coverage")
    funding = fields.Method("get_funding")

    def get_id(self, obj):
        """Get id. Use the DOI expressed as a URL."""
        doi = py_.get(obj, "pids.doi.identifier")
        if doi:
            return doi_as_url(doi)
        return missing

    def get_type(self, obj):
        """Get type. Use the vocabulary service to get the schema.org type."""
        props = get_vocabulary_props(
            "resourcetypes",
            ["props.schema.org"],
            py_.get(obj, "metadata.resource_type.id"),
        )
        return props.get("schema.org", "CreativeWork")

    def get_size(self, obj):
        """Get size."""
        ret = None
        size = py_.get(obj, "files.total_bytes")
        if size:
            ret = convert_size(size)
        return ret or missing

    def get_format(self, obj):
        """Get format."""
        formats = py_.get(obj, "metadata.formats")
        return unwrap(wrap(formats)) or missing

    def get_publication_date(self, obj):
        """Get publication date."""
        try:
            parsed_date = parse_edtf(py_.get(obj, "metadata.publication_date"))
        except ParseException:
            return missing

        # if date is an interval, use the start date
        if (type(parsed_date).__name__) == "Interval":
            parsed_date = parsed_date.lower
        return str(parsed_date)

    def get_modification_date(self, obj):
        """Get modification date."""
        last_updated = obj.get("updated")
        return last_updated or missing

    def get_language(self, obj):
        """Get language. Schemaorg expects either a string or language dict.

        For consistency with Zenodo, use the dict, and use the ISO 639-3 code
        for the alternateName (e.g. dan) and the language string (e.g. Danish)
        for the name. Use only the first of multiple languages provided.
        """
        language = parse_attributes(
            py_.get(obj, "metadata.languages"), content="id", first=True
        )
        if not language:
            return missing
        language_obj = pycountry.languages.get(alpha_3=language)
        if not language_obj:
            return missing
        return {
            "alternateName": language_obj.alpha_3,
            "@type": "Language",
            "name": language_obj.name,
        }

    def get_identifiers(self, obj):
        """Get (main and alternate) identifiers list."""
        doi = py_.get(obj, "pids.doi.identifier")
        if doi:
            return doi_as_url(doi)
        self_url = py_.get(obj, "links.self")
        return self_url or missing

    def get_spatial_coverage(self, obj):
        """Get spatial_coverage."""
        return missing
        # TODO: implement

    def get_publisher(self, obj):
        """Get publisher."""
        publisher = py_.get(obj, "metadata.publisher")
        if publisher:
            return {"@type": "Organization", "name": publisher}

        return missing

    def get_keywords(self, obj):
        """Get keywords.

        Schema.org expects a comma-separated string, not a list as in the Zenodo implementation.
        """
        subjects = py_.get(obj, "metadata.subjects")
        if not subjects:
            return missing
        subjects = [
            s["subject"] for s in wrap(subjects) if s.get("subject", None) is not None
        ]
        return ", ".join(subjects)

    def get_license(self, obj):
        """Get license.

        Find first license id or link in metadata.rights, then find matching SPDX metadata. Schemaorg expects a URL.
        """
        license_ = next(
            (i for i in wrap(py_.get(obj, "metadata.rights")) if i.get("id", None)),
            None,
        ) or next(
            (i for i in wrap(py_.get(obj, "metadata.rights")) if i.get("link", None)),
            None,
        )
        if license_ and license_.get("id", None):
            spdx = dict_to_spdx({"id": license_.get("id")})
        elif license_ and license_.get("link", None):
            spdx = dict_to_spdx({"url": license_.get("link", None)}) or license_
        else:
            spdx = None
        return spdx.get("url", None) if spdx else missing

    def get_funding(self, obj):
        """Serialize funding to schema.org.

        .. note::

            Property 'funding': https://schema.org/funding
            Type 'Grant': https://schema.org/Grant
        """

        def _serialize_funder(funder):
            """Serializes a funder to schema.org."""
            serialized_funder = {"@type": "Organization"}
            if funder.get("id"):
                serialized_funder.update({"@id": funder["id"]})
            if funder.get("name"):
                serialized_funder.update({"name": funder["name"]})
            return serialized_funder

        def _serialize_award(award):
            """Serializes an award (or grant) to schema.org."""
            title = py_.get(award, "title.en")
            number = award.get("number")
            id_ = award.get("id")

            if not (id_ or (title and number)):
                # One of 'id' or '(title' and 'number') must be provided
                raise ValidationError(
                    "Funding serialization failed on award: one of 'id' or ('number' and 'title') are required."
                )

            serialized_award = {}
            if title or number:
                # Serializes to:
                # title (number) OR title OR number
                fallback = title or number
                serialized_award.update(
                    {"name": f"{title} ({number})" if title and number else fallback}
                )
            if id_:
                serialized_award.update({"identifier": id_})

            url = next(
                (i for i in award.get("identifiers", []) if i.get("scheme") == "url"),
                None,
            )
            if url:
                serialized_award.update({"url": url})
            return serialized_award

        result = []

        funding = py_.get(obj, "metadata.funding", [])
        for fund in funding:
            serialized_funding = {}
            # Serialize funder
            funder = fund.get("funder")
            if funder:
                serialized_funding.update({"funder": _serialize_funder(funder)})

            # Serialize award (or grant)
            award = fund.get("award")
            if award:
                serialized_funding.update(**_serialize_award(award))
            result.append(serialized_funding)

        return result or missing
