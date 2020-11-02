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
        self.keys = parse_lookup_key(field)
        self.key = self.keys[-1]

    def dump(self, record, data):
        """Dump the data."""
        try:
            parent_data = dict_lookup(data, self.keys, parent=True)

            pd = parse_edtf(parent_data[self.key])
            parent_data[f"{self.key}_start"] = Arrow.fromtimestamp(
                calendar.timegm(pd.lower_strict()), tzinfo=utc
                ).date().isoformat()
            parent_data[f"{self.key}_end"] = Arrow.fromtimestamp(
                calendar.timegm(pd.upper_strict()), tzinfo=utc
                ).date().isoformat()
        except (KeyError, EDTFParseException):
            # The field does not exists or had wrong data
            return data  # FIXME: should log this in debug mode?

    def load(self, data, record_cls):
        """Load the data."""
        parent_data = dict_lookup(data, self.keys, parent=True)

        # `None` covers the cases where exceptions were raised in _dump
        parent_data.pop(f"{self.key}_start", None)
        parent_data.pop(f"{self.key}_end", None)
