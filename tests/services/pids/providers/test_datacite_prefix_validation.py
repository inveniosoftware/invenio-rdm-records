"""Test DataCite prefix validation."""

from unittest.mock import Mock

import pytest
from flask import current_app

from invenio_rdm_records.services.pids.providers import DataCiteClient


def test_datacite_prefix_validation_with_additional_list(running_app):
    """Test that DataCiteClient validates prefix against additional prefixes list."""
    # Configure DataCite with additional prefixes list
    old_config = dict(current_app.config)
    current_app.config.update(
        {
            "DATACITE_ENABLED": True,
            "DATACITE_USERNAME": "INVALID",
            "DATACITE_PASSWORD": "INVALID",
            "DATACITE_PREFIX": "10.1234",
            "DATACITE_ADDITIONAL_PREFIXES": ["10.5678"],
        }
    )

    try:
        # Create a mock record with PID
        mock_record = Mock()
        mock_record.pid.pid_value = "test123"

        # Create client
        client = DataCiteClient("test")

        # Test 1: Default prefix should work (always allowed)
        doi = client.generate_doi(mock_record)
        assert doi == "10.1234/test123"

        # Test 2: Additional custom prefix should work
        doi_custom = client.generate_doi(mock_record, prefix="10.5678")
        assert doi_custom == "10.5678/test123"

        # Test 3: Unsupported prefix should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            client.generate_doi(mock_record, prefix="10.9999")

        assert "not in the list of allowed DataCite prefixes" in str(exc_info.value)
        assert "10.9999" in str(exc_info.value)
        assert "10.1234, 10.5678" in str(exc_info.value)

        print("✓ Default prefix from config works")
        print("✓ Custom prefix in additional list works")
        print("✓ Custom prefix not in allowed list raises error")

    finally:
        # Restore config
        current_app.config.clear()
        current_app.config.update(old_config)


def test_datacite_prefix_validation_without_additional_prefixes(running_app):
    """Test that DataCiteClient only allows default prefix when additional_prefixes is None."""
    # Configure DataCite without additional prefixes (None = only default allowed)
    old_config = dict(current_app.config)
    current_app.config.update(
        {
            "DATACITE_ENABLED": True,
            "DATACITE_USERNAME": "INVALID",
            "DATACITE_PASSWORD": "INVALID",
            "DATACITE_PREFIX": "10.1234",
            # DATACITE_ADDITIONAL_PREFIXES not set (None = only default prefix)
        }
    )

    try:
        # Create a mock record with PID
        mock_record = Mock()
        mock_record.pid.pid_value = "test456"

        # Create client
        client = DataCiteClient("test")

        # Test 1: Default prefix should work
        doi = client.generate_doi(mock_record)
        assert doi == "10.1234/test456"

        # Test 2: Custom prefix should fail when additional_prefixes is None
        with pytest.raises(RuntimeError) as exc_info:
            client.generate_doi(mock_record, prefix="10.9999")

        assert "not in the list of allowed DataCite prefixes" in str(exc_info.value)
        assert "10.9999" in str(exc_info.value)
        assert "10.1234" in str(exc_info.value)

        print("✓ Only default prefix allowed when DATACITE_ADDITIONAL_PREFIXES is None")

    finally:
        # Restore config
        current_app.config.clear()
        current_app.config.update(old_config)


def test_datacite_prefix_override_with_allowed_prefix(running_app):
    """Test that DataCiteClient respects prefix kwarg override when prefix is allowed."""
    # Configure DataCite with additional prefixes
    old_config = dict(current_app.config)
    current_app.config.update(
        {
            "DATACITE_ENABLED": True,
            "DATACITE_USERNAME": "INVALID",
            "DATACITE_PASSWORD": "INVALID",
            "DATACITE_PREFIX": "10.1234",
            "DATACITE_ADDITIONAL_PREFIXES": ["10.9999"],
        }
    )

    try:
        # Create a mock record with PID
        mock_record = Mock()
        mock_record.pid.pid_value = "test789"

        # Create client
        client = DataCiteClient("test")

        # Test default prefix from config
        doi = client.generate_doi(mock_record)
        assert doi == "10.1234/test789", f"Expected 10.1234/test789, got {doi}"

        # Test prefix override with allowed prefix
        doi_override = client.generate_doi(mock_record, prefix="10.9999")
        assert (
            doi_override == "10.9999/test789"
        ), f"Expected 10.9999/test789, got {doi_override}"

        print("✓ Prefix override works with allowed additional prefix")

    finally:
        # Restore config
        current_app.config.clear()
        current_app.config.update(old_config)


def test_datacite_default_prefix_always_allowed(running_app):
    """Test that default prefix is always allowed even with empty additional list."""
    old_config = dict(current_app.config)
    current_app.config.update(
        {
            "DATACITE_ENABLED": True,
            "DATACITE_USERNAME": "INVALID",
            "DATACITE_PASSWORD": "INVALID",
            "DATACITE_PREFIX": "10.1234",
            "DATACITE_ADDITIONAL_PREFIXES": [],  # Empty list
        }
    )

    try:
        mock_record = Mock()
        mock_record.pid.pid_value = "test000"

        client = DataCiteClient("test")

        # Default prefix should always work
        doi = client.generate_doi(mock_record)
        assert doi == "10.1234/test000"

        # Other prefixes should fail with empty list
        with pytest.raises(RuntimeError) as exc_info:
            client.generate_doi(mock_record, prefix="10.5555")

        assert "not in the list of allowed DataCite prefixes" in str(exc_info.value)

        print("✓ Default prefix always allowed, even with empty additional list")

    finally:
        current_app.config.clear()
        current_app.config.update(old_config)


def test_datacite_multiple_additional_prefixes(running_app):
    """Test that multiple additional prefixes are all allowed."""
    old_config = dict(current_app.config)
    current_app.config.update(
        {
            "DATACITE_ENABLED": True,
            "DATACITE_USERNAME": "INVALID",
            "DATACITE_PASSWORD": "INVALID",
            "DATACITE_PREFIX": "10.1234",
            "DATACITE_ADDITIONAL_PREFIXES": ["10.5678", "10.9999", "10.1111"],
        }
    )

    try:
        mock_record = Mock()
        mock_record.pid.pid_value = "testmulti"

        client = DataCiteClient("test")

        # Test all allowed prefixes
        for prefix in ["10.1234", "10.5678", "10.9999", "10.1111"]:
            doi = client.generate_doi(mock_record, prefix=prefix)
            assert doi == f"{prefix}/testmulti"

        # Test disallowed prefix
        with pytest.raises(RuntimeError) as exc_info:
            client.generate_doi(mock_record, prefix="10.8888")

        assert "not in the list of allowed DataCite prefixes" in str(exc_info.value)

        print("✓ All additional prefixes are allowed")

    finally:
        current_app.config.clear()
        current_app.config.update(old_config)


if __name__ == "__main__":
    print("=== Testing DataCite Prefix Validation ===\n")

    print("Scenario 1: With additional prefixes list")
    print("-" * 50)
    print("This test requires running_app fixture, run with pytest")

    print("\n✅ Validation logic implemented!")
    print("\nFeature:")
    print("- DATACITE_ADDITIONAL_PREFIXES config validates custom prefixes")
    print("- None = only default prefix allowed (secure default)")
    print("- [] = only default prefix allowed")
    print("- [...] = default + listed prefixes allowed")
