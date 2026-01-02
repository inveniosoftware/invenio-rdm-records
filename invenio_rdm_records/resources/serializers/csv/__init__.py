# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSV Serializer for Invenio RDM Records."""

from flask_resources.serializers import CSVSerializer


class CSVRecordSerializer(CSVSerializer):
    """Marshmallow based CSV serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(header_separator=".", **options)
