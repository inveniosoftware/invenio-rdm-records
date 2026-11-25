# SPDX-FileCopyrightText: 2026 CERN
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests that we are calling `db.session.commit()` before datacite http calls
so that the connection goes back to the pool.
"""

from unittest.mock import MagicMock, patch

from invenio_pidstore.models import PIDStatus
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.pids.tasks import register_or_update_pid
from tests.fake_datacite_client import FakeDataCiteRESTClient


class TransactionProbe:
    """"""

    DML = ("SELECT", "INSERT", "UPDATE", "DELETE")

    def __init__(self, engine):
        """Create a probe for ``engine``."""
        self._engine = engine
        self.log = []  # ("sql", statement) | ("end", "after_commit"|"after_rollback")

    def _on_sql(self, conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().split(None, 1)[0].upper() in self.DML:
            self.log.append(("sql", statement))

    def _on_commit(self, session):
        self.log.append(("end", "after_commit"))

    def _on_rollback(self, session):
        self.log.append(("end", "after_rollback"))

    def __enter__(self):
        """Attach the listeners."""
        event.listen(self._engine, "before_cursor_execute", self._on_sql)
        # Session-level events fire on session.commit/rollback the calls
        # that release the connection in production but not for inner
        # `with db.session.begin_nested` blocks, which do not release it
        event.listen(Session, "after_commit", self._on_commit)
        event.listen(Session, "after_rollback", self._on_rollback)
        return self

    def __exit__(self, *exc):
        """Detach the listeners."""
        event.remove(self._engine, "before_cursor_execute", self._on_sql)
        event.remove(Session, "after_commit", self._on_commit)
        event.remove(Session, "after_rollback", self._on_rollback)


def test_register_or_update_does_not_hold_db_connection_while_http_request(
    db,
    running_app,
    search_clear,
    full_record,
    superuser_identity,
    mock_datacite_client,
):
    # Same as test_full_record_register
    full_record["pids"] = {}
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, full_record)
    draft = service.pids.create(superuser_identity, draft.id, "doi")
    doi = draft["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    record = service.record_cls.publish(draft._record)
    record.pids = {pid.pid_type: {"identifier": pid.pid_value, "provider": "datacite"}}
    record.metadata = draft["metadata"]
    record.register()
    record.commit()
    assert pid.status == PIDStatus.NEW
    pid.reserve()
    assert pid.status == PIDStatus.RESERVED

    at_call = {}

    def public_doi_probe(*args, **kwargs):
        at_call["log"] = list(probe.log)
        return MagicMock()

    # The faked http request is done at `FakeDataCiteRESTClient.public_doi`
    # so we are going to check the logs at that point.
    with (
        TransactionProbe(db.engine) as probe,
        patch.object(
            FakeDataCiteRESTClient, "public_doi", side_effect=public_doi_probe
        ),
    ):
        register_or_update_pid(recid=record["id"], scheme="doi")

    assert "log" in at_call, "POST was never called"
    assert at_call["log"][-1] == (
        "end",
        "after_commit",
    ), "http conneciton while db connection"

    # Clear current log
    at_call = {}

    # Run again to check update path at `FakeDataCiteRESTClient.update`
    with (
        TransactionProbe(db.engine) as probe,
        patch.object(
            FakeDataCiteRESTClient, "update_doi", side_effect=public_doi_probe
        ),
    ):
        register_or_update_pid(recid=record["id"], scheme="doi")

    assert "log" in at_call, "POST was never called"
    assert at_call["log"][-1] == (
        "end",
        "after_commit",
    ), "http conneciton while db connection"

    # Clear current log
    at_call = {}

    # Run again to check update with hidden record
    record.access.protection.record = "restricted"
    record.commit()
    with (
        TransactionProbe(db.engine) as probe,
        patch.object(FakeDataCiteRESTClient, "hide_doi", side_effect=public_doi_probe),
    ):
        register_or_update_pid(recid=record["id"], scheme="doi")

    assert "log" in at_call, "POST was never called"
    assert at_call["log"][-1] == (
        "end",
        "after_commit",
    ), "http conneciton while db connection"


def test_delete_and_restore_does_not_hold_db_connection_while_http_request(
    db,
    running_app,
    search_clear,
    minimal_record,
    mocker,
    superuser_identity,
    mock_datacite_client,
):
    # Same as test_restore_pid
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)
    doi = record["pids"]["doi"]["identifier"]
    parent_doi = record["parent"]["pids"]["doi"]["identifier"]
    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)
    assert pid.status == PIDStatus.REGISTERED
    parent_provider = service.pids.parent_pid_manager._get_provider("doi", "datacite")
    parent_pid = parent_provider.get(pid_value=parent_doi)
    assert parent_pid.status == PIDStatus.REGISTERED
    tombstone_info = {"note": "no specific reason, tbh"}

    at_call = {}

    def restore_probe(*args, **kwargs):
        at_call["log"] = list(probe.log)
        return MagicMock()

    # The faked http request is done at `FakeDataCiteRESTClient.hide_doi`
    # so we are going to check the logs at that point.
    with (
        TransactionProbe(db.engine) as probe,
        patch.object(FakeDataCiteRESTClient, "hide_doi", side_effect=restore_probe),
    ):
        record = service.delete_record(
            superuser_identity, id_=record.id, data=tombstone_info
        )
    assert "log" in at_call, "POST was never called"
    assert at_call["log"][-1] == (
        "end",
        "after_commit",
    ), "http conneciton while db connection"

    # Restore the one we just deleted.
    at_call = {}
    with (
        TransactionProbe(db.engine) as probe,
        patch.object(FakeDataCiteRESTClient, "show_doi", side_effect=restore_probe),
    ):
        service.restore_record(superuser_identity, record.id)

    assert "log" in at_call, "POST was never called"
    assert at_call["log"][-1] == (
        "end",
        "after_commit",
    ), "http conneciton while db connection"
