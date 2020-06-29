# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM records celery tasks."""

from invenio_db import db
from invenio_records_files.api import Record
from invenio_records_files.models import RecordsBuckets


def update_record_files_by_bucket(bucket_id):
    """Given a bucket id, dump its files in the record metadata."""
    record_bucket = \
        RecordsBuckets.query.filter_by(bucket_id=bucket_id).first()
    if record_bucket:
        record = Record.get_record(record_bucket.record_id)
        record.files.flush()
        record.commit()
        # it might fail with `sqlalchemy.orm.exc.StaleDataError`
        # if another task is updating the record at the same time.
        # The exception might be ignored because one of the task will
        # anyway update the record metadata with the entire content
        # of the bucket.
        db.session.commit()


def update_record_files_async(object_version):
    """Get the bucket id and spawn a task to update record metadata."""
    # convert to string to be able to serialize it when sending to the task
    str_uuid = str(object_version.bucket_id)
    return update_record_files_by_bucket(bucket_id=str_uuid)
