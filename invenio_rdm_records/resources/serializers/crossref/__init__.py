# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2025 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Crossref Serializers for Invenio RDM Records."""

from commonmeta import (
    MARSHMALLOW_MAP,
    CrossrefXMLSchema,
    CrossrefError,
    Metadata,
    convert_crossref_xml,
    unparse_xml,
)
from flask import current_app
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer


class CrossrefXMLSerializer(MarshmallowSerializer):
    """JSON based Crossref XML serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=CrossrefXMLSchema,
            list_schema_cls=BaseListSchema,
            encoder=self.crossref_xml_tostring,
            **options,
        )

    def dump_obj(self, record):
        """Dump a single record.

        Uses config variables for Crossref XML head elements.

        :param record: Record instance.
        """
        # Convert the metadata to crossref_xml format via the commonmeta intermediary format.
        # Reasons for failing to convert to Crossref XML include missing required metadata
        # and type not supported by Crossref.
        try:
            metadata = Metadata(
                record,
                via="inveniordm",
                depositor=current_app.config.get("CROSSREF_DEPOSITOR"),
                email=current_app.config.get("CROSSREF_EMAIL"),
                registrant=current_app.config.get("CROSSREF_REGISTRANT"),
            )
            data = convert_crossref_xml(metadata)

            # Use the marshmallow schema to dump the data
            schema = CrossrefXMLSchema()
            crossref_xml = schema.dump(data)

            # Ensure consistent field ordering through the defined mapping
            field_order = [MARSHMALLOW_MAP.get(k, k) for k in list(data.keys())]
            crossref_xml = {
                k: crossref_xml[k] for k in field_order if k in crossref_xml
            }

            head = {
                "depositor": metadata.depositor,
                "email": metadata.email,
                "registrant": metadata.registrant,
            }

            # Convert the dict to Crossref XML
            return unparse_xml(crossref_xml, dialect="crossref", head=head)
        except (ValueError, CrossrefError) as e:
            current_app.logger.error(
                f"CrossrefError while converting metadata to Crossref XML: {metadata.id} - {str(e)}"
            )
            return ""

    @classmethod
    def crossref_xml_tostring(cls, record):
        """Stringify a Crossref XML record."""
        return record
