# SPDX-FileCopyrightText: 2024 CERN
# SPDX-License-Identifier: MIT

"""CSV Serializer for Invenio RDM Records."""

from flask_resources.serializers import CSVSerializer


class CSVRecordSerializer(CSVSerializer):
    """Marshmallow based CSV serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(header_separator=".", **options)
