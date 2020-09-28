# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from marshmallow import INCLUDE, Schema, fields, validate


#
# PIDs
#
# TODO (Alex): See how this will be managed
class PIDSSchemaV1(Schema):
    """PIDs schema."""

    doi = fields.Str()
    concept_doi = fields.Str()
    oai = fields.Str()
