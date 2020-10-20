# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

import json
from functools import partial

from flask_resources.serializers import JSONSerializer

from invenio_rdm_records.vocabularies import Vocabularies


class UIJSONSerializer(JSONSerializer):
    """UI JSON serializer implementation."""

    def _serialize_access_right(self, obj):
        """Inject ui config for `access_right` field."""
        return dict(
            access_right=dict(
                category=obj["access"]["access_right"]
            ))

    def _serialize_ui_options_from_vocabulary(
            self, vocabulary_name, top_bucket_key=None):
        """Creates UI facet label options from RDM vocabularies.

        :params top_bucket_key: Key used for nested buckets to indicate
                                the top level aggregation.
        """
        ui_options = {}
        vocabulary = Vocabularies.get_vocabulary(
            vocabulary_name).dump_options()
        if type(vocabulary) is dict:
            ui_options[top_bucket_key] = {}
            for key in vocabulary.keys():
                for option in vocabulary[key]:
                    ui_options[top_bucket_key][option['value']] = \
                        str(option['text'])
        else:
            for option in vocabulary:
                ui_options[option['value']] = str(option['text'])
        return ui_options

    def _set_bucket_label(self, labels_map, bucket):
        """Set bucket label from config.

        :params labels_map: Dict of transforming bucket values to labels.
        :params bucket: Current aggregation bucket.
        """
        bucket_label = labels_map.get(bucket["key"])
        if bucket_label:
            bucket["label"] = bucket_label
        if bucket.get("subtype"):
            bucket["subtype"]["buckets"] = list(map(
                partial(self._set_bucket_label, labels_map),
                bucket["subtype"]["buckets"]))
        return bucket

    def _set_buckets_labels(self, label_map, buckets):
        """Map buckets values to labels according to configuration.

        :params labels_map: Dict of transforming bucket values to labels.
        :params buckets: Current aggregation bucket list.
        """
        return list(map(
                partial(self._set_bucket_label, label_map),
                buckets))

    def _serialize_agg(self, agg_obj, labels_map):
        """Inject ui config for aggregation.

        :params agg_obj: Current aggregation object.
        :params labels_map: Dict of transforming bucket values to labels.
        """
        if agg_obj:
            agg_obj["buckets"] = self._set_buckets_labels(
                labels_map, agg_obj["buckets"]
            )

    def _serialize_resource_type_agg(self, resource_type_agg):
        """Inject ui config for `resource_type` aggregation."""
        resource_type_labels = self._serialize_ui_options_from_vocabulary(
            "resource_type", "type")
        self._serialize_agg(resource_type_agg, resource_type_labels["type"])

    def _serialize_access_right_agg(self, access_right_agg):
        """Inject ui config for `access_right` aggregation."""
        access_right_labels = self._serialize_ui_options_from_vocabulary(
            "access_right")
        self._serialize_agg(access_right_agg, access_right_labels)

    def _serialize_aggregations(self, obj_list):
        """Inject ui config in aggregations."""
        aggregations = obj_list.get("aggregations")
        if aggregations:
            self._serialize_access_right_agg(aggregations.get("access_right"))
            self._serialize_resource_type_agg(
                aggregations.get("resource_type"))

    def serialize_object(self, obj, response_ctx=None, *args, **kwargs):
        """Dump the object into a json string."""
        obj['ui'] = self._serialize_access_right(obj)
        return json.dumps(obj)

    def serialize_object_list(
            self, obj_list, response_ctx=None, *args, **kwargs):
        """Dump the object list into a json string."""
        self._serialize_aggregations(obj_list)
        for obj in obj_list["hits"]["hits"]:
            obj['ui'] = self._serialize_access_right(obj)
        return json.dumps(obj_list)
