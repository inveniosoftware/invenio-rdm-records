# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021-2025 Northwestern University.
# Copyright (C) 2023 Graz University of Technology.
# Copyright (C) 2023 Caltech.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite based Schema for Invenio RDM Records."""

from babel_edtf import parse_edtf
from edtf.parser.grammar import ParseException
from flask import current_app
from flask_resources.serializers import BaseSerializerSchema
from invenio_access.permissions import system_identity
from invenio_base import invenio_url_for
from invenio_i18n import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, missing, post_dump, validate
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.html import strip_html
from pydash import py_

from ....proxies import current_rdm_records_service
from ...serializers.ui.schema import current_default_locale
from ..utils import get_preferred_identifier, get_vocabulary_props

RELATED_IDENTIFIER_SCHEMES = {
    "ark",
    "arxiv",
    "bibcode",
    "doi",
    "ean13",
    "eissn",
    "handle",
    "igsn",
    "isbn",
    "issn",
    "istc",
    "lissn",
    "lsid1",
    "pmid",
    "purl",
    "upc",
    "url",
    "urn",
    "w3id",
}
"""Allowed related identifier schemes for DataCite. Vocabulary taken from DataCite 4.3 schema definition."""


def get_scheme_datacite(scheme, config_name, default=None):
    """Returns the datacite equivalent of a scheme."""
    config_item = current_app.config[config_name]
    return config_item.get(scheme, {}).get("datacite", default)


class PersonOrOrgSchema43(Schema):
    """Creator/contributor common schema for v4."""

    name = fields.Str(attribute="person_or_org.name")
    nameType = fields.Method("get_name_type", attribute="person_or_org.type")
    givenName = fields.Str(attribute="person_or_org.given_name")
    familyName = fields.Str(attribute="person_or_org.family_name")
    nameIdentifiers = fields.Method("get_name_identifiers")
    affiliation = fields.Method("get_affiliation")

    def get_name_type(self, obj):
        """Get name type."""
        return obj["person_or_org"]["type"].title()

    def get_name_identifiers(self, obj):
        """Get name identifier list."""
        serialized_identifiers = []
        identifiers = obj["person_or_org"].get("identifiers", [])

        for identifier in identifiers:
            scheme = identifier["scheme"]
            id_scheme = get_scheme_datacite(
                scheme, "RDM_RECORDS_PERSONORG_SCHEMES", default=scheme
            )

            if id_scheme:
                name_id = {
                    "nameIdentifier": identifier["identifier"],
                    "nameIdentifierScheme": id_scheme,
                }
                serialized_identifiers.append(name_id)

        return serialized_identifiers

    def get_affiliation(self, obj):
        """Get affiliation list."""
        affiliations = obj.get("affiliations", [])

        if not affiliations:
            return missing

        serialized_affiliations = []

        for affiliation in affiliations:
            # name is mandatory with or without link to affiliation vocabulary
            aff = {"name": affiliation["name"]}
            id_ = affiliation.get("id")
            if id_:
                identifiers = affiliation.get("identifiers")
                if identifiers:
                    # FIXME: Make configurable
                    DATACITE_AFFILIATION_IDENTIFIER_TYPES_PREFERENCE = (
                        "ror",
                        "isni",
                        "gnd",
                    )
                    identifier = get_preferred_identifier(
                        DATACITE_AFFILIATION_IDENTIFIER_TYPES_PREFERENCE, identifiers
                    )
                    if not identifier:
                        identifier = identifiers[0]
                        identifier["scheme"] = "Other"

                    id_scheme = get_scheme_datacite(
                        identifier["scheme"],
                        "VOCABULARIES_AFFILIATION_SCHEMES",
                        default=identifier["scheme"].upper(),
                        # upper() is fine since this field is free text. It
                        # saves us from having to modify invenio-vocabularies
                        # or do config overrides.
                    )

                    if id_scheme == "ROR":
                        identifier_value = "https://ror.org/" + identifier["identifier"]
                    else:
                        identifier_value = identifier["identifier"]

                    if id_scheme:
                        aff["affiliationIdentifier"] = identifier_value
                        aff["affiliationIdentifierScheme"] = id_scheme
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

    contributorType = fields.Method("get_role")

    def get_role(self, obj):
        """Get datacite role."""
        role = obj.get("role")
        if not role:
            return missing

        props = get_vocabulary_props(
            "contributorsroles", ["props.datacite"], role["id"]
        )
        return props.get("datacite", "")


class SubjectSchema43(Schema):
    """Subjects schema for v43."""

    subject = fields.Str(attribute="subject")
    valueURI = fields.Str(attribute="identifier")
    subjectScheme = fields.Str(attribute="scheme")


