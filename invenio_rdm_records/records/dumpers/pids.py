# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Elasticsearch dumpers for PIDs."""


from invenio_records.dumpers import ElasticsearchDumperExt


class PIDsDumperExt(ElasticsearchDumperExt):
    """Elasticsearch dumper extension for  PIDs support.

    The JSON representation of the PIDs is a dictionary which keys
    are the identifier's scheme. However, that would turn into a dynamic
    mapping in ES with `text` type attributes. We want to be able to
    search by e.g. DOI in exact match terms. Since it contains dots, slashes,
    etc. it must be of type `keyword`. Therefore, this dumper turns the dict
    into a fixed mapping, dumping the key into the scheme attribute.
    """

    def dump(self, record, data):
        """Dump the data."""
        pids = data.get('pids', {})
        if pids:
            dumped_pids = []
            for scheme, pid_attrs in pids.items():
                dumped_pids.append({
                    "scheme": scheme,
                    **pid_attrs
                })

            data['pids'] = dumped_pids

    def load(self, data, record_cls):
        """Load the data."""
        pids = data.get('pids', {})
        if pids:
            loaded_pids = {}
            for pid_attrs in pids:
                scheme = pid_attrs.pop('scheme')
                loaded_pids[scheme] = pid_attrs

            data['pids'] = loaded_pids
