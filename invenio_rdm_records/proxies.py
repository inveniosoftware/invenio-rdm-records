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

current_rdm_records = LocalProxy(
    lambda: current_app.extensions['invenio-rdm-records']
)
"""Helper proxy to get the current App ILS extension."""
