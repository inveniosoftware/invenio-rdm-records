# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dcat based Schema for Invenio RDM Records."""

import idutils
from invenio_base import invenio_url_for
from marshmallow import ValidationError, fields, missing, validate
from marshmallow_utils.html import sanitize_unicode

from invenio_rdm_records.resources.serializers.datacite import DataCite43Schema


class DcatSchema(DataCite43Schema):
    """Dcat Marshmallow Schema."""

    _files = fields.Method("get_files")

    def get_files(self, obj):
        """Get files."""
        files_enabled = obj["files"].get("enabled", False)
        if not files_enabled:
            return missing
        files_entries = obj["files"].get("entries", {})
        record_id = obj["id"]
        files_list = []
        for key, value in files_entries.items():
            file_name = sanitize_unicode(
                value["key"]
            )  # There can be inconsistencies in the file name i.e. if the file name consists of invalid XML characters
            url = invenio_url_for(
                "invenio_app_rdm_records.record_file_download",
                pid_value=record_id,
                filename=file_name,
            )
            access_url = None
            if "doi" in obj["pids"]:
                access_url = idutils.to_url(
                    obj["pids"]["doi"]["identifier"], "doi", url_scheme="https"
                )

            files_list.append(
                dict(
                    size=str(value["size"]),
                    access_url=access_url,
                    download_url=url,
                    key=value["key"],
                )
            )

        return files_list or missing

    def get_subjects(self, obj):
        """Get subjects."""
        subjects = obj["metadata"].get("subjects", [])
        if not subjects:
            return missing

        validator = validate.URL()
        serialized_subjects = []

        for subject in subjects:
            entry = {"subject": subject.get("subject")}

            id_ = subject.get("id")
            if id_:
                entry["subjectScheme"] = subject.get("scheme")
                try:
                    validator(id_)
                    entry["valueURI"] = id_
                except ValidationError:
                    pass

            # Get identifiers and assign valueURI if scheme is 'url' and id_ was not a valid url
            if "valueURI" not in entry:
                entry["valueURI"] = next(
                    (
                        identifier.get("identifier")
                        for identifier in subject.get("identifiers", [])
                        if identifier.get("scheme") == "url"
                    ),
                    None,
                )

            # Add props if it exists
            props = subject.get("props", {})
            if props:
                entry["subjectProps"] = props

            serialized_subjects.append(entry)

        return serialized_subjects if serialized_subjects else missing
