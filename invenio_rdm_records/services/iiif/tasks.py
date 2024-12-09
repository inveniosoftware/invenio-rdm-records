# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tasks for statistics."""

from celery import shared_task
from invenio_db import db

from invenio_rdm_records.proxies import current_rdm_records_service

from .storage import tiles_storage


@shared_task(ignore_result=True)
def generate_tiles(record_id, file_key, file_type):
    """Generate pyramidal TIFF."""
    record = current_rdm_records_service.record_cls.pid.resolve(record_id)
    status_file = record.media_files[file_key + ".ptif"]
    status_file.processor["status"] = "processing"
    status_file.commit()
    db.session.commit()

    conversion_state = tiles_storage.save(record, file_key, file_type)

    status_file.processor["status"] = "finished" if conversion_state else "failed"
    status_file.file.file_model.uri = str(
        tiles_storage._get_file_path(record, file_key)
    )
    status_file.commit()
    db.session.commit()


@shared_task(
    ignore_result=True,
    max_retries=4,
    retry_backoff=10 * 60,
)
def cleanup_tiles_file(record_id, tile_file_key, retry=True):
    """Cleanup pyramidal TIFF."""
    try:
        record = current_rdm_records_service.record_cls.pid.resolve(record_id)

        deletion_status = tiles_storage.delete(record, tile_file_key[: -len(".ptif")])
        if deletion_status:
            mf = record.media_files.get(tile_file_key)
            fi = mf.file.file_model
            record.media_files.delete(
                tile_file_key, softdelete_obj=False, remove_rf=True
            )
            fi.delete()
        db.session.commit()
    except Exception as exc:
        if retry:
            cleanup_tiles_file.retry(exc=exc)
        else:
            raise exc
