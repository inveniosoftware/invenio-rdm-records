# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Cached transient field for record statistics."""

from invenio_records.systemfields import SystemField
from invenio_search.proxies import current_search_client
from invenio_search.utils import build_alias_name

from ..stats import Statistics


class RecordStatisticsField(SystemField):
    """Field for lazy fetching and caching (but not storing) of record statistics."""

    def _get_record_stats(self, record):
        """Get the record's statistics from either record or aggregation index."""
        stats = None
        recid, parent_recid = record["id"], record.parent["id"]

        try:
            # for more consistency between search results and each record's details,
            # we try to get the statistics from the record's search index first
            # note: this field is dumped into the record's data before indexing
            #       by the search dumper extension "StatisticsDumperExt"
            res = current_search_client.get(
                index=build_alias_name(record.index._name),
                id=record.id,
                params={"_source_includes": "stats"},
            )
            stats = res["_source"]["stats"]
        except Exception:
            stats = None

        # as a fallback, use the more up-to-date aggregations indices
        return stats or Statistics.get_record_stats(
            recid=recid, parent_recid=parent_recid
        )

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the persistent identifier."""
        if record is None:
            # returns the field itself.
            return self

        stats = record.get("stats", None)
        if stats:
            return stats

        stats = self._get_record_stats(record)
        record["stats"] = stats

        return stats

    def pre_commit(self, record, **kwargs):
        """Ensure that the statistics stay transient."""
        record.pop("stats", None)

    def pre_dump(self, record, data, **kwargs):
        """Do nothing in particular before a record is dumped."""
        # note: there's no pre/post-dump work being done in the system field because
        #       we only want the stats to be dumped into the search engine, which is
        #       done over at the "StatisticsDumperExt" search dumper extension
        #       putting that logic here would require more research into when a
        #       system field's `pre_dump()` is called
        pass
