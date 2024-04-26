# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# ZenodoRDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tasks for statistics."""

from celery import shared_task
from invenio_db import db

from invenio_rdm_records.proxies import current_rdm_records_service

from .utils import LocalTilesStorage

tif_store = LocalTilesStorage(base_path="/iiif/images")


@shared_task(
    ignore_result=True,
)
def generate_zoomable_image(record_id, file_key, params=None):
    """Generate pyramidal tiff."""
    record = current_rdm_records_service.record_cls.pid.resolve(record_id)
    status_file = record.media_files[file_key + ".ptif"]
    status_file["processor"]["status"] = "processing"
    status_file.commit()
    db.session.commit()

    conversion_state = tif_store.save(record, file_key)

    status_file["processor"]["status"] = "finished" if conversion_state else "failed"
    status_file.commit()
    db.session.commit()
