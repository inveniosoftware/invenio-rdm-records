# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test token serializers."""

from datetime import datetime, timedelta, timezone

import pytest
from itsdangerous import SignatureExpired

from invenio_rdm_records.secret_links.serializers import (
    SecretLinkSerializer,
    TimedSecretLinkSerializer,
)


def test_serializer(base_app):
    """Test the SecretLinkSerializer."""
    with base_app.app_context():
        serializer = SecretLinkSerializer()
        tkn_str = serializer.create_token(
            obj_id="someid", extra_data={"hello": "world"}
        )
        tkn_str2 = serializer.create_token(
            obj_id="someid", extra_data={"hello": "world"}
        )

        # check the creation of tokens from the same data doesn't
        # result in identical results
        assert tkn_str != tkn_str2
        assert isinstance(tkn_str, str)

        # test token loading
        tkn_dict = serializer.load_token(tkn_str)
        assert tkn_dict["id"] == "someid"
        assert tkn_dict["data"]["hello"] == "world"
        assert "random" not in tkn_dict

        # test the raw 'loads(...)'
        tkn_dict_orig = serializer.loads(tkn_str)
        assert "random" in tkn_dict_orig
        del tkn_dict_orig["random"]
        assert tkn_dict == tkn_dict_orig


def test_serializer_validate_token(base_app):
    """Test validation of a valid token."""
    with base_app.app_context():
        serializer = SecretLinkSerializer()
        tkn_str = serializer.create_token(
            obj_id="someid", extra_data={"hello": "world"}
        )

        tkn_dict = serializer.validate_token(tkn_str, expected_data={"hello": "world"})
        assert tkn_dict


def test_serializer_validate_invalid_token(base_app):
    """Test validation of an invalid token."""
    with base_app.app_context():
        serializer = SecretLinkSerializer()
        tkn_dict = serializer.validate_token("asdf")
        assert tkn_dict is None


def test_timed_serializer(base_app):
    """Test loading operations on valid tokens."""
    with base_app.app_context():
        in_10_mins = datetime.now(timezone.utc) + timedelta(minutes=10)
        serializer = TimedSecretLinkSerializer(expires_at=in_10_mins)
        tkn_str = serializer.create_token(
            obj_id="someid", extra_data={"hello": "world"}
        )
        tkn_str2 = serializer.create_token(
            obj_id="someid", extra_data={"hello": "world"}
        )

        # check the creation of tokens from the same data doesn't
        # result in identical results
        assert tkn_str != tkn_str2
        assert isinstance(tkn_str, str)

        # test token loading
        tkn_dict = serializer.load_token(tkn_str)
        assert tkn_dict["id"] == "someid"
        assert tkn_dict["data"]["hello"] == "world"
        assert "random" not in tkn_dict

        # test the raw 'loads(...)'
        tkn_dict_orig = serializer.loads(tkn_str)
        assert "random" in tkn_dict_orig
        del tkn_dict_orig["random"]
        assert tkn_dict == tkn_dict_orig


def test_timed_serializer_expired(base_app):
    """Test loading operations on expired tokens."""
    with base_app.app_context():
        _10_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        serializer = TimedSecretLinkSerializer(expires_at=_10_mins_ago)
        tkn_str = serializer.create_token(
            obj_id="someid", extra_data={"hello": "world"}
        )

        # test token loading
        with pytest.raises(SignatureExpired):
            serializer.load_token(tkn_str)

        # test the raw 'loads(...)'
        with pytest.raises(SignatureExpired):
            serializer.loads(tkn_str)

        tkn_dict = serializer.load_token(tkn_str, force=True)
        assert tkn_dict["id"] == "someid"
        assert tkn_dict["data"] == {"hello": "world"}
