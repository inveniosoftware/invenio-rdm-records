import io
from flask import current_app
from celery import shared_task
from pypdf import PdfReader
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service


@shared_task(ignore_result=True)
def extract_full_text(record_id, file_key):
    """Extract full text."""
    record = current_rdm_records_service.record_cls.pid.resolve(record_id)
    status_file = record.media_files[f"{file_key}.txt"]
    status_file.processor["status"] = "processing"
    status_file.commit()
    db.session.commit()
    try:
        with record.files[file_key].open_stream("rb") as fd:
            reader = PdfReader(fd)
            data = "\n".join(p.extract_text() for p in reader.pages).encode()
            status_file.object_version.file.set_contents(io.BytesIO(data))
            # When using init_contents on the processor readable is False
            status_file.object_version.file.readable = True
            status_file.processor["status"] = "finished"
    except Exception as ex:
        current_app.logger.exception("Full text extraction failed.")
        status_file.processor["status"] = "failed"
        raise ex
    finally:
        status_file.commit()
        db.session.commit()