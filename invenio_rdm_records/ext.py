# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from __future__ import absolute_import, print_function

from flask_babelex import gettext as _

from . import config


class InvenioRDMRecords(object):
    """Invenio-RDM-Records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions['invenio-rdm-records'] = self

    def init_config(self, app):
        """Initialize configuration."""
        with_endpoints = app.config.get(
            'RDM_RECORDS_ENDPOINTS_ENABLED', True)
        for k in dir(config):
            if k.startswith('RDM_RECORDS_'):
                app.config.setdefault(k, getattr(config, k))
            elif k == 'SEARCH_UI_JSTEMPLATE_RESULTS':
                app.config[k] = getattr(config, k)
            elif k == 'PIDSTORE_RECID_FIELD':
                app.config[k] = getattr(config, k)
            elif with_endpoints:
                if k in ['RECORDS_REST_ENDPOINTS', 'RECORDS_UI_ENDPOINTS',
                         'RECORDS_REST_FACETS', 'RECORDS_REST_SORT_OPTIONS',
                         'RECORDS_REST_DEFAULT_SORT']:
                    app.config.setdefault(k, {})
                    app.config[k].update(getattr(config, k))
