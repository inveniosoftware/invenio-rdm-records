# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for serializer utility functions."""

from unittest.mock import MagicMock, patch

import pytest

from invenio_rdm_records.resources.serializers.errors import VocabularyItemNotFoundError
from invenio_rdm_records.resources.serializers.utils import get_vocabulary_props


def _make_hit(**props):
    h = MagicMock()
    h.get = lambda k, default=None: props.get(k, default)
    return h


def _make_results(*hits):
    r = MagicMock()
    r.hits = list(hits)
    return r


def _make_mock_svc(results):
    """Return a MagicMock service stub without accessing Flask-proxied original."""
    mock_svc = MagicMock()
    mock_svc.read_all.return_value = results
    return mock_svc


class TestGetVocabularyProps:
    """Tests for get_vocabulary_props helper."""

    def test_query_uses_id_keyword_subfield(self):
        """Term query must target id.keyword, not the text-analyzed id field.

        Vocabulary IDs such as EHVM-H119 are tokenised by the text analyser
        (lowercased, hyphen-split) and would not match a term query on `id`.
        The `.keyword` sub-field stores the original string verbatim.
        """
        hit = _make_hit(props={"datacite": "Dataset"})
        results = _make_results(hit)
        mock_svc = _make_mock_svc(results)

        with patch(
            "invenio_rdm_records.resources.serializers.utils.vocabulary_service",
            new=mock_svc,
        ):
            get_vocabulary_props("resourcetypes", ["datacite"], "EHVM-H119")

        extra_filter = mock_svc.read_all.call_args.kwargs.get("extra_filter")
        assert extra_filter is not None, "extra_filter was not passed to read_all"
        q_dict = extra_filter.to_dict()
        assert "term" in q_dict, f"Expected term query, got: {q_dict}"
        term_body = q_dict["term"]
        assert "id.keyword" in term_body, (
            f"Term query targets {list(term_body.keys())!r} instead of 'id.keyword'."
            " Uppercase/hyphenated vocabulary IDs (e.g. EHVM-H119) will fail."
        )
        assert "id" not in term_body, (
            "Term query must NOT target the text-analyzed 'id' field"
        )

    def test_returns_props_on_hit(self):
        hit = _make_hit(props={"datacite": "Dataset"})
        results = _make_results(hit)
        mock_svc = _make_mock_svc(results)

        with patch(
            "invenio_rdm_records.resources.serializers.utils.vocabulary_service",
            new=mock_svc,
        ):
            props = get_vocabulary_props("resourcetypes", ["datacite"], "dataset")

        assert props == {"datacite": "Dataset"}

    def test_raises_when_not_found(self):
        results = _make_results()
        mock_svc = _make_mock_svc(results)

        with patch(
            "invenio_rdm_records.resources.serializers.utils.vocabulary_service",
            new=mock_svc,
        ):
            with pytest.raises(VocabularyItemNotFoundError):
                get_vocabulary_props("resourcetypes", ["datacite"], "EHVM-H119")

    def test_returns_empty_props_when_props_key_missing(self):
        hit = _make_hit()
        results = _make_results(hit)
        mock_svc = _make_mock_svc(results)

        with patch(
            "invenio_rdm_records.resources.serializers.utils.vocabulary_service",
            new=mock_svc,
        ):
            props = get_vocabulary_props("resourcetypes", ["datacite"], "dataset")

        assert props == {}
