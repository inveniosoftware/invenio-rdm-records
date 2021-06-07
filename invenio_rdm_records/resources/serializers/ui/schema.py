# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

from copy import deepcopy
from functools import partial

from flask import current_app
from flask_babelex import get_locale
from flask_babelex import gettext as _
from invenio_i18n.ext import current_i18n
from marshmallow import Schema, fields, missing
from marshmallow_utils.fields import BabelGettextDictField
from marshmallow_utils.fields import FormatDate as FormatDate_
from marshmallow_utils.fields import FormatEDTF as FormatEDTF_
from marshmallow_utils.fields import StrippedHTML

from .fields import AccessStatusField


def current_default_locale():
    """Get the Flask app's default locale."""
    if current_app:
        return current_app.config.get('BABEL_DEFAULT_LOCALE', 'en')
    # Use english by default if not specified
    return 'en'


# Partial to make short definitions in below schema.
FormatEDTF = partial(FormatEDTF_, locale=get_locale)
FormatDate = partial(FormatDate_, locale=get_locale)
L10NString = partial(BabelGettextDictField, get_locale, current_default_locale)


def make_affiliation_index(attr, obj, dummy_ctx):
    """Serializes creators/contributors for easier UI consumption."""
    # Copy so we don't modify in place the existing dict.
    creators = deepcopy(obj.get('metadata', {}).get(attr))
    if not creators:
        return missing

    affiliations_idx = {}
    # Below is a trick to make sure we can increment in the index inside
    # the apply_idx function without overwriting the outer scope.
    index = {'val': 1}

    def apply_idx(affiliation):
        """Map an affiliation into list of (index, affiliation string)."""
        name = affiliation.get('name')
        if name not in affiliations_idx:
            affiliations_idx[name] = index['val']
            index['val'] += 1
        idx = affiliations_idx[name]
        return [idx, name]

    # For each creator, apply the
    for creator in creators:
        if 'affiliations' in creator:
            creator['affiliations'] = list(map(
                apply_idx,
                creator['affiliations']
            ))

    # Create a full list of affiliations.
    affiliation_list = [[v, k] for k, v in affiliations_idx.items()]
    affiliation_list.sort(key=lambda x: x[0])

    return {
        attr: creators,
        'affiliations': affiliation_list,
    }


def record_version(obj):
    """Return record's version."""
    field_data = obj.get("metadata", {}).get("version")

    if not field_data:
        return f"v{obj['versions']['index']}"

    return field_data


class ResourceTypeL10NSchema(Schema):
    """Localization of resource type title."""

    id = fields.String()
    title = L10NString(data_key='title_l10n')


class LanguageL10NSchema(Schema):
    """Localization of language titles."""

    id = fields.String()
    title = L10NString(data_key='title_l10n')


class SubjectL10NSchema(Schema):
    """Localization of subject titles."""

    id = fields.String()
    title = L10NString(data_key='title_l10n')


class UIObjectSchema(Schema):
    """Schema for dumping extra information for the UI."""

    publication_date_l10n_medium = FormatEDTF(
        attribute='metadata.publication_date', format='medium')

    publication_date_l10n_long = FormatEDTF(
        attribute='metadata.publication_date', format='long')

    created_date_l10n_long = FormatDate(attribute='created', format='long')

    updated_date_l10n_long = FormatDate(attribute='updated', format='long')

    resource_type = fields.Nested(
        ResourceTypeL10NSchema,
        attribute='metadata.resource_type'
    )

    access_status = AccessStatusField(attribute='access')

    creators = fields.Function(partial(make_affiliation_index, 'creators'))

    contributors = fields.Function(
        partial(make_affiliation_index, 'contributors'))

    languages = fields.List(
        fields.Nested(LanguageL10NSchema),
        attribute='metadata.languages',
    )

    subjects = fields.List(
        fields.Nested(SubjectL10NSchema),
        attribute='metadata.subjects',
    )

    description_stripped = StrippedHTML(attribute="metadata.description")

    version = fields.Function(record_version)


#
# List schema
class UIListSchema(Schema):
    """Schema for dumping extra information in the UI."""

    hits = fields.Method('get_hits')
    aggregations = fields.Method('get_aggs')

    def get_hits(self, obj_list):
        """Apply hits transformation."""
        for obj in obj_list['hits']['hits']:
            obj[self.context['object_key']] = \
                self.context['object_schema_cls']().dump(obj)
        return obj_list['hits']

    def get_aggs(self, obj_list):
        """Apply aggregations transformation."""
        aggs = obj_list.get("aggregations")
        if not aggs:
            return missing
        return aggs
