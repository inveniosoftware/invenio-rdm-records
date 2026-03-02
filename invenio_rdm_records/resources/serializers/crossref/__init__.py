# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2026 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Crossref Serializers for Invenio RDM Records."""

from commonmeta import (
    CrossrefError,
    CrossrefXMLSchema,
    Metadata,
    tostring,
    write_crossref_xml,
)
from flask import current_app
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer


class CrossrefXMLSerializer(MarshmallowSerializer):
    """Marshmallow based Crossref XML serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        encoder = options.get("encoder", tostring)
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=CrossrefXMLSchema,
            list_schema_cls=BaseListSchema,
            encoder=encoder,
            **options,
        )

    def serialize_object(self, obj):
        """Serialize a single record to Crossref XML bytes.

        Overrides the default to avoid double-encoding, since
        ``dump_obj`` already returns XML bytes.
        """
        return self.dump_obj(obj)

    def dump_obj(self, record, url=None):
        """Dump a single record.

        Config variables for Crossref XML head elements are used in the
        XML head element.

        :param record: Record instance (dict, Record model, or ChainObject).
        :param url: the landing page URL for the DOI.
            Falls back to ``SITE_UI_URL``/records/<id> if not provided.
        """
        # Determine the URL that the DOI resolves to, in the following order:
        #
        # 1. identifier of type url in ``metadata.identifiers``
        #    (e.g. archived original content)
        # 2. The landing page URL passed by the PID service
        # 3. Default constructed from ``SITE_UI_URL`` and record ID
        #    (e.g. for Celery tasks or tests without UI endpoints)
        identifiers = (
            record.get("metadata", {}).get("identifiers", [])
            if isinstance(record, dict)
            else getattr(getattr(record, "metadata", None), "get", lambda *a: [])(
                "identifiers", []
            )
        )
        registered_url = (
            next(
                (
                    i.get("identifier")
                    for i in (identifiers or [])
                    if i.get("scheme") == "url" and i.get("identifier") is not None
                ),
                None,
            )
            or url
        )

        if registered_url is None:
            site_url = current_app.config.get("SITE_UI_URL", "")
            record_id = (
                record.get("id")
                if isinstance(record, dict)
                else getattr(record, "id", None)
            )
            if site_url and record_id:
                registered_url = f"{site_url}/records/{record_id}"

        # Convert the metadata to crossref_xml format via the commonmeta intermediary format.
        # XML Schema validation errors raise CrossrefError.
        try:
            metadata = Metadata(
                record,
                via="inveniordm",
                url=registered_url,
            )
            crossref_xml = write_crossref_xml(metadata)
            head = {
                "depositor": current_app.config.get("CROSSREF_DEPOSITOR"),
                "email": current_app.config.get("CROSSREF_EMAIL"),
                "registrant": current_app.config.get("CROSSREF_REGISTRANT"),
            }
            return tostring(crossref_xml, head=head)
        except CrossrefError as e:
            current_app.logger.error(
                f"CrossrefError while converting {metadata.id} to Crossref XML: {str(e)}"
            )
            return ""
