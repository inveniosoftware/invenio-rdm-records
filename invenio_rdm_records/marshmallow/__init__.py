# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Schemas for marshmallow."""

from __future__ import absolute_import, print_function

from .json import MetadataSchemaV1, RecordSchemaV1

__all__ = ('MetadataSchemaV1', 'RecordSchemaV1',)
