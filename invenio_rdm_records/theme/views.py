# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio RDM Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint used for loading templates.

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""

from operator import itemgetter
from os.path import splitext

import arrow
import idutils
from arrow.parser import ParserError
from flask import Blueprint, current_app, render_template
from flask_babelex import format_date as babel_format_date
from invenio_previewer.views import is_previewable
from invenio_records_permissions.policies import get_record_permission_policy

from ..utils import is_doi_locally_managed
from ..vocabularies import Vocabularies

blueprint = Blueprint(
    'invenio_rdm_records',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/coming-soon')
def coming_soon():
    """Route to display on soon-to-come features."""
    return render_template('invenio_rdm_records/coming_soon_page.html')


@blueprint.app_template_filter('to_date')
def to_date(date_string):
    """Return a Date object from a passed date string.

    Typically used as follows:

        ```jinja2
        {{ date_string | to_date | date_format("long") }}
        ```
    """
    assert isinstance(date_string, str)
    date = ""
    try:
        date = arrow.get(date_string).date()
    except ParserError:
        date = date_string
    return date


@blueprint.app_template_filter('format_date')
def format_date(date, format):
    """Return a formatted Date string.

    If the passed date is a string then it returns it

    Typically used as follows:

        ```jinja2
        {{ date | format_date("long") }}
        ```
    """
    if isinstance(date, str):
        return date
    return babel_format_date(date=date, format=format)


@blueprint.app_template_filter()
def select_preview_file(files):
    """Get list of files and select one for preview."""
    selected = None

    try:
        for f in sorted(files or [], key=itemgetter('key')):
            file_type = splitext(f['key'])[1][1:].lower()
            if is_previewable(file_type):
                if selected is None:
                    selected = f
                elif f['default']:
                    selected = f
    except KeyError:
        pass
    return selected


@blueprint.app_template_filter('can_list_files')
def can_list_files(record):
    """Permission check if current user can list files of record.

    The current_user is used under the hood by flask-principal.

    Once we move to Single-Page-App approach, we likely want to enforce
    permissions at the final serialization level (only).
    """
    PermissionPolicy = get_record_permission_policy()
    return PermissionPolicy(action='read_files', record=record).can()


@blueprint.app_template_filter()
def contributortype_title(value):
    """Get object type."""
    return current_app.config.get('RECORD_CONTRIBUTOR_TYPES_LABELS', {}).get(
        value, value)


@blueprint.app_template_filter('pid_url')
def pid_url(identifier, scheme=None, url_scheme='https'):
    """Convert persistent identifier into a link."""
    if scheme is None:
        try:
            scheme = idutils.detect_identifier_schemes(identifier)[0]
        except IndexError:
            scheme = None
    try:
        if scheme and identifier:
            return idutils.to_url(identifier, scheme, url_scheme=url_scheme)
    except Exception:
        current_app.logger.warning('URL generation for identifier {0} failed.'
                                   .format(identifier), exc_info=True)
    return ''


@blueprint.app_template_filter('doi_identifier')
def doi_identifier(identifiers):
    """Determine if DOI is managed locally."""
    for identifier in identifiers:
        # TODO: extract this "DOI" constant to a registry?
        if identifier == 'DOI':
            return identifiers[identifier]


@blueprint.app_template_filter('doi_locally_managed')
def doi_locally_managed(pid):
    """Determine if DOI is managed locally."""
    return is_doi_locally_managed(pid)


@blueprint.app_template_filter('vocabulary_title')
def vocabulary_title(dict_key, vocabulary_key):
    """Returns formatted vocabulary-corresponding human-readable string."""
    vocabulary = Vocabularies.get_vocabulary(vocabulary_key)
    return vocabulary.get_title_by_dict(dict_key)
