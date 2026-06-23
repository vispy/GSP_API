"""GSP v0.1 conformance fixture package."""

from .baseline import (
    ConformanceScene,
    GuideConformanceScene,
    TiledSourceConformanceScene,
    capability_snapshot_fixture,
    guide_scene,
    image_visual_fixture,
    point_over_image_scene,
    point_visual_fixture,
    tiled_image_source_fixture,
    tiled_source_scene,
)
from .array_chunks import Base64ArrayChunk, validate_base64_array_chunk
from .debug_report import conformance_debug_report, conformance_debug_report_json
from .json_fixture import (
    MINIMAL_JSON_FIXTURE_NAME,
    load_minimal_json_fixture,
    replay_minimal_json_fixture,
    validate_minimal_json_fixture,
)
from .matrix import BackendConformanceExpectation, backend_conformance_matrix
from .preconfigured_source_fixture import (
    S021_PRECONFIGURED_SOURCE_FIXTURE_NAME,
    PreconfiguredSourceCaseResult,
    load_s021_preconfigured_source_fixture,
    validate_s021_preconfigured_source_fixture,
)
from .replay import InProcessReplayResult, replay_conformance_fixtures
from .security_fixture import (
    S020_SECURITY_NEGATIVE_FIXTURE_NAME,
    SecurityNegativeCaseResult,
    load_s020_security_negative_fixture,
    validate_s020_security_negative_fixture,
)
from .s022_http_mock_array import (
    S022_HTTP_MOCK_ARRAY_FIXTURE_NAME,
    S022HttpMockArrayCaseResult,
    load_s022_http_mock_array_fixture,
    s022_http_mock_array_capability_metadata,
    validate_s022_http_mock_array_fixture,
)

__all__ = [
    "Base64ArrayChunk",
    "BackendConformanceExpectation",
    "ConformanceScene",
    "GuideConformanceScene",
    "InProcessReplayResult",
    "MINIMAL_JSON_FIXTURE_NAME",
    "PreconfiguredSourceCaseResult",
    "S020_SECURITY_NEGATIVE_FIXTURE_NAME",
    "S021_PRECONFIGURED_SOURCE_FIXTURE_NAME",
    "S022HttpMockArrayCaseResult",
    "S022_HTTP_MOCK_ARRAY_FIXTURE_NAME",
    "SecurityNegativeCaseResult",
    "TiledSourceConformanceScene",
    "backend_conformance_matrix",
    "capability_snapshot_fixture",
    "conformance_debug_report",
    "conformance_debug_report_json",
    "guide_scene",
    "image_visual_fixture",
    "load_minimal_json_fixture",
    "load_s021_preconfigured_source_fixture",
    "load_s020_security_negative_fixture",
    "load_s022_http_mock_array_fixture",
    "point_over_image_scene",
    "point_visual_fixture",
    "replay_minimal_json_fixture",
    "replay_conformance_fixtures",
    "s022_http_mock_array_capability_metadata",
    "tiled_image_source_fixture",
    "tiled_source_scene",
    "validate_base64_array_chunk",
    "validate_minimal_json_fixture",
    "validate_s021_preconfigured_source_fixture",
    "validate_s020_security_negative_fixture",
    "validate_s022_http_mock_array_fixture",
]
