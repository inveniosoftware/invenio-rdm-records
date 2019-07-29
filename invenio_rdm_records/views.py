# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

# TODO: This is an example file. Remove it if you do not need it, including
# the templates and static folders as well as the test case.

from __future__ import absolute_import, print_function

from flask import Blueprint, render_template
from flask_babelex import gettext as _

blueprint = Blueprint(
    'invenio_rdm_records',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route("/")
def index():
    """Render a basic view."""
    return render_template(
        "invenio_rdm_records/index.html",
        module_name=_('Invenio-RDM-Records'))
