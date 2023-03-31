# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community records schema."""

from invenio_i18n import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, validate, validates


class RecordSchema(Schema):
    """Schema to define a community id."""

    id = fields.String()


class CommunityRecordsSchema(Schema):
    """Record's communities schema."""

    records = fields.List(
        fields.Nested(RecordSchema), validate=validate.Length(min=1), required=True
    )

    @validates("records")
    def validate_records(self, value):
        """Validate communities."""
        max_number = self.context["max_number"]
        if max_number < len(value):
            raise ValidationError(
                _(
                    "Too many records passed, {max_number} max allowed.".format(
                        max_number=max_number
                    )
                )
            )

        # check unique ids
        uniques = set()
        duplicated = set()
        for record in value:
            rec_id = record["id"]
            if rec_id in uniques:
                duplicated.add(rec_id)
            uniques.add(rec_id)

        if duplicated:
            raise ValidationError(
                _("Duplicated records {rec_ids}.".format(rec_ids=duplicated))
            )
