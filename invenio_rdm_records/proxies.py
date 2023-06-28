# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Helper proxy to the state object."""

from flask import current_app
from werkzeug.local import LocalProxy

current_rdm_records = LocalProxy(lambda: current_app.extensions["invenio-rdm-records"])
"""Helper proxy to get the current RDM-Records extension."""


current_rdm_records_service = LocalProxy(
    lambda: current_app.extensions["invenio-rdm-records"].records_service
)
"""Helper proxy to get the current RDM-Records records service extension."""

current_rdm_records_media_files_service = LocalProxy(
    lambda: current_app.extensions["invenio-rdm-records"].records_media_files_service
)
"""Helper proxy to get the current RDM-Records records service extension."""

current_oaipmh_server_service = LocalProxy(
    lambda: current_app.extensions["invenio-rdm-records"].oaipmh_server_service
)
"""Helper proxy to get the current OAI-PMH service extension."""

current_record_communities_service = LocalProxy(
    lambda: current_app.extensions["invenio-rdm-records"].record_communities_service
)
"""Helper proxy to get the current Records Communities service extension."""

current_community_records_service = LocalProxy(
    lambda: current_app.extensions["invenio-rdm-records"].community_records_service
)
"""Helper proxy to get the current Communities Records service extension."""
