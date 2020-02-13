# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json

from flask import Flask
from invenio_search import current_search

from invenio_rdm_records import InvenioRDMRecords


def test_version():
    """Test version import."""
    from invenio_rdm_records import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioRDMRecords(app)
    assert 'invenio-rdm-records' in app.extensions

    app = Flask('testapp')
    ext = InvenioRDMRecords()
    assert 'invenio-rdm-records' not in app.extensions
    ext.init_app(app)
    assert 'invenio-rdm-records' in app.extensions
