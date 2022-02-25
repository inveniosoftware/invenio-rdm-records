# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

from ast import literal_eval
from copy import deepcopy
from functools import partial

from flask import current_app
from flask_babelex import get_locale
from invenio_i18n.ext import current_i18n
from marshmallow import Schema, fields, missing
from marshmallow_utils.fields import BabelGettextDictField
from marshmallow_utils.fields import FormatDate as FormatDate_
from marshmallow_utils.fields import FormatEDTF as FormatEDTF_
from marshmallow_utils.fields import StrippedHTML
from marshmallow_utils.fields.babel import gettext_from_dict

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
L10NString = partial(BabelGettextDictField, get_locale,
                     current_default_locale())


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
    affiliation_list = []

    def apply_idx(affiliation):
        """Map an affiliation into list of (index, affiliation string)."""
        name = affiliation.get('name')
        id_value = affiliation.get('id')
        if name not in affiliations_idx:
            affiliations_idx[name] = index['val']
            affiliation_list.append([index['val'], name, id_value])
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
        if 'role' in creator:
            creator['role']['title'] = gettext_from_dict(
                creator['role']['title'],
                get_locale(),
                current_default_locale()
            )

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


class VocabularyL10Schema(Schema):
    """Vocabulary schema."""

    id = fields.String()
    title = L10NString(data_key='title_l10n')


class RelatedIdentifiersSchema(Schema):
    """Localization of language titles."""

    identifier = fields.String()
    relation_type = fields.Nested(
        VocabularyL10Schema,
        attribute='relation_type'
    )
    scheme = fields.String()
    resource_type = fields.Nested(
        VocabularyL10Schema,
        attribute='resource_type'
    )


class AdditionalTitlesSchema(Schema):
    """Additional titles schema."""

    title = fields.String()
    type = fields.Nested(
        VocabularyL10Schema,
        attribute='type'
    )
    lang = fields.Nested(
        VocabularyL10Schema,
        attribute='lang'
    )


class AdditionalDescriptionsSchema(Schema):
    """Localization of additional descriptions."""

    description = StrippedHTML(attribute='description')
    type = fields.Nested(
        VocabularyL10Schema,
        attribute='type'
    )
    lang = fields.Nested(
        VocabularyL10Schema,
        attribute='lang'
    )


class DatesSchema(Schema):
    """Localization of dates."""

    date = fields.String()
    type = fields.Nested(
        VocabularyL10Schema,
        attribute='type'
    )
    description = StrippedHTML(attribute='description')


class RightsSchema(VocabularyL10Schema):
    """Rights schema."""

    description = L10NString(data_key='description_l10n')
    icon = fields.Str(dump_only=True)
    link = fields.String()
    props = fields.Dict()


class UIObjectSchema(Schema):
    """Schema for dumping extra information for the UI."""

    publication_date_l10n_medium = FormatEDTF(
        attribute='metadata.publication_date', format='medium')

    publication_date_l10n_long = FormatEDTF(
        attribute='metadata.publication_date', format='long')

    created_date_l10n_long = FormatDate(attribute='created', format='long')

    updated_date_l10n_long = FormatDate(attribute='updated', format='long')

    resource_type = fields.Nested(
        VocabularyL10Schema,
        attribute='metadata.resource_type'
    )

    additional_titles = fields.List(
        fields.Nested(AdditionalTitlesSchema),
        attribute='metadata.additional_titles'
    )

    access_status = AccessStatusField(attribute='access')

    creators = fields.Function(partial(make_affiliation_index, 'creators'))

    contributors = fields.Function(
        partial(make_affiliation_index, 'contributors'))

    languages = fields.List(
        fields.Nested(VocabularyL10Schema),
        attribute='metadata.languages',
    )

    description_stripped = StrippedHTML(attribute="metadata.description")

    version = fields.Function(record_version)

    related_identifiers = fields.List(
        fields.Nested(RelatedIdentifiersSchema()),
        attribute="metadata.related_identifiers"
    )

    additional_descriptions = fields.List(
        fields.Nested(AdditionalDescriptionsSchema()),
        attribute="metadata.additional_descriptions"
    )

    dates = fields.List(
        fields.Nested(DatesSchema()),
        attribute="metadata.dates"
    )

    rights = fields.List(
        fields.Nested(RightsSchema()),
        attribute="metadata.rights"
    )

    is_draft = fields.Boolean(attribute="is_draft")


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
