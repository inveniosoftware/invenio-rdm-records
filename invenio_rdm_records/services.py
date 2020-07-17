# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Service."""

from invenio_records_resources.services import RecordService, \
    RecordServiceConfig

# TODO: IMPLEMENT ME if more specialized configuration needed
# class BibliographicRecordServiceConfig(RecordServiceConfig):
#     """Bibliographic Record Service configuration."""


class BibliographicRecordService(RecordService):
    """Bibliographic Record Service."""

    default_config = RecordServiceConfig
