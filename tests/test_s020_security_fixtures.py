"""Tests for S020 no-network security negative conformance fixtures."""

import json

import pytest

from fixtures.conformance import (
    load_s020_security_negative_fixture,
    validate_s020_security_negative_fixture,
)


def test_s020_security_negative_fixture_is_json_safe_and_no_network():
    fixture = load_s020_security_negative_fixture()

    encoded = json.dumps(fixture, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded["schema_kind"] == "gsp.conformance.security-negative"
    assert decoded["schema_version"] == "0.1.0"
    assert decoded["protocol"]["network_io_allowed"] is False
    assert decoded["protocol"]["dynamic_loading_allowed"] is False


def test_s020_security_negative_fixture_validates_expected_diagnostics():
    results = validate_s020_security_negative_fixture()

    assert len(results) == 7
    assert all(result.passed for result in results)
    by_id = {result.case_id: result for result in results}
    assert "GSP_FETCH_DESCRIPTOR_REJECTED" in by_id["source:direct-remote-fetch-disabled"].observed_codes
    assert "GSP_SOURCE_HANDLE_UNKNOWN" in by_id["source:unknown-preconfigured-handle"].observed_codes
    assert "GSP_MANIFEST_EXECUTION_FORBIDDEN" in by_id["manifest:python-import-forbidden"].observed_codes


def test_s020_security_negative_fixture_detects_diagnostic_mismatch():
    fixture = load_s020_security_negative_fixture()
    fixture["cases"][0]["expected_codes"] = ["GSP_INLINE_SECRET_REJECTED"]

    with pytest.raises(ValueError, match="expected diagnostic codes"):
        validate_s020_security_negative_fixture(fixture)
