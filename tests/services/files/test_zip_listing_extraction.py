# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CESNET i.a.l.e.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test RDM records files (metadata)."""

import io
import time
import zipfile
from pathlib import Path

import psutil

from invenio_rdm_records.proxies import current_rdm_records_service


def test_zip_file_listing(
    running_app, db, location, minimal_record, identity_simple, search_clear
):
    """Test setting file metadata."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    data["media_files"] = {"enabled": True}
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
        "children": {
            "test_zip": {
                "children": {
                    "test1.txt": {
                        "key": "test1.txt",
                        "type": "file",
                        "id": "test_zip/test1.txt",
                        "size": 12,
                        "compressed_size": 14,
                        "mime_type": "text/plain",
                        "crc": 2962613731,
                        "links": {
                            "content": f"https://127.0.0.1:5000/api/records/{draft.id}/files/test.zip/container/test_zip/test1.txt",
                        },
                    }
                },
                "key": "test_zip",
                "id": "test_zip",
                "type": "folder",
                "links": {
                    "content": f"https://127.0.0.1:5000/api/records/{draft.id}/files/test.zip/container/test_zip"
                },
            }
        },
        "total": 1,
        "truncated": False,
    }


def test_zip_file_extraction(
    running_app, db, location, minimal_record, identity_simple, search_clear
):
    """Test setting file metadata."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    data["media_files"] = {"enabled": True}
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

    extracted = file_service.extract_from_container(
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
    data["media_files"] = {"enabled": True}
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

    extracted = file_service.extract_from_container(
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


def test_large_zip_folder_extraction(
    running_app, db, location, minimal_record, identity_simple, search_clear
):
    """Test extracting a folder from a large in-memory zip file."""
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    data["media_files"] = {"enabled": True}
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
        zipf.writestr("big_test_zip/", "")

        # Create multiple nested folders and files
        for i in range(5):  # top-level folders
            for j in range(10):  # subfolders
                for k in range(20):  # files in each subfolder
                    folder_path = f"folder_{i}/subfolder_{j}/"
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
    extracted = file_service.extract_from_container(
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


def test_large_zip_memory_usage(
    running_app, db, location, minimal_record, identity_simple, search_clear
):
    """Test that ZIP extraction is memory efficient."""
    import gc
    import os

    process = psutil.Process(os.getpid())

    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    data["media_files"] = {"enabled": True}
    service = current_rdm_records_service
    file_service = service.files

    draft = service.create(identity_simple, data)
    metadata = {"type": "zip"}
    service.draft_files.init_files(
        identity_simple,
        draft.id,
        data=[
            {"key": "huge_test.zip", "metadata": metadata, "access": {"hidden": False}}
        ],
    )

    # Create a large zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("huge_test/", "")
        # Add a few large files
        for i in range(10):
            zipf.writestr(f"huge_test/largefile_{i}.bin", b"x" * 50_000_000)
    zip_buffer.seek(0)

    service.draft_files.set_file_content(
        identity_simple, draft.id, "huge_test.zip", zip_buffer
    )
    service.draft_files.commit_file(identity_simple, draft.id, "huge_test.zip")
    record = service.publish(identity_simple, draft.id)

    # Measure memory before extraction
    gc.collect()
    mem_before = process.memory_info().rss

    # Perform extraction
    extracted = file_service.extract_from_container(
        identity_simple,
        draft.id,
        "huge_test.zip",
        "huge_test",  # entire zip
    )
    res = extracted.send_file()

    # Read in streaming chunks
    data_stream = io.BytesIO()

    # Track maximum instantaneous memory usage during streaming
    max_mem_usage = mem_before

    for chunk in res.response:
        # force freeing objects accumulated in previous iteration
        gc.collect()

        mem_before_chunk = process.memory_info().rss

        # write chunk to output buffer
        data_stream.write(chunk)
        # simulate some delay and measure periodically
        time.sleep(0.01)

        mem_after_chunk = process.memory_info().rss
        # track peak
        if mem_after_chunk > max_mem_usage:
            max_mem_usage = mem_after_chunk

        print(
            f"Chunk size={len(chunk)}, "
            f"mem_before_chunk={mem_before_chunk / 1e6:.1f} MB, "
            f"mem_after_chunk={mem_after_chunk / 1e6:.1f} MB"
        )

    gc.collect()
    mem_after = process.memory_info().rss
    mem_diff_mb = (mem_after - mem_before) / (1024 * 1024)
    peak_diff_mb = (max_mem_usage - mem_before) / (1024 * 1024)

    print(
        f"Total memory before: {mem_before / 1e6:.1f} MB, "
        f"after: {mem_after / 1e6:.1f} MB, "
        f"diff: {mem_diff_mb:.2f} MB"
    )
    print(f"Peak memory usage increase during streaming: {peak_diff_mb:.2f} MB")

    # Check memory growth is reasonable (<100 MB)
    assert peak_diff_mb < 100, f"Extraction used too much memory: {peak_diff_mb:.2f} MB"


def test_zip_listing_resource(
    running_app, db, location, minimal_record, identity_simple, client, search_clear
):
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    data["media_files"] = {"enabled": True}
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
        "children": {
            "test_zip": {
                "children": {
                    "test1.txt": {
                        "key": "test1.txt",
                        "type": "file",
                        "id": "test_zip/test1.txt",
                        "size": 12,
                        "compressed_size": 14,
                        "mime_type": "text/plain",
                        "crc": 2962613731,
                        "links": {
                            "content": f"https://127.0.0.1:5000/api/records/{draft.id}/files/test.zip/container/test_zip/test1.txt",
                        },
                    }
                },
                "key": "test_zip",
                "id": "test_zip",
                "type": "folder",
                "links": {
                    "content": f"https://127.0.0.1:5000/api/records/{draft.id}/files/test.zip/container/test_zip"
                },
            }
        },
        "total": 1,
        "truncated": False,
    }


def test_zip_file_extract_resource(
    running_app, db, location, minimal_record, identity_simple, client, search_clear
):
    data = minimal_record.copy()
    data["files"] = {"enabled": True}
    data["media_files"] = {"enabled": True}
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
    data["media_files"] = {"enabled": True}
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
