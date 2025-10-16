# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2025 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Crossref Serializers for Invenio RDM Records."""

from commonmeta import (
    CrossrefXMLSchema,
    Metadata,
    write_crossref_xml,
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
        # Report write errors. Reasons for failing to convert to Crossref XML include missing
        # required metadata and type not supported by Crossref.
        metadata = Metadata(
            record,
            via="inveniordm",
            depositor=current_app.config.get("CROSSREF_DEPOSITOR"),
            email=current_app.config.get("CROSSREF_EMAIL"),
            registrant=current_app.config.get("CROSSREF_REGISTRANT"),
        )
        crossref_xml, write_errors = write_crossref_xml(metadata)
        if write_errors is not None:
            current_app.logger.error(
                f"Could not convert metadata {metadata.id} to Crossref XML: {write_errors}"
            )
        return crossref_xml

    @classmethod
    def crossref_xml_tostring(cls, record):
        """Stringify a Crossref XML record."""
        return record
