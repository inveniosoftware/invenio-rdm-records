# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from invenio_records.dictutils import dict_set
from invenio_records.dumpers import ElasticsearchDumperExt


class HasDraftDumperExt(ElasticsearchDumperExt):
    """Elasticsearch dumper extension to store if the record has a draft.

    It stores the `record.has_draft` value in the ES record or defaults to
    `False` if the method is not defined e.g Draft records.
    """

    def __init__(self, key):
        """Constructor.

        :param key: field path to store if the record has a draft.
        """
        self.key = key

    def dump(self, record, data):
        """Dump the data."""
        dict_set(
            data,
            self.key,
            getattr(record, 'has_draft', False)
        )

    def load(self, data, record_cls):
        """Load the data."""
        data.pop(self.key, None)
