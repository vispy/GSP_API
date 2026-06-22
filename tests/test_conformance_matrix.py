"""Tests for backend conformance matrix expectations."""

import pytest

from fixtures.conformance import BackendConformanceExpectation, backend_conformance_matrix
from gsp.protocol import QueryStatus, TILED_IMAGE_EXTENSION_CAPABILITY, VisualFamily


def _matrix_ids(expectation: BackendConformanceExpectation) -> str:
    return expectation.backend_id


def test_backend_conformance_matrix_lists_reference_and_deferred_backends():
    matrix = backend_conformance_matrix()

    assert tuple(entry.backend_id for entry in matrix) == ("matplotlib", "datoviz")
    assert tuple(entry.status for entry in matrix) == ("pass", "skip")
    assert matrix[0].replay is not None
    assert matrix[1].replay is None
    assert "conformance replay" in matrix[1].reason


@pytest.mark.parametrize("expectation", backend_conformance_matrix(), ids=_matrix_ids)
def test_backend_conformance_matrix_replays_or_skips_cleanly(expectation: BackendConformanceExpectation):
    if expectation.status == "skip":
        pytest.skip(expectation.reason)

    assert expectation.replay is not None
    replay = expectation.replay()

    assert replay.server_name == "gsp-v0.1-reference"
    assert replay.visual_families == ("point", "image")
    assert replay.extensions == (TILED_IMAGE_EXTENSION_CAPABILITY,)
    assert replay.point_query.status == QueryStatus.HIT
    assert replay.point_query.visual_family == VisualFamily.POINT
    assert replay.guide_query.status == QueryStatus.HIT
    assert replay.guide_miss.status == QueryStatus.MISS
    assert replay.tiled_query.status == QueryStatus.HIT
