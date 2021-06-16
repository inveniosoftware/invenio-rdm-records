# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite based Schema for Invenio RDM Records."""

from edtf import parse_edtf
from edtf.parser.grammar import ParseException
from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow import Schema, ValidationError, fields, missing, post_dump, \
    validate
from marshmallow_utils.fields import SanitizedUnicode

from ..utils import map_type


class PersonOrOrgSchema43(Schema):
    """Creator/contributor common schema for v4."""

    # PIDS-FIXME: need a more escalable solution for URIs
    URIS = {
        "orcid": "http://orcid.org/",
        "gnd": "http://d-nb.info/",  # PIDS-FIXME: is this correct?
        "ror": "https://ror.org/",
        "isni": "https://isni.org",
    }

    name = fields.Str(attribute="person_or_org.name")
    nameType = fields.Str(attribute="person_or_org.type")
    givenName = fields.Str(attribute="person_or_org.given_name")
    familyName = fields.Str(attribute="person_or_org.family_name")
    nameIdentifiers = fields.Method('get_name_identifiers')
    affiliations = fields.Method('get_affiliation')

    def get_name_identifiers(self, obj):
        """Get name identifier list."""
        serialized_identifiers = []
        identifiers = obj["person_or_org"].get("identifiers", [])

        for identifier in identifiers:
            scheme = identifier["scheme"]
            value = identifier["identifier"]
            uri = self.URIS.get(scheme)

            name_id = {
                "nameIdentifier": value,
                "nameIdentifierScheme": scheme.upper(),
            }

            if uri:
                name_id["nameIdentifier"] = uri + value
                name_id["schemeURI"] = uri

            serialized_identifiers.append(name_id)

        return serialized_identifiers

    def get_affiliation(self, obj):
        """Get affiliation list."""
        affiliations = obj.get("affiliations", [])

        if not affiliations:
            return missing

        serialized_affiliations = []
        ids = []

        for affiliation in affiliations:
            id_ = affiliation.get("id")
            if id_:
                ids.append(id_)
            else:
                # if no id, name is mandatory
                serialized_affiliations.append(
                    {"name": affiliation["name"]}
                )
        if ids:
            affiliations_service = (
                current_service_registry.get("rdm-affiliations")
            )
            affiliations = affiliations_service.read_many(system_identity, ids)

            for affiliation in affiliations:
                aff = {
                    "name": affiliation["name"],
                }
                identifier = affiliation.get("identifiers")
                if identifier:
                    # PIDS-FIXME: DataCite accepts only one, how to decide
                    identifier = identifier[0]
                    scheme = identifier["scheme"]
                    id_value = identifier["identifier"]
                    aff["affiliationIdentifier"] = id_value
                    aff["affiliationIdentifierScheme"] = scheme.upper()
                    uri = self.URIS.get(scheme)
                    if uri:
                        aff["affiliationIdentifier"] = uri + id_value

                serialized_affiliations.append(aff)

        return serialized_affiliations

    @post_dump(pass_many=False)
    def capitalize_name_type(self, data, **kwargs):
        """Capitalize type."""
        if data.get("nameType"):
            data["nameType"] = data["nameType"].capitalize()

        return data


class CreatorSchema43(PersonOrOrgSchema43):
    """Creator schema for v4."""


class ContributorSchema43(PersonOrOrgSchema43):
    """Contributor schema for v43."""

    contributorType = fields.Method('get_role')

    def get_role(self, obj):
        """Get datacite role."""
        role = obj.get("role")
        if not role:
            return missing

        props = map_type(
            'contributorsroles',
            ['props.datacite'],
            role["id"],
        )
        return props.get('datacite', '')


class SubjectSchema43(Schema):
    """Subjects schema for v43."""

    subject = fields.Str(attribute="subject")
    valueURI = fields.Str(attribute="identifier")
    subjectScheme = fields.Str(attribute="scheme")


