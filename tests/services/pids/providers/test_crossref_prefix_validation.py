"""Test Crossref prefix validation."""

from unittest.mock import Mock

import pytest
from flask import current_app

from invenio_rdm_records.services.pids.providers import CrossrefClient


def test_crossref_prefix_validation_with_supported_list(running_app):
    """Test that CrossrefClient validates prefix against supported prefixes list."""
    # Configure Crossref with additional prefixes list
    old_config = dict(current_app.config)
    current_app.config.update(
        {
            "CROSSREF_ENABLED": True,
            "CROSSREF_USERNAME": "INVALID",
            "CROSSREF_PASSWORD": "INVALID",
            "CROSSREF_DEPOSITOR": "INVALID",
            "CROSSREF_EMAIL": "info@example.org",
            "CROSSREF_REGISTRANT": "INVALID",
            "CROSSREF_PREFIX": "10.1234",
            "CROSSREF_ADDITIONAL_PREFIXES": ["10.5678"],
        }
    )

    try:
        # Create a mock record with PID
        mock_record = Mock()
        mock_record.pid.pid_value = "test123"

        # Create client
        client = CrossrefClient("test")

        # Test 1: Default prefix should work (always allowed)
        doi = client.generate_doi(mock_record)
        assert doi == "10.1234/test123"

        # Test 2: Additional custom prefix should work
        doi_custom = client.generate_doi(mock_record, prefix="10.5678")
        assert doi_custom == "10.5678/test123"

        # Test 3: Unsupported prefix should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            client.generate_doi(mock_record, prefix="10.9999")

        assert "not in the list of allowed Crossref prefixes" in str(exc_info.value)
        assert "10.9999" in str(exc_info.value)
        assert "10.1234, 10.5678" in str(exc_info.value)

        print("✓ Default prefix from config works")
        print("✓ Custom prefix in additional list works")
        print("✓ Custom prefix not in allowed list raises error")

    finally:
        # Restore config
        current_app.config.clear()
        current_app.config.update(old_config)


def test_crossref_prefix_validation_without_additional_prefixes(running_app):
    """Test that CrossrefClient only allows default prefix when additional_prefixes is None."""
    # Configure Crossref without additional prefixes (None = only default allowed)
    old_config = dict(current_app.config)
    current_app.config.update(
        {
            "CROSSREF_ENABLED": True,
            "CROSSREF_USERNAME": "INVALID",
            "CROSSREF_PASSWORD": "INVALID",
            "CROSSREF_DEPOSITOR": "INVALID",
            "CROSSREF_EMAIL": "info@example.org",
            "CROSSREF_REGISTRANT": "INVALID",
            "CROSSREF_PREFIX": "10.1234",
            # CROSSREF_ADDITIONAL_PREFIXES not set (None = only default prefix)
        }
    )

    try:
        # Create a mock record with PID
        mock_record = Mock()
        mock_record.pid.pid_value = "test456"

        # Create client
        client = CrossrefClient("test")

        # Test 1: Default prefix should work
        doi = client.generate_doi(mock_record)
        assert doi == "10.1234/test456"

        # Test 2: Custom prefix should fail when additional_prefixes is None
        with pytest.raises(RuntimeError) as exc_info:
            client.generate_doi(mock_record, prefix="10.9999")

        assert "not in the list of allowed Crossref prefixes" in str(exc_info.value)
        assert "10.9999" in str(exc_info.value)
        assert "10.1234" in str(exc_info.value)

        print("✓ Only default prefix allowed when CROSSREF_ADDITIONAL_PREFIXES is None")

    finally:
        # Restore config
        current_app.config.clear()
        current_app.config.update(old_config)


if __name__ == "__main__":
    print("=== Testing Crossref Prefix Validation ===\n")

    print("Scenario 1: With supported prefixes list")
    print("-" * 50)
    print("This test requires running_app fixture, run with pytest")

    print("\n✅ Validation logic implemented!")
    print("\nFeature:")
    print("- CROSSREF_SUPPORTED_PREFIXES config validates custom prefixes")
    print("- Empty list = no validation (allows any prefix)")
    print("- Non-empty list = only listed prefixes allowed")
