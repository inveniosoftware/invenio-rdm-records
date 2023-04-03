# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Search dumpers for access-control information."""

from flask import current_app
from invenio_records.dictutils import dict_lookup, parse_lookup_key
from invenio_records.dumpers import SearchDumperExt

from ..stats import Statistics


class StatisticsDumperExt(SearchDumperExt):
    """Search dumper extension for record statistics.

    On dump, it fetches the record's download & view statistics via Invenio-Stats
    queries and dumps them into a field so that they are indexed in the search engine.
    On load, it keeps the dumped values in the data dictionary, in order to enable
    the record schema to dump them if present.
    """

    def __init__(self, target_field):
        """Constructor.

        :param target_field: dot separated path where to dump the tokens.
        """
        super().__init__()
        self.keys = parse_lookup_key(target_field)
        self.key = self.keys[-1]

    def dump(self, record, data):
        """Dump the download & view statistics to the data dictionary."""
        if record.is_draft:
            return

        recid = record.pid.pid_value
        parent_recid = record.parent.pid.pid_value

        try:
            parent_data = dict_lookup(data, self.keys, parent=True)
            parent_data[self.key] = Statistics.get_record_stats(
                recid=recid, parent_recid=parent_recid
            )
        except KeyError as e:
            current_app.logger.warning(e)

    def load(self, data, record_cls):
        """Keep the download & view statistics in the data dictionary.

        This is relevant for the "RecordStatisticsField" system field,
        which uses this entry in the record's data.
        """
        pass
