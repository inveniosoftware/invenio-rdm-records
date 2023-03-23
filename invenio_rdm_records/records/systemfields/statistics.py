# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Cached transient field for record statistics."""

from invenio_records.systemfields import SystemField

from ...stats.utils import get_record_stats


class RecordStatisticsField(SystemField):
    """Field for lazy fetching and caching (but not storing) of record statistics."""

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

        recid = record["id"]
        parent_recid = record.parent["id"]
        stats = get_record_stats(recid=recid, parent_recid=parent_recid)
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
