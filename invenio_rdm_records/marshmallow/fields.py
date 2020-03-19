# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom provided fields."""
from datetime import date

from edtf.parser.grammar import ParseException, level0Expression
from flask_babelex import lazy_gettext as _
from marshmallow import fields


class EDTFLevel0DateString(fields.Str):
    """
    Extended Date(/Time) Format Level 0 date string field.

    Made a field for stronger semantics than just a validator.
    """

    default_error_messages = {
        "invalid": _("Please provide a valid date or interval.")
    }

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize an EDTF Level 0 formatted date string.

        load()-equivalent operation.

        NOTE: Level 0 allows for an interval.
        NOTE: ``level0Expression`` tries hard to parse dates. For example,
              ``"2020-01-02garbage"`` will parse to the 2020-01-02 date.
        NOTE: uses today's date if falsey value given
        """
        if not value:
            today_str = date.today().isoformat()
            return (
                super(EDTFLevel0DateString, self)
                ._deserialize(today_str, attr, data, **kwargs)
            )

        parser = level0Expression("level0")

        try:
            result = parser.parseString(value)

            if not result:
                raise ParseException()

            # check it is chronological if interval
            # NOTE: EDTF Date and Interval both have same interface
            #       and date.lower_strict() <= date.upper_strict() is always
            #       True for a Date
            result = result[0]
            if result.upper_strict() < result.lower_strict():
                raise self.make_error("invalid")

            return (
                super(EDTFLevel0DateString, self)
                ._deserialize(str(result), attr, data, **kwargs)
            )
        except ParseException:
            raise self.make_error("invalid")
