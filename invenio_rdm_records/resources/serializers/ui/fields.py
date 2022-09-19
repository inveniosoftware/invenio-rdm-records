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

from invenio_rdm_records.records.systemfields.access.field.record import (
    AccessStatusEnum,
)


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
            AccessStatusEnum.EMBARGOED: "outline clock",
            AccessStatusEnum.RESTRICTED: "ban",
            AccessStatusEnum.METADATA_ONLY: "tag",
        }.get(self.access_status)


class UIObjectAccessStatus(UIAccessStatus):
    """Record or draft access status UI properties."""

    def __init__(self, record_access_dict, has_files):
        """Build access status object."""
        self.record_access_dict = record_access_dict
        self.has_files = has_files
        super().__init__(record_access_dict.get("status"))

    @property
    def description(self):
        """Record access status description."""
        options = {
            AccessStatusEnum.OPEN: _("The record and files are publicly accessible."),
            AccessStatusEnum.METADATA_ONLY: _(
                "No files are available for this record."
            ),
        }

        if self.record_access_dict.get("record") == "restricted":
            if self.has_files:
                options.update(
                    {
                        AccessStatusEnum.EMBARGOED: _(
                            "The record and files will be made publicly available "
                            "on %(date)s."
                        )
                        % {"date": self.embargo_date},
                        AccessStatusEnum.RESTRICTED: _(
                            "The record and files are restricted to users with "
                            "access."
                        ),
                    }
                )
            else:
                options.update(
                    {
                        AccessStatusEnum.EMBARGOED: _(
                            "The record will be made publicly available on " "%(date)s."
                        )
                        % {"date": self.embargo_date},
                        AccessStatusEnum.RESTRICTED: _(
                            "The record is restricted to users with access."
                        ),
                    }
                )
        else:
            options.update(
                {
                    AccessStatusEnum.EMBARGOED: _(
                        "The files will be made publicly available on " "%(date)s."
                    )
                    % {"date": self.embargo_date},
                    AccessStatusEnum.RESTRICTED: _(
                        "The record is publicly accessible, but files are "
                        "restricted to users with access."
                    ),
                }
            )

        return options.get(self.access_status)

    @property
    def embargo_date(self):
        """Embargo date."""
        until = self.record_access_dict.get("embargo").get("until")
        if until:
            return format_edtf(until, format="long")
        return until

    @property
    def message_class(self):
        """UI message class name."""
        return {
            AccessStatusEnum.OPEN: "",
            AccessStatusEnum.EMBARGOED: "warning",
            AccessStatusEnum.RESTRICTED: "negative",
            AccessStatusEnum.METADATA_ONLY: "",
        }.get(self.access_status)


class AccessStatusField(fields.Field):
    """Record access status."""

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialise access status."""
        record_access_dict = obj.get("access")
        has_files = obj.get("files").get("enabled", False)
        if record_access_dict:
            record_access_status_ui = UIObjectAccessStatus(
                record_access_dict, has_files
            )
            return {
                "id": record_access_status_ui.id,
                "title_l10n": record_access_status_ui.title,
                "description_l10n": record_access_status_ui.description,
                "icon": record_access_status_ui.icon,
                "embargo_date_l10n": record_access_status_ui.embargo_date,
                "message_class": record_access_status_ui.message_class,
            }
