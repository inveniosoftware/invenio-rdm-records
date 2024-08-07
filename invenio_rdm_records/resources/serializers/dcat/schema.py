# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dcat based Schema for Invenio RDM Records."""

import idutils
from flask import current_app
from marshmallow import fields, missing
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
            url = f"{current_app.config['SITE_UI_URL']}/records/{record_id}/files/{file_name}"
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
