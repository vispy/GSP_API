"""Tests for S022 no-network mock HTTP array conformance fixtures."""

import json

import pytest

from fixtures.conformance import (
    load_s022_http_mock_array_fixture,
    validate_s022_http_mock_array_fixture,
)


def test_s022_http_mock_array_fixture_is_json_safe_and_no_network():
    fixture = load_s022_http_mock_array_fixture()

    encoded = json.dumps(fixture, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded["schema_kind"] == "gsp.conformance.s022-http-mock-array"
    assert decoded["schema_version"] == "0.1.0"
    assert decoded["protocol"]["network_io_allowed"] is False
    assert decoded["protocol"]["dynamic_loading_allowed"] is False
    assert decoded["mock_access"]["fetcher_id"] == "gsp.fetcher.http.mock.v1"
    assert decoded["mock_access"]["network_io"] is False


def test_s022_http_mock_array_fixture_validates_replay_cases():
    results = validate_s022_http_mock_array_fixture()

    assert len(results) == 16
    assert all(result.passed for result in results)
    by_id = {result.case_id: result for result in results}
    assert by_id["s022:http-mock-npy-array-success"].observed_codes == ()
    assert "GSP_FETCH_DESCRIPTOR_REJECTED" in by_id["s022:descriptor-fetch-descriptor-rejected"].observed_codes
    assert "GSP_CONTENT_TYPE_UNSUPPORTED" in by_id["s022:response-content-type-rejected"].observed_codes
    assert "GSP_QUERY_SCOPE_VIOLATION" in by_id["s022:query-out-of-bounds"].observed_codes


def test_s022_http_mock_array_fixture_detects_value_mismatch():
    fixture = load_s022_http_mock_array_fixture()
    fixture["cases"][0]["expected_array"]["values"][0][0] = 99.0

    with pytest.raises(ValueError, match="materialized values mismatch"):
        validate_s022_http_mock_array_fixture(fixture)
