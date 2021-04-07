# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

from babel_edtf import format_edtf
from flask_babelex import gettext as _
from marshmallow import fields

from invenio_rdm_records.records.systemfields.access.field.record import \
    AccessStatusEnum
from invenio_rdm_records.vocabularies import Vocabularies


class VocabularyField(fields.String):
    """Vocabulary field."""

    def __init__(self, vocabulary_name, entry_key=None, **kwargs):
        """Initialize field."""
        self.vocabulary_name = vocabulary_name
        self.entry_key = entry_key
        kwargs.setdefault('dump_only', True)
        super().__init__(**kwargs)

    @property
    def vocabulary(self):
        """Get the vocabulary."""
        return Vocabularies.get_vocabulary(self.vocabulary_name)

    def entry(self, value):
        """Get the vocabulary entry."""
        return self.vocabulary.get_entry_by_dict(value)

    def format(self, value):
        """Get the specific key or object from the vocabulary."""
        entry = self.entry(value)
        return entry[self.entry_key] if self.entry_key else entry

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize the vocabulary title."""
        return self.format(value)


class VocabularyTitleField(VocabularyField):
    """Vocabulary title field."""

    def entry(self, value):
        """Get the vocabulary title."""
        return self.vocabulary.get_title_by_dict(value)


class UIAccessStatus(object):
    """Access status properties to display in the UI."""

    def __init__(self, access_status):
        """Build access status object."""
        self.access_status = AccessStatusEnum(access_status)

    @property
    def id(self):
        """Access status id."""
        return self.access_status.value

    @property
    def title(self):
        """Access status title."""
        return {
            AccessStatusEnum.OPEN: _("Open"),
            AccessStatusEnum.EMBARGOED: _("Embargoed"),
            AccessStatusEnum.RESTRICTED: _("Restricted"),
            AccessStatusEnum.METADATA_ONLY: _("Metadata-only"),
        }.get(self.access_status)

    @property
    def icon(self):
        """Access status icon."""
        return {
            AccessStatusEnum.OPEN: "unlock",
            AccessStatusEnum.EMBARGOED: "",
            AccessStatusEnum.RESTRICTED: "lock",
            AccessStatusEnum.METADATA_ONLY: "key",
        }.get(self.access_status)


class UIObjectAccessStatus(UIAccessStatus):
    """Record or draft access status UI properties."""

    def __init__(self, record_access_dict):
        """Build access status object."""
        self.record_access_dict = record_access_dict
        super().__init__(record_access_dict.get('status'))

    @property
    def description(self):
        """Record access status description."""
        return {
            AccessStatusEnum.OPEN: lambda obj: (
                _("Files are publicly accessible.")
            ),
            AccessStatusEnum.EMBARGOED: lambda obj: (
                _("The record and files will be made publicly available on")
                + " {date}.".format(
                    date=format_edtf(obj.get('embargo').get('until')))
            ),
            AccessStatusEnum.RESTRICTED: lambda obj: (
                _("You may request access to the files in this upload, "
                  "provided that you fulfil the conditions below. The "
                  "decision whether to grant/deny access is solely under "
                  "the responsibility of the record owner.")
            ),
            AccessStatusEnum.METADATA_ONLY: lambda obj: (
                _("Files are not publicly accessible.")
            ),
        }.get(self.access_status)(self.record_access_dict)


class AccessStatusField(fields.Field):
    """Record access status."""

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialise access status."""
        record_access_dict = obj.get('access')
        if record_access_dict:
            record_access_status_ui = \
                UIObjectAccessStatus(record_access_dict)
            return {
                "id": record_access_status_ui.id,
                "title_l10n": record_access_status_ui.title,
                "description_l10n": record_access_status_ui.description,
                "icon": record_access_status_ui.icon,
            }
