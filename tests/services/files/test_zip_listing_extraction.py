# SPDX-FileCopyrightText: 2025 CESNET i.a.l.e.
# SPDX-License-Identifier: MIT

"""Test RDM records files (metadata)."""

import io
import sys
import zipfile
from pathlib import Path
from unittest.mock import ANY, MagicMock, call

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.files.service import FileService
from sqlalchemy.exc import NoResultFound

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services import tasks as file_tasks
from invenio_rdm_records.services.components import (
    RDMFileProcessorComponent,
)
from invenio_rdm_records.services.components import files as file_processor_module


def test_file_processor_queues_rdm_extraction(monkeypatch):
    """Queue the RDM-specific metadata extraction task."""
    service = MagicMock()
    uow = MagicMock()
    registry = MagicMock()
    registry.get_service_id.return_value = "draft-files"
    component = RDMFileProcessorComponent(service)
    component.uow = uow
    monkeypatch.setattr(file_processor_module, "current_service_registry", registry)

    component.commit_file(None, "record-id", "test.zip", None)

    operation = uow.register.call_args.args[0]
    assert operation._celery_task is file_tasks.extract_rdm_file_metadata
    assert operation._args == ("draft-files", "record-id", "test.zip")


@pytest.mark.parametrize(
    ("service_id", "fallback_service_id", "error"),
    [
        ("draft-files", "files", NoResultFound()),
        (
            "draft-media-files",
            "media-files",
            PIDDoesNotExistError("recid", "record-id"),
        ),
    ],
)
def test_rdm_extraction_uses_published_fallback(
    service_id, fallback_service_id, error, monkeypatch
):
    """Retry through the matching published service when the draft is gone."""
    draft_service = MagicMock()
    draft_service.extract_file_metadata.side_effect = error
    published_service = MagicMock()
    registry = MagicMock()
    registry.get.side_effect = {
        service_id: draft_service,
        fallback_service_id: published_service,
    }.get
    monkeypatch.setattr(file_tasks, "current_service_registry", registry)

    file_tasks.extract_rdm_file_metadata(service_id, "record-id", "test.zip")

    assert registry.get.call_args_list == [call(service_id), call(fallback_service_id)]
    published_service.extract_published_file_metadata.assert_called_once_with(
        ANY, "record-id", "test.zip"
    )


def test_rdm_extraction_logs_file_context(monkeypatch):
    """Log the affected file and original processor error."""
    service = MagicMock()
    service.extract_file_metadata.side_effect = RuntimeError("processor failed")
    registry = MagicMock()
    registry.get.return_value = service
    app = MagicMock()
    monkeypatch.setattr(file_tasks, "current_service_registry", registry)
    monkeypatch.setattr(file_tasks, "current_app", app)

    file_tasks.extract_rdm_file_metadata("draft-files", "record-id", "test.zip")

    app.logger.exception.assert_called_once_with(
        "Failed to extract file metadata. service_id=%s record_id=%s "
        "file_key=%s exception_type=%s exception=%s",
        "draft-files",
        "record-id",
        "test.zip",
        "RuntimeError",
        service.extract_file_metadata.side_effect,
    )


@pytest.mark.skipif(
    not hasattr(FileService, "extract_published_file_metadata"),
    reason="Requires invenio-records-resources#702",
)
def test_rdm_extraction_after_draft_publication(
    running_app,
    db,
    location,
    minimal_record,
    identity_simple,
    search_clear,
    monkeypatch,
):
    """Extract metadata when publication finishes before the queued task."""
    queued_task = MagicMock()
    monkeypatch.setattr(
        "invenio_rdm_records.services.components.files.extract_rdm_file_metadata",
        queued_task,
    )
    service = current_rdm_records_service
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    draft = service.create(identity_simple, data)

    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[{"key": "test.zip", "metadata": {}, "access": {"hidden": False}}],
    )
    zip_path = Path(__file__).parent.parent / "data" / "test_zip.zip"
    with open(zip_path, "rb") as fp:
        service.draft_files.set_file_content(identity_simple, draft.id, "test.zip", fp)

    service.draft_files.commit_file(identity_simple, draft.id, "test.zip")
    assert queued_task.apply_async.called
    service.publish(identity_simple, draft.id)

    file_tasks.extract_rdm_file_metadata(
        *queued_task.apply_async.call_args.kwargs["args"]
    )

    file_item = service.files.read_file_metadata(identity_simple, draft.id, "test.zip")
    assert isinstance(file_item.data["metadata"]["zip_toc_position"], int)


