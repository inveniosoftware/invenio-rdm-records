# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Service."""

from invenio_records_resources.services import MarshmallowDataValidator, \
    RecordService, RecordServiceConfig

from invenio_rdm_records.permissions import RDMRecordPermissionPolicy

from .marshmallow.json import MetadataSchemaV1


# TODO: IMPLEMENT ME if more specialized configuration needed
class BibliographicRecordServiceConfig(RecordServiceConfig):
    """Bibliographic Record Service configuration."""

    permission_policy_cls = RDMRecordPermissionPolicy
    data_validator = MarshmallowDataValidator(
        schema=MetadataSchemaV1)


class BibliographicRecordService(RecordService):
    """Bibliographic Record Service."""

    default_config = BibliographicRecordServiceConfig