class RightSchema43(Schema):
    """Rights schema for v43."""

    rights = fields.Str(attribute="title")
    rightsIdentifierScheme = fields.Str(attribute="scheme")
    rightsIdentifier = fields.Str(attribute="identifier")
    rightsUri = fields.Str(attribute="link")


class FundingSchema43(Schema):
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


class DataCite43Schema(Schema):
    """DataCite 4.3 Marshmallow Schema."""

    # PIDS-FIXME: What about versioning links and related ids
    types = fields.Method('get_type')
    titles = fields.Method('get_titles')
    creators = fields.List(
        fields.Nested(CreatorSchema43), attribute='metadata.creators')
    contributors = fields.List(
        fields.Nested(ContributorSchema43), attribute='metadata.contributors')
    publisher = fields.Str(attribute='metadata.publisher')
    publicationYear = fields.Method("get_publication_year")
    subjects = fields.Method("get_subjects")
    dates = fields.Method('get_dates')
    language = fields.Method('get_language')
    identifiers = fields.Method('get_identifiers')
    relatedIdentifiers = fields.Method('get_related_identifiers')
    sizes = fields.List(SanitizedUnicode(), attribute="metadata.sizes")
    formats = fields.List(SanitizedUnicode(), attribute="metadata.formats")
    version = SanitizedUnicode(attribute="metadata.version")
    rightsList = fields.List(
        fields.Nested(RightSchema43), attribute='metadata.rights')
    descriptions = fields.Method('get_descriptions')
    geoLocations = fields.Method("get_locations")
    fundingReferences = fields.List(
        fields.Nested(FundingSchema43), attribute='metadata.funding')
    schemaVersion = fields.Constant("http://datacite.org/schema/kernel-4")

    def get_type(self, obj):
        """Get resource type."""
        props = map_type(
            'resourcetypes',
            ['props.datacite_general', 'props.datacite_type'],
            obj["metadata"]["resource_type"]["id"],
        )
        return {
            'resourceTypeGeneral': props.get("datacite_general", "Other"),
            'resourceType': props.get("datacite_type", ""),
        }

    def _get_text(self, obj, field, default_type=None):
        """Get text list (for titles and descriptions)."""
        text = []
        main_value = obj["metadata"].get(field)

        if main_value:
            text = [{field: main_value}]
            if default_type:
                text[0][f"{field}Type"] = default_type

        additional_text = obj["metadata"].get(f"additional_{field}s", [])
        for t in additional_text:
            item = {field: t.get(field)}

            # Text type
            type_id = t.get("type", {}).get("id")
            if type_id:
                props = map_type(
                    f"{field}types",
                    ["props.datacite"],
                    type_id)
                if "datacite" in props:
                    item[f"{field}Type"] = props["datacite"]

            # Language
            lang_id = t.get("lang", {}).get("id")
            if lang_id:
                item["lang"] = lang_id

            text.append(item)

        return text or missing

    def get_titles(self, obj):
        """Get titles list."""
        return self._get_text(obj, "title")

    def get_descriptions(self, obj):
        """Get descriptions list."""
        return self._get_text(obj, "description", default_type="Abstract")

    def get_publication_year(self, obj):
        """Get publication year from edtf date."""
        try:
            publication_date = obj["metadata"]["publication_date"]
            parsed_date = parse_edtf(publication_date)
            return str(parsed_date.lower_strict().tm_year)
        except ParseException:
            # Should not fail since it was validated at service schema
            current_app.logger.error("Error parsing publication_date field for"
                                     f"record {obj['metadata']}")
            raise ValidationError(_("Invalid publication date value."))

    def get_dates(self, obj):
        """Get dates."""
        dates = [{
            "date": obj["metadata"]["publication_date"],
            "dateType": "Issued"
        }]

        for date in obj["metadata"].get("dates", []):
            date_type_id = date.get("type", {}).get("id")
            props = map_type('datetypes', ['props'], date_type_id)
            to_append = {
                "date": date["date"],
                "dateType": props.get("datacite", "Other")
            }
            desc = date.get("description")
            if desc:
                to_append["dateInformation"] = desc

            dates.append(to_append)

        return dates or missing

    def get_language(self, obj):
        """Get language."""
        languages = obj["metadata"].get("languages", [])
        if languages:
            # DataCite support only one language, so we take the first.
            return languages[0]["id"]

        return missing

    def get_identifiers(self, obj):
        """Get identifiers list."""
        # TODO: This has to be reviewed, as DataCite JSON is not the same
        # format as the datacite pypi package's JSON used for JSON -> XML
        # transformation.
        serialized_identifiers = []

        # Identifiers field
        metadata = obj["metadata"]
        identifiers = metadata.get("identifiers", [])
        for id_ in identifiers:
            serialized_identifiers.append({
                "identifier": id_["identifier"],
                "identifierType": id_["scheme"]
            })

        # PIDs field
        pids = obj["pids"]
        for scheme, id_ in pids.items():
            serialized_identifiers.append({
                "identifier": id_["identifier"],
                "identifierType": scheme.upper()
            })

        return serialized_identifiers or missing

    def get_related_identifiers(self, obj):
        """Get related identifiers."""
        # PIDS-FIXME: This might get much more complex depending on the id
        serialized_identifiers = []
        metadata = obj["metadata"]
        identifiers = metadata.get("related_identifiers", [])
        for rel_id in identifiers:
            relation_type_id = rel_id.get("relation_type", {}).get("id")
            props = map_type(
                "relationtypes",
                ["props"],
                relation_type_id
            )
            serialized_identifier = {
                "relatedIdentifierType": rel_id["scheme"].upper(),
                "relationType": props.get("datacite", ""),
                "relatedIdentifier": rel_id["identifier"],
            }

            resource_type_id = rel_id.get("resource_type", {}).get("id")
            if resource_type_id:
                props = map_type(
                    "resourcetypes",
                    ["props"],
                    resource_type_id
                )
                serialized_identifier["resourceTypeGeneral"] = props.get(
                    "datacite_general", "Other")

            serialized_identifiers.append(serialized_identifier)

        return serialized_identifiers or missing

    def get_locations(self, obj):
        """Get locations."""
        locations = []

        loc_list = obj["metadata"].get("locations", {}).get("features", [])
        for location in loc_list:
            place = location.get("place")
            serialized_location = {}
            if place:
                serialized_location["geoLocationPlace"] = place
            geometry = location.get("geometry")
            if geometry:
                geo_type = geometry["type"]
                # PIDS-FIXME: Scalable enough?
                # PIDS-FIXME: Implement Box and Polygon serialization
                if geo_type == "Point":
                    serialized_location["geoLocationPoint"] = {
                        "pointLatitude": geometry["coordinates"][0],
                        "pointLongitude": geometry["coordinates"][1],
                    }

            locations.append(serialized_location)
        return locations or missing

    def get_subjects(self, obj):
        """Get datacite subjects."""
        subjects = obj["metadata"].get("subjects", [])
        if not subjects:
            return missing

        serialized_subjects = []
        ids = []
        for subject in subjects:
            sub_text = subject.get("subject")
            if sub_text:
                serialized_subjects.append({"Subject": sub_text})
            else:
                ids.append(subject.get("id"))

        if ids:
            subjects_service = (
                current_service_registry.get("rdm-subjects")
            )
            subjects = subjects_service.read_many(system_identity, ids)
            validator = validate.URL()
            for subject in subjects:
                serialized_subj = {
                    "Subject": subject.get("subject"),
                    "subjectScheme": subject.get("scheme"),
                }
                id_ = subject.get("id")

                try:
                    validator(id_)
                    serialized_subj["valueURI"] = id_
                except ValidationError:
                    pass

                serialized_subjects.append(serialized_subj)

        return serialized_subjects if serialized_subjects else missing
