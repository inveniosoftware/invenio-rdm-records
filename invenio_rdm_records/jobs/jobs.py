# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Jobs definition module."""

from invenio_i18n import lazy_gettext as _
from invenio_jobs.jobs import JobType

from invenio_rdm_records.services.tasks import update_expired_embargos

update_expired_embargos_cls = JobType.create(
    arguments_schema=None,
    job_cls_name="UpdateEmbargoesJob",
    id_="update_expired_embargos",
    task=update_expired_embargos,
    description=_("Updates expired embargoes"),
    title=_("Update expired embargoes"),
)
