# SPDX-FileCopyrightText: 2023 CERN
# SPDX-License-Identifier: MIT

"""BibTex Serializer for Invenio RDM Records."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer

from .schema import BibTexSchema


class BibtexSerializer(MarshmallowSerializer):
    """Marshmallow based BibTex serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=BibTexSchema,
            list_schema_cls=BaseListSchema,
            encoder=self.bibtex_tostring,
            **options,
        )

    @classmethod
    def bibtex_tostring(cls, record):
        """Stringify a BibTex record."""
        return record
