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

from flask_babelex import get_locale
from marshmallow import INCLUDE, Schema, fields, missing
from marshmallow_utils.fields import FormatDate as FormatDate_
from marshmallow_utils.fields import FormatEDTF as FormatEDTF_

from invenio_rdm_records.vocabularies import Vocabularies

from .fields import VocabularyField, VocabularyTitleField

# Partial to make short definitions in below schema.
FormatEDTF = partial(FormatEDTF_, locale=get_locale)
FormatDate = partial(FormatDate_, locale=get_locale)


def make_affiliation_index(attr, obj, dummy_ctx):
    """Serializes creators/contributors for easier UI consumption."""
    # Copy so we don't modify in place the existing dict.
    creators = deepcopy(obj['metadata'].get(attr))
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
            assigned_index = index['val']
            index['val'] += 1
        return [assigned_index, name]

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


#
# Object schema
#
class AccessRightSchema(Schema):
    """Access right vocabulary."""

    category = fields.String(attribute='access_right', dump_only=True)

    icon = VocabularyField(
        'access_right',
        entry_key='icon',
        attribute='access_right'
    )

    title = VocabularyField(
        'access_right',
        entry_key='access_right_name',
        attribute='access_right'
    )


class UIObjectSchema(Schema):
    """Schema for dumping extra information for the UI."""

    publication_date_l10n_medium = FormatEDTF(
        attribute='metadata.publication_date', format='medium')

    publication_date_l10n_long = FormatEDTF(
        attribute='metadata.publication_date', format='long')

    created_date_l10n_long = FormatDate(attribute='created', format='long')

    updated_date_l10n_long = FormatDate(attribute='updated', format='long')

    resource_type = VocabularyTitleField(
        'resource_type', attribute='metadata.resource_type')

    access_right = fields.Nested(AccessRightSchema, attribute='access')

    creators = fields.Function(partial(make_affiliation_index, 'creators'))

    contributors = fields.Function(
        partial(make_affiliation_index, 'contributors'))


#
# List schema
class UIListSchema(Schema):
    """Schema for dumping extra information in the UI."""

    class Meta:
        """."""

        unknown = INCLUDE

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

        for name, agg in aggs.items():
            # Aggregation key/name must match vocabulary id.
            vocab = Vocabularies.get_vocabulary(name)
            if not vocab:
                continue

            buckets = agg.get('buckets')
            if buckets:
                apply_labels(vocab, buckets)

        return aggs


def apply_labels(vocab, buckets):
    """Inject labels in the aggregation buckets.

    :params agg: Current aggregation object.
    :params vocab: The vocabulary
    """
    for b in buckets:
        b['label'] = vocab.get_title_by_dict(b['key'])

        # Recursively apply to subbuckets
        for data in b.values():
            if isinstance(data, dict) and 'buckets' in data:
                apply_labels(vocab, data['buckets'])
