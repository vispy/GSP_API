"""Tests for S021 preconfigured-source conformance fixtures."""

import json

import pytest

from fixtures.conformance import (
    load_s021_preconfigured_source_fixture,
    validate_s021_preconfigured_source_fixture,
)


def test_s021_preconfigured_source_fixture_is_json_safe_and_no_network():
    fixture = load_s021_preconfigured_source_fixture()

    encoded = json.dumps(fixture, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded["schema_kind"] == "gsp.conformance.preconfigured-source"
    assert decoded["schema_version"] == "0.1.0"
    assert decoded["protocol"]["network_io_allowed"] is False
    assert decoded["protocol"]["dynamic_loading_allowed"] is False


def test_s021_preconfigured_source_fixture_validates_resolver_replay():
    results = validate_s021_preconfigured_source_fixture()

    assert len(results) == 3
    assert all(result.passed for result in results)
    by_id = {result.case_id: result for result in results}
    assert by_id["resolver:known-handle-tile"].diagnostic is None
    assert by_id["resolver:unknown-handle"].diagnostic is not None
    assert by_id["resolver:fetch-descriptor-rejected"].diagnostic is not None


def test_s021_preconfigured_source_fixture_detects_tile_mismatch():
    fixture = load_s021_preconfigured_source_fixture()
    fixture["cases"][0]["expected_tile"]["first_rgba"] = [0, 0, 0, 0]

    with pytest.raises(ValueError, match="first pixel mismatch"):
        validate_s021_preconfigured_source_fixture(fixture)
