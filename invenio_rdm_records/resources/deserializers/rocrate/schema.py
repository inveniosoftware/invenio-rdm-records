# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RO-Crate schema."""

from distutils.log import error

from flask_babelex import lazy_gettext as _
from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load, validate
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode


def _list_value(lst):
    """Return the first value from single-value lists."""
    if isinstance(lst, list) and len(lst) == 1:
        return lst[0]
    return lst


class ROCrateSchema(Schema):
    """Schema for the loading RO-Crate into record metadata."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    error_messages = {
        "required": _("Missing data for required field."),
    }

    LIST_VALUE_FIELDS = [
        "license",
        "description",
        "datePublished",
    ]

    @pre_load
    def list_to_value(self, data, **kwargs):
        """Extract top-level single-item list field values."""
        for field in self.LIST_VALUE_FIELDS:
            if field in data:
                data[field] = _list_value(data[field])
        return data

    resource_type = fields.Constant({"id": "dataset"})
    title = SanitizedUnicode(data_key="name", required=True)
    description = SanitizedHTML()
    publication_date = fields.Method(
        deserialize="load_publication_date",
        data_key="datePublished",
        required=True,
    )

    def load_publication_date(self, value):
        """Load publication date."""
        if value:
            return value[:10]

    creators = fields.Method(
        deserialize="load_creators",
        required=True,
        data_key="author",
        validate=validate.Length(min=1),
    )

    def load_creators(self, value):
        """Load creators."""
        errors = {}
        creators = []
        for c_idx, obj in enumerate(value):
            person_or_org = {}
            affiliations = []

            if obj.get("@type") == "Person":
                person_or_org["type"] = "personal"
                family_name = _list_value(obj.get("familyName"))
                if not family_name:
                    errors[f"{c_idx}.familyName"] = self.error_messages["required"]
                person_or_org["family_name"] = family_name
                given_name = _list_value(obj.get("givenName"))
                if not given_name:
                    errors[f"{c_idx}.givenName"] = self.error_messages["required"]
                person_or_org["given_name"] = given_name
                if obj.get("affiliation"):
                    for a_idx, a in enumerate(obj.get("affiliation")):
                        if not a.get("name"):
                            errors[
                                f"{c_idx}.affiliation.{a_idx}.name"
                            ] = self.error_messages["required"]
                        affiliations.append({"name": a.get("name")})
            elif obj.get("@type") == "Organization":
                person_or_org["type"] = "organizational"
                if not obj.get("name"):
                    errors[f"{c_idx}.name"] = self.error_messages["required"]
                person_or_org["name"] = obj.get("name")
            else:
                errors[f"{c_idx}.@type"] = _(
                    "'@type' must be 'Person' or 'Organization'"
                )

            creators.append(
                {
                    "person_or_org": person_or_org,
                    "affiliations": affiliations,
                }
            )

        if errors:
            raise ValidationError(errors)
        return creators

    rights = fields.Method(deserialize="load_rights", data_key="license", required=True)

    def load_rights(self, value):
        """Load rights."""
        if value:
            ret = {}
            if value.get("name"):
                ret["title"] = {"en": value["name"]}
            else:
                raise ValidationError({"name": self.error_messages["required"]})
            if value.get("description"):
                ret["description"] = {"en": _list_value(value["description"])}

            return [ret]

    subjects = fields.Method(deserialize="load_subjects", data_key="keywords")

    def load_subjects(self, value):
        """Load subjects."""
        if value and isinstance(value, list):
            return [{"subject": s} for s in value]
        else:
            raise ValidationError(_("Format must be a list of strings."))
