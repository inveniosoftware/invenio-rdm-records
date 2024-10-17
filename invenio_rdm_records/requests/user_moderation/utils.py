# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM user moderation utilities."""

from invenio_db import db
from invenio_search.api import RecordsSearchV2

from ...proxies import current_rdm_records_service


def get_user_records(user_id, from_db=False, status=None):
    """Helper function for getting all the records of the user."""
    record_cls = current_rdm_records_service.record_cls
    model_cls = record_cls.model_cls
    parent_cls = record_cls.parent_record_cls
    parent_model_cls = parent_cls.model_cls

    if from_db:
        query = (
            db.session.query(model_cls.json["id"].as_string())
            .join(parent_model_cls)
            .filter(
                parent_model_cls.json["access"]["owned_by"]["user"].as_string()
                == str(user_id),
            )
        )
        if status:
            query = query.filter(model_cls.deletion_status.in_(status))

        return (row[0] for row in query.yield_per(1000))
    else:
        search = (
            RecordsSearchV2(index=record_cls.index._name)
            .filter("term", **{"parent.access.owned_by.user": user_id})
            .source(["id"])
        )
        if status:
            if not isinstance(status, (tuple, list)):
                status = [status]
            status = [s.value for s in status]
            search = search.filter("terms", deletion_status=status)
        return (hit["id"] for hit in search.scan())
