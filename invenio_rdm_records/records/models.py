# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record and Draft models."""

from invenio_db import db
from invenio_drafts_resources.records import DraftMetadataBase


class DraftMetadata(db.Model, DraftMetadataBase):
    """Represent a bibliographic record draft metadata."""

    __tablename__ = 'drafts_metadata'
