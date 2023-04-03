# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio RDM Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permission factories for Invenio-Stats.

In contrast to the very liberal defaults provided by Invenio-Stats, these permission
factories deny access unless otherwise specified.
"""

from flask import current_app
from invenio_stats.proxies import current_stats


class Statistics:
    """Statistics API class."""

    @classmethod
    def _get_query(cls, query_name):
        """Build the statistics query from configuration."""
        query_config = current_stats.queries[query_name]
        return query_config.cls(name=query_config.name, **query_config.params)

    @classmethod
    def get_record_stats(cls, recid, parent_recid):
        """Fetch the statistics for the given record."""
        try:
            views = cls._get_query("record-view").run(recid=recid)
            views_all = cls._get_query("record-view-all-versions").run(
                parent_recid=parent_recid
            )
        except Exception as e:
            # e.g. opensearchpy.exceptions.NotFoundError
            # when the aggregation search index hasn't been created yet
            current_app.logger.warning(e)

            fallback_result = {
                "views": 0,
                "unique_views": 0,
            }
            views = views_all = downloads = downloads_all = fallback_result

        try:
            downloads = cls._get_query("record-download").run(recid=recid)
            downloads_all = cls._get_query("record-download-all-versions").run(
                parent_recid=parent_recid
            )
        except Exception as e:
            # same as above, but for failure in the download statistics
            # because they are a separate index that can fail independently
            current_app.logger.warning(e)

            fallback_result = {
                "downloads": 0,
                "unique_downloads": 0,
                "data_volume": 0,
            }
            downloads = downloads_all = fallback_result

        stats = {
            "this_version": {
                "views": views["views"],
                "unique_views": views["unique_views"],
                "downloads": downloads["downloads"],
                "unique_downloads": downloads["unique_downloads"],
                "data_volume": downloads["data_volume"],
            },
            "all_versions": {
                "views": views_all["views"],
                "unique_views": views_all["unique_views"],
                "downloads": downloads_all["downloads"],
                "unique_downloads": downloads_all["unique_downloads"],
                "data_volume": downloads_all["data_volume"],
            },
        }

        return stats
