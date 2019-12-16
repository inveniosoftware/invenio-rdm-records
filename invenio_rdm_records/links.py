# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Links factory."""

from flask import url_for
from invenio_records_rest import current_records_rest
from invenio_records_rest.links import default_links_factory


def links_factory(pid, **kwargs):
    """Links factory for InvenioRDM records.

    For now, just adds 'files' link
    """
    links = default_links_factory(pid)
    links['files'] = url_for(
        'invenio_records_files.recid_bucket_api',
        pid_value=pid.pid_value,
        _external=True
    )
    return links
