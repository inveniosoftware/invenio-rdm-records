# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

import re
from contextlib import contextmanager

import pytest
from invenio_github.models import Release, ReleaseStatus, Repository
from invenio_vcs.contrib.github import GitHubProviderFactory
from invenio_vcs.contrib.gitlab import GitLabProviderFactory
from sqlalchemy import event

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.github.release import RDMGithubRelease
from invenio_rdm_records.services.vcs.release import RDMVCSRelease


@contextmanager
def count_queries(db):
    """Context manager that counts the amount of queries done."""
    s = []

    def _record(conn, cursor, statement, parameters, context, excutemany):
        s.append(statement)

    event.listen(db.engine, "before_cursor_execute", _record)
    try:
        yield s
    finally:
        event.remove(db.engine, "before_cursor_execute", _record)


@pytest.fixture()
def published_record(running_app, minimal_record, search_clear):
    """Published record fixture."""
    service = current_rdm_records_service
    identity = running_app.superuser_identity
    draft = service.create(identity, minimal_record)
    return service.publish(identity, draft.id)._record


@pytest.fixture()
def github_release(db, running_app, published_record, uploader):
    """Published GitHub release poiting at a published record"""
    repo = Repository(github_id=424242, name="owner/repo", user_id=uploader.id)
    release = Release(
        release_id=1,
        tag="v1.0",
        repository=repo,
        record_id=published_record.id,
        status=ReleaseStatus.PUBLISHED,
    )
    db.session.add_all([repo, release])
    db.session.commit()
    # Session refresh here prevents the `count_queries` from
    # counting this as part of the test.
    db.session.refresh(release)
    return release


@pytest.fixture()
def github_provider_for_vcs():
    return GitHubProviderFactory(
        base_url="https://github.com",
        webhook_receiver_url="http://localhost:5000/api/receivers/github/events/?access_token={token}",
    )


@pytest.fixture()
def gitlab_provider_for_vcs():
    return GitLabProviderFactory(
        base_url="https://gitlab.com",
        webhook_receiver_url="http://localhost:5000/api/receivers/gitlab/events/?access_token={token}",
    )


@pytest.mark.parametrize(
    "provider",
    [
        (gitlab_provider_for_vcs),
        (github_provider_for_vcs),
    ],
)
def test_badge_value_query_count_vcs(db, github_release, provider, published_record):
    doi = published_record["pids"]["doi"]["identifier"]
    with count_queries(db) as statements:
        badge_value = RDMVCSRelease(github_release, provider).badge_value

    # len(statements) was 110 before the change to `badge_value`
    assert len(statements) == 1
    assert badge_value == doi

    pattern = r"10\.1234/[a-z0-9\-]{1,12}"
    assert re.fullmatch(pattern, badge_value) is not None


def test_badge_value_query_count(db, github_release, published_record):
    """Regression test: `badge_value` stays at one query."""
    doi = published_record["pids"]["doi"]["identifier"]
    with count_queries(db) as statements:
        badge_value = RDMGithubRelease(github_release).badge_value

    # len(statements) was 112 before the change to `badge_value`
    assert len(statements) == 1
    assert badge_value == doi

    pattern = r"10\.1234/[a-z0-9\-]{1,12}"
    assert re.fullmatch(pattern, badge_value) is not None
