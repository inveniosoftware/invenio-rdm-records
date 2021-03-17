# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""ElasticSearch dumpers for access-control information."""

from invenio_records.dictutils import dict_lookup, parse_lookup_key
from invenio_records.dumpers import ElasticsearchDumperExt


class GrantTokensDumperExt(ElasticsearchDumperExt):
    """Elasticsearch dumper extension for access grant tokens support.

    On dump, it uses the record's ``Access`` system field to generate tokens
    from the record's (access) ``Grants`` and dump them in the specified target
    field in the dictionary (per default: ``access.grant_tokens``).
    On load, it simply removes the target field from the dictionary again.
    """

    def __init__(self, target_field):
        """Constructor.

        :param target_field: dot separated path where to dump the tokens.
        """
        super().__init__()
        self.keys = parse_lookup_key(target_field)
        self.key = self.keys[-1]

    def dump(self, record, data):
        """Dump the grant tokens to the data dictionary."""
        try:
            if record.access:
                tokens = [grant.to_token() for grant in record.access.grants]
                parent_data = dict_lookup(data, self.keys, parent=True)
                parent_data[self.key] = tokens

        except KeyError:
            pass

    def load(self, data, record_cls):
        """Remove the tokens from the data dictionary."""
        try:
            parent_data = dict_lookup(data, self.keys, parent=True)
            if parent_data is not None:
                parent_data.pop(self.key, None)

        except KeyError:
            pass
