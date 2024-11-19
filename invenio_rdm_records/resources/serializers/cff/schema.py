# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""CFF schema."""

from flask_resources.serializers import BaseSerializerSchema
from marshmallow import ValidationError, fields, missing
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode


def _serialize_person(person):
    """Serializes one person."""
    fam_name = person["person_or_org"].get("family_name")
    giv_name = person["person_or_org"].get("given_name")

    serialized = {}

    if fam_name:
        serialized.update({"family-names": fam_name})
    if giv_name:
        serialized.update({"given-names": giv_name})

    if not serialized:
        return ValidationError("One of 'family-names' or 'given-names' is required.")

    identifiers = person["person_or_org"].get("identifiers", [])
    affiliations = person.get("affiliations", [])

    for _id in identifiers:
        if _id["scheme"] == "orcid":
            serialized.update({"orcid": _id["identifier"]})
            break

    for _affiliation in affiliations:
        # CFF only supports one affiliation for a person. We serialize the first one only.
        serialized.update(
            # Serialize the name, if given, defaults to the affiliation ID (one of both is mandatory)
            {"affiliation": _affiliation.get("name", _affiliation.get("id"))}
        )
        break
    return serialized


def _serialize_org(org):
    """Serializes a CFF entity (organization in RDM)."""
    name = org["person_or_org"]["name"]
    identifiers = org["person_or_org"].get("identifiers", [])
    serialized = {"name": name}
    for _id in identifiers:
        if _id["scheme"] == "orcid":
            serialized.update({"orcid": _id["identifier"]})
            break
    return serialized


class CFFSchema(BaseSerializerSchema):
    """CFF Schema.

    .. note::

        The schema is defined in:
            https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md

    :raises ValidationError: when the resource type is not allowed.
    """

    allowed_types = {"software", "dataset"}

    # Legacy Zenodo is incomplete, it's a deserializer (transforms CITATION.cff to zenodo upload).
    type = fields.Method("get_type")
    abstract = SanitizedHTML(attribute="metadata.description")
    authors = fields.Method("get_authors")
    cff_version = fields.Constant("1.2.0", data_key="cff-version")
    contact = fields.Method("get_contact")
    date_released = fields.Method("get_date_released", data_key="date-released")
    doi = fields.Method("get_doi")
    identifiers = fields.Method("get_identifiers")
    keywords = fields.Method("get_keywords")
    license = fields.Method("get_license")
    license_url = fields.Method("get_license_url", data_key="license-url")
    # TODO references - related identifiers?
    # TODO there are other derivations of repository
    repository_code = fields.Method("get_repository_code", data_key="repository-code")
    title = SanitizedUnicode(attribute="metadata.title")
    version = SanitizedHTML(attribute="metadata.version")

    def get_authors(self, obj):
        """Get authors."""
        metadata = obj.get("metadata", {})

        result = []

        creators = metadata.get("creators", [])
        contributors = metadata.get("contributors", [])

        for creator in creators + contributors:
            if creator["person_or_org"]["type"] == "personal":
                s_author = _serialize_person(creator)
            else:
                s_author = _serialize_org(creator)
            result.append(s_author)

        return result

    def get_contact(self, obj):
        """Serializes contact person, if any."""
        metadata = obj.get("metadata", {})

        result = {}

        authors = metadata.get("authors", [])

        for author in authors:
            role = author.get("role")
            if role and role["id"] == "contactperson":
                if author["person_or_org"]["type"] == "personal":
                    result = _serialize_person(author)
                else:
                    result = _serialize_org(author)
                break

        return result or missing

    def get_date_released(self, obj):
        """Serialize release date."""
        pub_date = obj.get("metadata", {}).get("publication_date")
        # YYYY-MM-DD
        return pub_date or missing

    def get_doi(self, obj):
        """Serialize DOI."""
        doi = obj.get("pids", {}).get("doi", {}).get("identifier")
        return doi or missing

    def get_identifiers(self, obj):
        """Serialize identifiers.

        Each CFF accepts identifiers of the following types:
            - DOI
            - URL
            - SWH
            - Other
        """
        alternate_identifiers = obj.get("metadata", {}).get("identifiers", [])

        allowed_types = ["doi", "url", "swh"]

        result = []
        for _identifier in alternate_identifiers:
            serialized = {}
            scheme = _identifier["scheme"]
            value = _identifier["identifier"]
            _type = scheme if scheme in allowed_types else "other"
            serialized.update({"type": _type, "value": value})
            result.append(serialized)

        return result or missing

    def get_keywords(self, obj):
        """Serialize keywords."""
        subjects = obj.get("metadata", {}).get("subjects", [])

        result = []
        for _subject in subjects:
            subject_id = _subject.get("id")
            custom_subject = _subject.get("subject")
            if subject_id:
                result.append(subject_id)
            if custom_subject:
                result.append(custom_subject)
        return result or missing

    def get_license(self, obj):
        """Serialize license.

        CFF defines a license as it's  SPDX identifier, just like RDM.
        """
        rights = obj.get("metadata", {}).get("rights", [])
        result = []
        for right in rights:
            # Only serialize licenses that have an ``id```. IDs in RDM match SPDX ids.
            _id = right.get("id")
            if _id:
                result.append(_id)
        return result

    def get_license_url(self, obj):
        """Serialize non-standard licenses url.

        CFF only allows one non-standard license to be serialized.
        A non-standard license, as definded by CFF, is a license without a valid SPDX id.
        We serialize a non-standard license url if the license does not have an `id` AND has a `link`.
        """
        rights = obj.get("metadata", {}).get("rights", [])
        result = None
        for right in rights:
            # Only serialize licenses that have an ``id```. IDs in RDM match SPDX ids.
            _id = right.get("id")
            link = right.get("link")
            if not _id and link:
                result = link
                break
        return result or missing

    def get_repository_code(self, obj):
        """Serialize repository code.

        As defined by CFF, a repository is represented by its URL.
        The URL of the work in a source code repository.
        """
        resource_type = obj.get("metadata", {}).get("resource_type", {}).get("id")

        if resource_type != "software":
            return missing

        identifiers = obj.get("metadata", {}).get("related_identifiers", [])
        result = None
        for _identifier in identifiers:
            scheme = _identifier["scheme"]
            value = _identifier["identifier"]
            rt = _identifier.get("resource_type", {}).get("id")
            relation_type = _identifier.get("relation_type", {}).get("id")
            is_sw_supplement = rt == "software" and relation_type == "issupplementto"
            if scheme == "url" and is_sw_supplement:
                result = value
                break
        return result or missing

    def get_type(self, obj):
        """Serialize record type.

        Only software and dataset are allowed in CFF.
        """
        resource_type = obj.get("metadata", {}).get("resource_type", {}).get("id")
        if resource_type not in self.allowed_types:
            return missing

        return resource_type