class DataCite43Schema(BaseSerializerSchema):
    """DataCite JSON 4.3 Marshmallow Schema."""

    types = fields.Method("get_type")
    titles = fields.Method("get_titles")
    creators = fields.List(
        fields.Nested(CreatorSchema43), attribute="metadata.creators"
    )
    contributors = fields.List(
        fields.Nested(ContributorSchema43), attribute="metadata.contributors"
    )
    publisher = fields.Str(attribute="metadata.publisher")
    publicationYear = fields.Method("get_publication_year")
    subjects = fields.Method("get_subjects")
    dates = fields.Method("get_dates")
    language = fields.Method("get_language")
    identifiers = fields.Method("get_identifiers")
    relatedIdentifiers = fields.Method("get_related_identifiers")
    sizes = fields.List(SanitizedUnicode(), attribute="metadata.sizes")
    formats = fields.List(SanitizedUnicode(), attribute="metadata.formats")
    version = SanitizedUnicode(attribute="metadata.version")
    rightsList = fields.Method("get_rights")
    descriptions = fields.Method("get_descriptions")
    geoLocations = fields.Method("get_locations")
    fundingReferences = fields.Method("get_funding")
    schemaVersion = fields.Constant("http://datacite.org/schema/kernel-4")

    def get_type(self, obj):
        """Get resource type."""
        resource_type_id = py_.get(obj, "metadata.resource_type.id")
        if not resource_type_id:
            return missing

        props = get_vocabulary_props(
            "resourcetypes",
            ["props.datacite_general", "props.datacite_type"],
            resource_type_id,
        )
        return {
            "resourceTypeGeneral": props.get("datacite_general", "Other"),
            "resourceType": props.get("datacite_type", ""),
        }

    def _merge_main_and_additional(self, obj, field, default_type=None):
        """Return merged list of main + additional titles/descriptions."""
        result = []
        main_value = obj["metadata"].get(field)

        if main_value:
            item = {field: strip_html(main_value)}
            if default_type:
                item[f"{field}Type"] = default_type
            result.append(item)

        additional_values = obj["metadata"].get(f"additional_{field}s", [])
        for v in additional_values:
            item = {field: strip_html(v.get(field))}

            # Type
            type_id = v.get("type", {}).get("id")
            if type_id:
                props = get_vocabulary_props(
                    f"{field}types", ["props.datacite"], type_id
                )
                if "datacite" in props:
                    item[f"{field}Type"] = props["datacite"]

            # Language
            lang_id = v.get("lang", {}).get("id")
            if lang_id:
                item["lang"] = lang_id

            result.append(item)

        return result or missing

    def get_titles(self, obj):
        """Get titles list."""
        return self._merge_main_and_additional(obj, "title")

    def get_descriptions(self, obj):
        """Get descriptions list."""
        return self._merge_main_and_additional(
            obj, "description", default_type="Abstract"
        )

    def get_publication_year(self, obj):
        """Get publication year from edtf date."""
        publication_date = py_.get(obj, "metadata.publication_date")
        if not publication_date:
            return missing

        try:
            parsed_date = parse_edtf(publication_date)
            return str(parsed_date.lower_strict().tm_year)
        except ParseException:
            # Should not fail since it was validated at service schema
            current_app.logger.error(
                f"Error parsing publication_date field for record {obj['metadata']}"
            )
            raise ValidationError(_("Invalid publication date value."))

    def get_dates(self, obj):
        """Get dates."""
        pub_date = py_.get(obj, "metadata.publication_date")
        dates = [{"date": pub_date, "dateType": "Issued"}] if pub_date else []

        updated = False

        for date in obj["metadata"].get("dates", []):
            date_type_id = date.get("type", {}).get("id")
            if date_type_id == "updated":
                updated = True
            props = get_vocabulary_props("datetypes", ["props.datacite"], date_type_id)
            to_append = {
                "date": date["date"],
                "dateType": props.get("datacite", "Other"),
            }
            desc = date.get("description")
            if desc:
                to_append["dateInformation"] = desc

            dates.append(to_append)

        if not updated:
            try:
                updated_date = obj["updated"]
            except KeyError:
                pass
                # If no update date is present, do nothing. Happens with some tests, but should not in live repository
            else:
                to_append = {
                    "date": updated_date.split("T")[0],
                    "dateType": "Updated",
                }
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
        """Get (main and alternate) identifiers list."""
        # Add local URL
        serialized_identifiers = []
        links = obj.get("links")
        if links:
            serialized_identifiers.append(
                {
                    "identifier": obj["links"]["self_html"],
                    "identifierType": "URL",
                }
            )
        # pids go first so the DOI from the record is included
        pids = obj["pids"]
        for scheme, id_ in pids.items():
            id_scheme = get_scheme_datacite(
                scheme, "RDM_RECORDS_IDENTIFIERS_SCHEMES", default=scheme
            )

            if id_scheme:
                serialized_identifiers.append(
                    {"identifier": id_["identifier"], "identifierType": id_scheme}
                )

        # Identifiers field
        identifiers = obj["metadata"].get("identifiers", [])
        for id_ in identifiers:
            scheme = id_["scheme"]
            id_scheme = get_scheme_datacite(
                scheme, "RDM_RECORDS_IDENTIFIERS_SCHEMES", default=scheme
            )
            if id_scheme:
                # DataCite only accepts a DOI identifier that is the official
                # registered DOI - ones in the alternate identifier field are
                # dropped
                if id_scheme != "DOI":
                    serialized_identifiers.append(
                        {"identifier": id_["identifier"], "identifierType": id_scheme}
                    )

        return serialized_identifiers or missing

    def get_related_identifiers(self, obj):
        """Get related identifiers."""
        serialized_identifiers = []
        metadata = obj["metadata"]
        identifiers = metadata.get("related_identifiers", [])
        for rel_id in identifiers:
            relation_type_id = rel_id.get("relation_type", {}).get("id")
            props = get_vocabulary_props(
                "relationtypes", ["props.datacite"], relation_type_id
            )

            scheme = rel_id["scheme"]
            id_scheme = get_scheme_datacite(
                scheme, "RDM_RECORDS_IDENTIFIERS_SCHEMES", default=scheme
            )

            # Only serialize related identifiers with a valid scheme for DataCite.
            if id_scheme and id_scheme.lower() in RELATED_IDENTIFIER_SCHEMES:
                serialized_identifier = {
                    "relatedIdentifier": rel_id["identifier"],
                    "relationType": props.get("datacite", ""),
                    "relatedIdentifierType": id_scheme,
                }

                resource_type_id = rel_id.get("resource_type", {}).get("id")
                if resource_type_id:
                    props = get_vocabulary_props(
                        "resourcetypes",
                        # Cache is on both keys so query datacite_type as well
                        # even though it's not accessed.
                        ["props.datacite_general", "props.datacite_type"],
                        resource_type_id,
                    )
                    serialized_identifier["resourceTypeGeneral"] = props.get(
                        "datacite_general", "Other"
                    )

                serialized_identifiers.append(serialized_identifier)

        # Generate parent/child versioning relationships
        if self.context.get("is_parent"):
            # Fetch DOIs for all versions
            # NOTE: The refresh is safe to do here since we'll be in Celery task
            current_rdm_records_service.indexer.refresh()
            record_versions = current_rdm_records_service.scan_versions(
                system_identity,
                obj._child["id"],
                params={"_source_includes": "pids.doi"},
            )
            for version in record_versions:
                version_doi = version.get("pids", {}).get("doi")
                id_scheme = get_scheme_datacite(
                    "doi",
                    "RDM_RECORDS_IDENTIFIERS_SCHEMES",
                    default="DOI",
                )

                if version_doi:
                    serialized_identifiers.append(
                        {
                            "relatedIdentifier": version_doi["identifier"],
                            "relationType": "HasVersion",
                            "relatedIdentifierType": id_scheme,
                        }
                    )
        else:
            if hasattr(obj, "parent"):
                parent_record = obj.parent
            else:
                parent_record = obj.get("parent", {})
            parent_doi = parent_record.get("pids", {}).get("doi")

            if parent_doi:
                id_scheme = get_scheme_datacite(
                    "doi",
                    "RDM_RECORDS_IDENTIFIERS_SCHEMES",
                    default="doi",
                )
                if id_scheme.lower() in RELATED_IDENTIFIER_SCHEMES:
                    serialized_identifiers.append(
                        {
                            "relatedIdentifier": parent_doi["identifier"],
                            "relationType": "IsVersionOf",
                            "relatedIdentifierType": id_scheme,
                        }
                    )

        # adding communities
        communities = obj.get("parent", {}).get("communities", {}).get("entries", [])
        for community in communities:
            slug = community.get("slug")
            url = invenio_url_for(
                "invenio_app_rdm_communities.communities_home", pid_value=slug
            )
            serialized_identifiers.append(
                {
                    "relatedIdentifier": url,
                    "relationType": "IsPartOf",
                    "relatedIdentifierType": "URL",
                }
            )
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
                if geo_type == "Point":
                    serialized_location["geoLocationPoint"] = {
                        "pointLongitude": str(geometry["coordinates"][0]),
                        "pointLatitude": str(geometry["coordinates"][1]),
                    }
                elif geo_type == "Polygon":
                    # geojson has a layer of nesting before actual coordinates
                    coords = geometry["coordinates"][0]
                    # First we see if we have a box
                    box = False
                    if len(coords) in [4, 5]:
                        # A box polygon may wrap around with 5 coordinates
                        x_coords = set()
                        y_coords = set()
                        for coord in coords:
                            x_coords.add(coord[0])
                            y_coords.add(coord[1])
                        if len(x_coords) == 2 and len(y_coords) == 2:
                            x_coords = sorted(x_coords)
                            y_coords = sorted(y_coords)
                            serialized_location["geoLocationBox"] = {
                                "westBoundLongitude": str(x_coords[0]),
                                "eastBoundLongitude": str(x_coords[1]),
                                "southBoundLatitude": str(y_coords[0]),
                                "northBoundLatitude": str(y_coords[1]),
                            }
                            box = True
                    if not box:
                        polygon = []
                        for coord in coords:
                            polygon.append(
                                {
                                    "polygonPoint": {
                                        "pointLongitude": str(coord[0]),
                                        "pointLatitude": str(coord[1]),
                                    }
                                }
                            )
                        serialized_location["geoLocationPolygon"] = polygon

            locations.append(serialized_location)
        return locations or missing

    def get_subjects(self, obj):
        """Get datacite subjects."""
        subjects = obj["metadata"].get("subjects", [])
        if not subjects:
            return missing

        validator = validate.URL()
        serialized_subjects = []

        for subject in subjects:
            entry = {"subject": subject.get("subject")}

            id_ = subject.get("id")
            if id_:
                entry["subjectScheme"] = subject.get("scheme")
                try:
                    validator(id_)
                    entry["valueURI"] = id_
                except ValidationError:
                    pass

            serialized_subjects.append(entry)

        return serialized_subjects if serialized_subjects else missing

    def get_rights(self, obj):
        """Get datacite rigths."""
        rights = obj["metadata"].get("rights", [])
        copyright = obj["metadata"].get("copyright", None)
        if not rights and not copyright:
            return missing

        serialized_rights = []
        for right in rights:
            entry = {"rights": right.get("title", {}).get(current_default_locale())}

            id_ = right.get("id")
            if id_:
                entry["rightsIdentifier"] = right.get("id")
                entry["rightsIdentifierScheme"] = right.get("props", {}).get("scheme")

            # Get url from props (vocabulary) or link (custom license)
            link = right.get("props", {}).get("url") or right.get("link", {})
            if link:
                entry["rightsUri"] = link
            serialized_rights.append(entry)
        if copyright:
            serialized_rights.append(
                {
                    "rights": copyright,
                    "rightsUri": "http://rightsstatements.org/vocab/InC/1.0/",
                }
            )

        return serialized_rights if serialized_rights else missing

    def get_funding(self, obj):
        """Get funding references."""
        # constants
        FUNDER_ID_TYPES_PREF = current_app.config.get(
            "RDM_DATACITE_FUNDER_IDENTIFIERS_PRIORITY",
            (
                "ror",
                "doi",
                "grid",
                "isni",
                "gnd",
            ),
        )
        DATACITE_AWARD_IDENTIFIER_TYPES_PREFERENCE = ("doi", "url")
        TO_FUNDER_IDENTIFIER_TYPES = {
            "isni": "ISNI",
            "gnd": "GND",
            "grid": "GRID",
            "ror": "ROR",
            "doi": "Crossref Funder ID",  # from FundRef
        }
        funding_references = []
        funding_list = obj["metadata"].get("funding", [])
        for funding in funding_list:
            # funder, if there is an item in the list  it must have a funder
            funding_ref = {}
            funder = funding.get("funder", {})
            funding_ref["funderName"] = funder["name"]
            identifiers = funder.get("identifiers", [])
            if identifiers:
                identifier = get_preferred_identifier(FUNDER_ID_TYPES_PREF, identifiers)
                if not identifier:
                    identifier = identifiers[0]
                    identifier["scheme"] = "Other"

                id_type = TO_FUNDER_IDENTIFIER_TYPES.get(identifier["scheme"], "Other")

                funding_ref["funderIdentifier"] = identifier["identifier"]
                funding_ref["funderIdentifierType"] = id_type

            # award
            award = funding.get("award")
            if award:  # having an award is optional
                award_title = award.get("title", {}).get("en")
                if award_title:
                    funding_ref["awardTitle"] = award_title
                award_number = award.get("number")
                if award_number:
                    funding_ref["awardNumber"] = award_number

                identifiers = award.get("identifiers", [])
                if identifiers:
                    identifier = get_preferred_identifier(
                        DATACITE_AWARD_IDENTIFIER_TYPES_PREFERENCE, identifiers
                    )
                    if identifier:
                        funding_ref["awardURI"] = identifier["identifier"]

            funding_references.append(funding_ref)
        return funding_references or missing