def test_zip_file_listing(
    running_app, db, location, minimal_record, identity_simple, search_clear
):
    """Test setting file metadata."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    file_service = service.files

    # Create
    draft = service.create(identity_simple, data)

    # Initialize files and add valid metadata
    metadata = {
        "type": "zip",
    }
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[{"key": "test.zip", "metadata": metadata, "access": {"hidden": False}}],
    )

    zip_path = Path(__file__).parent.parent / "data" / "test_zip.zip"
    with open(zip_path, "rb") as f:
        service.draft_files.set_file_content(identity_simple, draft.id, "test.zip", f)

    service.draft_files.commit_file(identity_simple, draft.id, "test.zip")

    # Publish the record
    record = service.publish(identity_simple, draft.id)

    # Get file metadata
    listing = file_service.list_container(identity_simple, draft.id, "test.zip")
    assert listing.to_dict() == {
        "entries": [
            {
                "key": "test_zip/test1.txt",
                "size": 12,
                "compressed_size": 14,
                "mimetype": "text/plain",
                "crc": 2962613731,
                "links": {
                    "content": f"https://127.0.0.1:5000/api/records/{draft.id}/files/test.zip/container/test_zip/test1.txt"
                },
            }
        ],
        "truncated": False,
        "total": 1,
        "directories": [
            {
                "key": "test_zip",
                "links": {
                    "content": f"https://127.0.0.1:5000/api/records/{draft.id}/files/test.zip/container/test_zip"
                },
                "entries": ["test_zip/test1.txt"],
            }
        ],
    }


def test_zip_file_extraction(
    running_app, db, location, minimal_record, identity_simple, search_clear
):
    """Test setting file metadata."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    file_service = service.files

    # Create
    draft = service.create(identity_simple, data)

    # Initialize files and add valid metadata
    metadata = {
        "type": "zip",
    }
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[{"key": "test.zip", "metadata": metadata, "access": {"hidden": False}}],
    )

    zip_path = Path(__file__).parent.parent / "data" / "test_zip.zip"
    with open(zip_path, "rb") as f:
        service.draft_files.set_file_content(identity_simple, draft.id, "test.zip", f)

    service.draft_files.commit_file(identity_simple, draft.id, "test.zip")

    # Publish the record
    record = service.publish(identity_simple, draft.id)

    extracted = file_service.extract_container_item(
        identity_simple, draft.id, "test.zip", "test_zip/test1.txt"
    )
    res = extracted.send_file()
    data = b"".join(res.response)
    assert res.mimetype == "text/plain"
    assert len(data) == 12
    assert data == b"Hello World\n"


def test_zip_folder_extraction(
    running_app, db, location, minimal_record, identity_simple, search_clear
):
    """Test setting file metadata."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    file_service = service.files

    # Create
    draft = service.create(identity_simple, data)

    # Initialize files and add valid metadata
    metadata = {
        "type": "zip",
    }
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[
            {
                "key": "test_directory_zip.zip",
                "metadata": metadata,
                "access": {"hidden": False},
            }
        ],
    )

    zip_path = Path(__file__).parent.parent / "data" / "test_directory_zip.zip"
    with open(zip_path, "rb") as f:
        service.draft_files.set_file_content(
            identity_simple, draft.id, "test_directory_zip.zip", f
        )

    service.draft_files.commit_file(identity_simple, draft.id, "test_directory_zip.zip")

    # Publish the record
    record = service.publish(identity_simple, draft.id)

    extracted = file_service.extract_container_item(
        identity_simple,
        draft.id,
        "test_directory_zip.zip",
        "test_directory_zip/directory1",
    )
    res = extracted.send_file()
    data = b"".join(res.response)
    zip_bytes = io.BytesIO(data)
    with zipfile.ZipFile(zip_bytes, "r") as zip_ref:
        namelist = zip_ref.namelist()
        assert namelist == ["directory1-file1.txt", "directory1-file2.txt"]

        with zip_ref.open("directory1-file1.txt") as f:
            content = f.read().decode("utf-8")
            assert content == "directory1-file1\n"

        with zip_ref.open("directory1-file2.txt") as f:
            content = f.read().decode("utf-8")
            assert content == "directory1-file2\n"


@pytest.mark.skipif(sys.version_info < (3, 11), reason="Requires Python 3.11+")
def test_large_zip_folder_extraction(
    running_app, db, location, minimal_record, identity_simple, search_clear
):
    """Test extracting a folder from a large in-memory zip file."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service
    file_service = service.files

    # Create draft
    draft = service.create(identity_simple, data)

    # Prepare metadata
    metadata = {"type": "zip"}
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[
            {
                "key": "big_test_zip.zip",
                "metadata": metadata,
                "access": {"hidden": False},
            }
        ],
    )

    # Create a large zip in memory for simplicity
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Create multiple nested directories and files
        for i in range(5):  # top-level directories
            zipf.mkdir(f"folder_{i}/")
            for j in range(10):  # subdirectories
                folder_path = f"folder_{i}/subfolder_{j}/"
                zipf.mkdir(folder_path)
                for k in range(20):  # files in each subfolder
                    file_name = f"file_{k}.txt"
                    content = f"This is file {k} in {folder_path}".encode("utf-8")
                    zipf.writestr(folder_path + file_name, content)

    zip_buffer.seek(0)

    # Upload ZIP as file content
    service.draft_files.set_file_content(
        identity_simple, draft.id, "big_test_zip.zip", zip_buffer
    )

    service.draft_files.commit_file(identity_simple, draft.id, "big_test_zip.zip")

    # Publish
    record = service.publish(identity_simple, draft.id)

    # Extract a specific folder from the zip
    extracted = file_service.extract_container_item(
        identity_simple,
        draft.id,
        "big_test_zip.zip",
        "folder_3/subfolder_7",  # some folder to extract
    )

    # Read the returned zip data
    res = extracted.send_file()
    data = b"".join(res.response)
    zip_bytes = io.BytesIO(data)

    # Verify extracted folder content
    with zipfile.ZipFile(zip_bytes, "r") as zip_ref:
        names = sorted(zip_ref.namelist())
        assert len(names) == 20  # we added 20 files
        # Check one file’s content
        with zip_ref.open("file_0.txt") as f:
            content = f.read().decode("utf-8")
            assert "folder_3/subfolder_7" in content


