# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

import calendar
from datetime import date

from edtf import parse_edtf
from edtf.parser.edtf_exceptions import EDTFParseException
from invenio_records.dictutils import dict_lookup, parse_lookup_key
from invenio_records.dumpers import ElasticsearchDumperExt


class EDTFDumperExt(ElasticsearchDumperExt):
    """Elasticsearch dumper extension for EDTF dates support.

    It adds two fields in the root of the document: publication_date_start
    and publication_date_end, which correspond to the lower strict and upper
    strict bounds. This are required for sorting. In an ascending sort (most
    recent last), sort by publication_date_start to get a natural sort order.
    In a descending sort (most recent first), sort by publication_date_end.
    """

    def __init__(self, field):
        """Constructor.

        :param field: dot separated path to the EDTF field to process.
        """
        super(EDTFDumperExt, self).__init__()
        self.field_path = field.split('.')

    def dump(self, record, data):
        """Dump the data."""
        try:
            keys = parse_lookup_key(self.field_path)
            key = keys[-1]
            date_value = dict_lookup(data, keys)

            pd = parse_edtf(date_value)
            data[f"{key}_start"] = date.fromtimestamp(
                calendar.timegm(pd.lower_strict())).isoformat()
            data[f"{key}_end"] = date.fromtimestamp(
                calendar.timegm(pd.upper_strict())).isoformat()
        except (KeyError, EDTFParseException):
            # The field does not exists or had wrong data
            return data  # FIXME: should log this in debug mode?

    def load(self, data, record_cls):
        """Load the data."""
        # From `dump` the new fields are always in the root
        key = parse_lookup_key(self.field_path)[-1]
        # `None` covers the cases where exceptions were raised in _dump
        data.pop(f"{key}_start", None)
        data.pop(f"{key}_end", None)
