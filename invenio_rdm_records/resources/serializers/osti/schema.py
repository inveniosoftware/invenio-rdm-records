# MSD-LIVE change: custom OSTI serializer used to convert 
# the json format of an RDM record to the OSTI json schema

# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 PNNL.
# Copyright (C) 2022 BNL.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OSTI based Schema for Invenio RDM Records."""

from edtf import parse_edtf, struct_time_to_date
from edtf.parser.grammar import ParseException
from flask import current_app
from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, missing
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.html import strip_html
from invenio_records_resources.proxies import current_service_registry
from invenio_access.permissions import system_identity


class AuthorSchema(Schema):
    # OSTI requires last_name so if an org is an author use that as the lastname

    # person_or_org.name is the name entered if Organization is chosen 
    # as an author, but OSTI requires a first and last name. So if we 
    # don't have first and last name, use the org's full name as both
    # if fields.Str(attribute="person_or_org.family_name") is not None:
    #     last_name = fields.Str(attribute="person_or_org.family_name")
    # else:
    #     last_name = fields.Str(attribute="person_or_org.name")
    #
    # first_name = fields.Str(attribute="person_or_org.given_name")

    last_name = fields.Method('get_last_name')
    first_name = fields.Method('get_first_name')
    # optionally is affiliation_name, private_email 
    # (N/A as RDM doesn't even ask for it?), orcid_id
    orcid_id = fields.Method('get_orcid')
    affiliation_name = fields.Method('get_affiliation')

    def get_first_name(self, obj):
        given_name = obj["person_or_org"].get("given_name")
        if given_name is not None:
            return given_name

        return missing

    def get_last_name(self, obj):
        fam_name = obj["person_or_org"].get("family_name")
        name = obj["person_or_org"].get("name")
        if fam_name is not None:
            return fam_name
        elif name is not None:
            return name

        return missing

    def get_orcid(self, obj):
        identifiers = obj["person_or_org"].get("identifiers", [])
        for identifier in identifiers:
            scheme = identifier["scheme"]
            if scheme == 'orcid':
                return identifier["identifier"]

        return missing

    def get_affiliation(self, obj):
        """Get affiliation list."""
        affiliations = obj.get("affiliations", [])

        if not affiliations:
            return missing

        # OSTI only supports 1 affiliation for an author 
        # so just return the first one
        affiliation = affiliations[0]
        id_ = affiliation.get("id")
        if id_:
            affiliations_service = current_service_registry.get("affiliations")
            full_affiliation = affiliations_service.read(system_identity, id_, True)
            return full_affiliation.data["name"]
        else:
            return affiliation["name"]


class OSTISchema(Schema):
    """OSTI Marshmallow Schema."""

    dataset_type = fields.Method('get_type')
    title = SanitizedUnicode(attribute="metadata.title")
    # site_url = SanitizedUnicode(attribute="links.self_html")
    publication_date = fields.Method("get_publication_date")
    authors = fields.List(
        fields.Nested(AuthorSchema), attribute='metadata.creators')
    keywords = fields.Method("get_subjects")
    # other_identifying_numbers = fields.Method('get_related_identifiers')
    description = fields.Method('get_descriptions')

    def get_type(self, obj):
        """Get resource type."""
        if not obj["metadata"]["resource_type"]:
            return missing
        rdm_type = obj["metadata"]["resource_type"]["id"]
        # default to the OSTI type of Specialized Mix
        osti_type = 'SM'
        if rdm_type == 'dataset-modeloutput':
            osti_type = 'AS' # Animations/Simulations
        elif rdm_type == 'dataset-observation':
            osti_type = 'I' # Instrument

        return osti_type

    def _merge_main_and_additional(self, obj, field):
        """Return merged list of main + additional titles/descriptions."""
        result = ''
        main_value = obj["metadata"].get(field)

        if main_value:
            item = strip_html(main_value)
            result += item + " "

        additional_values = obj["metadata"].get(f"additional_{field}s", [])
        for v in additional_values:
            item = strip_html(v.get(field))
            result += item + " "

        return result or missing


    def get_descriptions(self, obj):
        """Get descriptions list."""
        descriptions = self._merge_main_and_additional(
            obj, "description"
        )
        return descriptions

    def get_publication_date(self, obj):
        """Get publication year from edtf date."""
        try:
            if not obj["metadata"]["publication_date"]:
                return missing
            publication_date = obj["metadata"]["publication_date"]
            parsed_date = parse_edtf(publication_date)
            real_date = struct_time_to_date(parsed_date.lower_strict())
            return str(real_date.strftime("%m/%d/%Y"))
        except ParseException:
            # Should not fail since it was validated at service schema
            current_app.logger.error("Error parsing publication_date field for"
                                     f"record {obj['metadata']}")
            raise ValidationError(_("Invalid publication date value."))

    def get_related_identifiers(self, obj):
        """Get related identifiers."""
        metadata = obj["metadata"]
        identifiers = metadata.get("related_identifiers", [])
        if not identifiers:
            return missing

        serialized_identifiers = ''
        for rel_id in identifiers:
            serialized_identifiers = rel_id.get("identifier", "")
            serialized_identifiers += ";"

        return serialized_identifiers or missing

    def get_subjects(self, obj):
        """Get osti keywords."""
        subjects = obj["metadata"].get("subjects", [])
        if not subjects:
            return missing

        serialized_subjects = ''
        for subject in subjects:
            sub_text = subject.get("subject")
            if sub_text:
                serialized_subjects += sub_text
                serialized_subjects += ";"

        return serialized_subjects if serialized_subjects else missing

