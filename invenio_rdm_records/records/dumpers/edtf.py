# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

import calendar

from arrow import Arrow
from edtf import parse_edtf
from edtf.parser.edtf_exceptions import EDTFParseException
from invenio_records.dictutils import dict_lookup, parse_lookup_key
from invenio_records.dumpers import ElasticsearchDumperExt
from pytz import utc


def _format_date(date):
    """Format the given date into ISO format."""
    arrow = Arrow.fromtimestamp(calendar.timegm(date), tzinfo=utc)
    return arrow.date().isoformat()


class EDTFDumperExt(ElasticsearchDumperExt):
    """Elasticsearch dumper extension for EDTF dates support.

    It parses the value (i.e. the EDTF level 0 string) of the specified
    field in the document and adds a dictionary holding the values
    :code:`{"lte": lower_strict, "gte": upper_strict}`, whose values correspond
    to the lower strict and upper strict bounds.
    They are required for sorting.
    In an ascending sort (most recent last), sort by `<FIELD_NAME>_range.gte`
    to get a natural sort order. In a descending sort (most recent first),
    sort by `<FIELD_NAME>_range.lte`.
    """

    def __init__(self, field):
        """Constructor.

        :param field: dot separated path to the EDTF field to process.
        """
        super(EDTFDumperExt, self).__init__()
        self.keys = parse_lookup_key(field)
        self.key = self.keys[-1]
        self.range_key = "{}_range".format(self.key)

    def dump(self, record, data):
        """Dump the data."""
        try:
            parent_data = dict_lookup(data, self.keys, parent=True)
            pd = parse_edtf(parent_data[self.key])
            parent_data[self.range_key] = {
                "gte": _format_date(pd.lower_strict()),
                "lte": _format_date(pd.upper_strict()),
            }

        except (KeyError, EDTFParseException):
            # The field does not exists or had wrong data
            return data  # FIXME: should log this in debug mode?

    def load(self, data, record_cls):
        """Load the data."""
        try:
            parent_data = dict_lookup(data, self.keys, parent=True)
            # `None` covers the cases where exceptions were raised in _dump
            parent_data.pop(self.range_key, None)
        except KeyError:
            # Drafts partially saved with no data
            # The empty {} gets removed by `clear_none`
            return data


class EDTFListDumperExt(ElasticsearchDumperExt):
    """Elasticsearch dumper extension for support of EDTF date lists.

    It iterates over the items at the specified field in the
    document and adds dictionaries holding the values
    :code:`{"lte": lower_strict, "gte": upper_strict}`, as parsed
    from their EDTF fields (specified by the key).
    These values correspond to the lower strict and upper strict bounds.
    They are required for sorting.
    In an ascending sort (most recent last), sort by `<FIELD_NAME>_range.gte`
    to get a natural sort order. In a descending sort (most recent first),
    sort by `<FIELD_NAME>_range.lte`.
    """

    def __init__(self, list_field, key):
        """Constructor.

        :param list_field: dot-separated path to the array to process.
        :param key: name of the (scalar) EDTF field. This field has to be
                    present in each array item. In contrast to `list_field`,
                    this should be a simple field name (and not a
                    dot-separated path).
        """
        super(EDTFListDumperExt, self).__init__()
        self.keys = parse_lookup_key(list_field)
        self.key = key
        self.range_key = "{}_range".format(self.key)

    def dump(self, record, data):
        """Dump the data."""
        try:
            date_list = dict_lookup(data, self.keys, parent=False)

            # note: EDTF parse_edtf (using pyparsing) expects a string
            for item in date_list:
                pd = parse_edtf(item[self.key])
                item[self.range_key] = {
                    "gte": _format_date(pd.lower_strict()),
                    "lte": _format_date(pd.upper_strict()),
                }

        except (KeyError, EDTFParseException):
            # The field does not exists or had wrong data
            return data  # FIXME: should log this in debug mode?

    def load(self, data, record_cls):
        """Load the data."""
        try:
            date_list = dict_lookup(data, self.keys, parent=False)

            # `None` covers the cases where exceptions were raised in _dump
            for item in date_list:
                item.pop(self.range_key, None)

        except KeyError:
            return data
