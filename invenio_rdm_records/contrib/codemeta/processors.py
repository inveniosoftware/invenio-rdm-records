# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Codemeta processors."""

from flask_resources.serializers import DumperMixin


class CodemetaDumper(DumperMixin):
    """Software fields dumper for CodeMeta."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds the codemeta information."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        repository = custom_fields.get("code:codeRepository")
        prog_language = custom_fields.get("code:programmingLanguage")
        platform = custom_fields.get("code:runtimePlatform")
        operating_sys = custom_fields.get("code:operatingSystem")
        status = custom_fields.get("code:developmentStatus")

        if repository:
            data["codeRepository"] = repository

        if platform:
            data["runtimePlatform"] = platform

        if prog_language:
            data["programmingLanguage"] = " ".join(
                [pl["title"]["en"] for pl in prog_language]
            )

        if operating_sys:
            data["operatingSystem"] = operating_sys

        if status:
            data["developmentStatus"] = status["title"]["en"]

        return data
