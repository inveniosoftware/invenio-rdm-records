# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow utility functions."""

import pycountry
from flask_babelex import lazy_gettext as _
from marshmallow import ValidationError


def validate_iso639_3(value):
    """Validate that language is ISO 639-3 value."""
    if not pycountry.languages.get(alpha_3=value):
        raise ValidationError(
            _('Language must be a lower-cased 3-letter ISO 639-3 string.'),
            field_name=['language']
        )