def test_zip_listing_resource(
    running_app, db, location, minimal_record, identity_simple, client, search_clear
):
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    file_service = service.files

    # Create
    draft = service.create(identity_simple, data)

    # Initialize files and add valid metadata
    metadata = {
        "type": "zip",
    }
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[{"key": "test.zip", "metadata": metadata, "access": {"hidden": False}}],
    )

    zip_path = Path(__file__).parent.parent / "data" / "test_zip.zip"
    with open(zip_path, "rb") as f:
        service.draft_files.set_file_content(identity_simple, draft.id, "test.zip", f)

    service.draft_files.commit_file(identity_simple, draft.id, "test.zip")

    # Publish the record
    record = service.publish(identity_simple, draft.id)

    res = client.get(
        f"/records/{draft.id}/files/test.zip/container",
        headers={
            "content-type": "application/json",
        },
    )
    assert res.status_code == 200
    assert res.json == {
        "entries": [
            {
                "key": "test_zip/test1.txt",
                "size": 12,
                "compressed_size": 14,
                "mimetype": "text/plain",
                "crc": 2962613731,
                "links": {
                    "content": f"https://127.0.0.1:5000/api/records/{draft.id}/files/test.zip/container/test_zip/test1.txt"
                },
            }
        ],
        "truncated": False,
        "total": 1,
        "directories": [
            {
                "key": "test_zip",
                "links": {
                    "content": f"https://127.0.0.1:5000/api/records/{draft.id}/files/test.zip/container/test_zip"
                },
                "entries": ["test_zip/test1.txt"],
            }
        ],
    }


def test_zip_file_extract_resource(
    running_app, db, location, minimal_record, identity_simple, client, search_clear
):
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    file_service = service.files

    # Create
    draft = service.create(identity_simple, data)

    # Initialize files and add valid metadata
    metadata = {
        "type": "zip",
    }
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[
            {
                "key": "test_directory_zip.zip",
                "metadata": metadata,
                "access": {"hidden": False},
            }
        ],
    )

    zip_path = Path(__file__).parent.parent / "data" / "test_directory_zip.zip"
    with open(zip_path, "rb") as f:
        service.draft_files.set_file_content(
            identity_simple, draft.id, "test_directory_zip.zip", f
        )

    service.draft_files.commit_file(identity_simple, draft.id, "test_directory_zip.zip")

    # Publish the record
    record = service.publish(identity_simple, draft.id)

    res = client.get(
        f"/records/{draft.id}/files/test_directory_zip.zip/container/test_directory_zip/directory1/directory1-file1.txt",
        headers={
            "content-type": "application/json",
        },
    )
    assert res.status_code == 200
    assert res.data == b"directory1-file1\n"


def test_zip_folder_extract_resource(
    running_app, db, location, minimal_record, identity_simple, client, search_clear
):
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    service = current_rdm_records_service

    file_service = service.files

    # Create
    draft = service.create(identity_simple, data)

    # Initialize files and add valid metadata
    metadata = {
        "type": "zip",
    }
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[
            {
                "key": "test_directory_zip.zip",
                "metadata": metadata,
                "access": {"hidden": False},
            }
        ],
    )

    zip_path = Path(__file__).parent.parent / "data" / "test_directory_zip.zip"
    with open(zip_path, "rb") as f:
        service.draft_files.set_file_content(
            identity_simple, draft.id, "test_directory_zip.zip", f
        )

    service.draft_files.commit_file(identity_simple, draft.id, "test_directory_zip.zip")

    # Publish the record
    record = service.publish(identity_simple, draft.id)

    res = client.get(
        f"/records/{draft.id}/files/test_directory_zip.zip/container/test_directory_zip/directory1",
        headers={
            "content-type": "application/json",
        },
    )
    assert res.status_code == 200

    zip_bytes = io.BytesIO(res.data)
    with zipfile.ZipFile(zip_bytes, "r") as zip_ref:
        namelist = zip_ref.namelist()
        assert namelist == ["directory1-file1.txt", "directory1-file2.txt"]

        with zip_ref.open("directory1-file1.txt") as f:
            content = f.read().decode("utf-8")
            assert content == "directory1-file1\n"

        with zip_ref.open("directory1-file2.txt") as f:
            content = f.read().decode("utf-8")
            assert content == "directory1-file2\n"
