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
