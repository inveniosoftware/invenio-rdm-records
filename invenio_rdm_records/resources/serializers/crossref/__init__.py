# SPDX-FileCopyrightText: 2021-2024 CERN.
# SPDX-FileCopyrightText: 2026 Front Matter.
# SPDX-License-Identifier: MIT

"""Crossref Serializers for Invenio RDM Records."""

from commonmeta import (
    CrossrefError,
    CrossrefXMLSchema,
    Metadata,
    doi_as_url,
    tostring,
    write_crossref_xml,
)
from flask import current_app
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer
from invenio_access.permissions import system_identity

from ....proxies import current_rdm_records_service


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
            self._add_version_relations(record, metadata)
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

    def _add_version_relations(self, record, metadata):
        """Inject parent/child version relations into the commonmeta metadata.

        Mirrors the DataCite serializer: the concept (parent) DOI lists *every*
        version via ``HasVersion``; a version DOI links to its concept DOI via
        ``IsVersionOf``. This uses the records service (``scan_versions``), which
        the commonmeta reader cannot reach, so the concept DOI can list all
        versions rather than only the latest one exposed by the ChainObject.

        Emitting ``HasVersion`` requires a commonmeta-py that serializes it
        (versions < 0.263 dropped it); ``IsVersionOf`` works regardless. Lookup
        failures are logged and swallowed so version relations never block a DOI
        registration.
        """
        try:
            relations = list(metadata.relations or [])

            def add(identifier, relation_type):
                """Append a deduplicated version relation."""
                url = doi_as_url(identifier) if identifier else None
                relation = {"id": url, "type": relation_type}
                if url and relation not in relations:
                    relations.append(relation)

            # The parent/concept DOI is the only registration passed as a
            # ChainObject (see invenio_rdm_records.utils.ChainObject).
            is_parent = hasattr(record, "_child") and hasattr(record, "_parent")

            if is_parent:
                child = record._child
                child_id = (
                    child.get("id")
                    if isinstance(child, dict)
                    else getattr(child, "id", None)
                )
                if child_id:
                    # Refresh so a just-created version is visible; safe here as
                    # DOI registration runs in a Celery task.
                    current_rdm_records_service.indexer.refresh()
                    versions = current_rdm_records_service.scan_versions(
                        system_identity,
                        child_id,
                        params={"_source_includes": "pids.doi"},
                    )
                    for version in versions:
                        version_doi = (version.get("pids") or {}).get("doi") or {}
                        add(version_doi.get("identifier"), "HasVersion")
            else:
                parent = getattr(record, "parent", None)
                if parent is None and isinstance(record, dict):
                    parent = record.get("parent")
                parent_doi = ((parent or {}).get("pids") or {}).get("doi") or {}
                add(parent_doi.get("identifier"), "IsVersionOf")

            metadata.relations = relations
        except Exception as e:  # noqa: BLE001 - never block a DOI registration
            current_app.logger.warning(
                f"Could not add version relations for Crossref XML: {e}"
            )
