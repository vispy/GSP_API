"""Tests for S022 no-network HTTP array descriptor validation."""

from gsp.protocol import (
    CredentialPolicy,
    DataLocality,
    DataSourceDescriptor,
    DataSourceKind,
    MaterializationPolicy,
    SecurityDiagnosticCode,
    validate_s022_http_array_source_descriptor,
)


SOURCE_REF = {"resolver_id": "gsp.demo.http-resource-resolver", "source_id": "demo-http-npy-array"}


def _array_descriptor(**overrides: object) -> DataSourceDescriptor:
    values: dict[str, object] = {
        "id": "source:s022-array",
        "kind": DataSourceKind.ARRAY,
        "shape": (4, 4),
        "dtype": "float32",
        "channels": 1,
        "coordinate_system": "array-index",
        "locality": DataLocality.PRECONFIGURED_SOURCE,
        "credential_policy": CredentialPolicy.NONE,
        "source_ref": SOURCE_REF,
        "materialization_policy": MaterializationPolicy.FULL,
        "cache_policy": {"mode": "none"},
        "metadata": {
            "format": "npy",
            "decoder_id": "gsp.decoder.npy.v1",
            "materialization_target": "array-resource",
            "x-purpose": "s022-http-single-resource-proof",
        },
    }
    values.update(overrides)
    return DataSourceDescriptor(**values)  # type: ignore[arg-type]


def test_s022_http_array_descriptor_accepts_preconfigured_npy_array_shape():
    result = validate_s022_http_array_source_descriptor(_array_descriptor(), allowed_source_refs=(SOURCE_REF,))

    assert result.accepted
    assert result.codes == ()


def test_s022_http_array_descriptor_rejects_http_as_source_contract():
    result = validate_s022_http_array_source_descriptor(
        _array_descriptor(kind=DataSourceKind.OPAQUE),
        allowed_source_refs=(SOURCE_REF,),
    )

    assert not result.accepted
    assert SecurityDiagnosticCode.SOURCE_CONTRACT_UNSUPPORTED in result.codes


def test_s022_http_array_descriptor_rejects_direct_remote_fetch_and_fetch_descriptor():
    result = validate_s022_http_array_source_descriptor(
        _array_descriptor(
            locality=DataLocality.DIRECT_REMOTE_FETCH,
            fetch_descriptor={"url": "https://example.invalid/demo.npy"},
        ),
        allowed_source_refs=(SOURCE_REF,),
    )

    assert not result.accepted
    assert SecurityDiagnosticCode.SOURCE_LOCALITY_UNSUPPORTED in result.codes
    assert SecurityDiagnosticCode.FETCH_DESCRIPTOR_REJECTED in result.codes
    assert SecurityDiagnosticCode.REMOTE_FETCH_DISABLED in result.codes


def test_s022_http_array_descriptor_rejects_credentials_and_headers():
    result = validate_s022_http_array_source_descriptor(
        _array_descriptor(
            credential_policy=CredentialPolicy.PRECONFIGURED_REF,
            credential_ref="private-credential",
            metadata={
                "format": "npy",
                "decoder_id": "gsp.decoder.npy.v1",
                "materialization_target": "array-resource",
                "headers": {"authorization": "Bearer secret"},
            },
        ),
        allowed_source_refs=(SOURCE_REF,),
    )

    assert not result.accepted
    assert SecurityDiagnosticCode.CREDENTIAL_POLICY_UNSUPPORTED in result.codes
    assert SecurityDiagnosticCode.CREDENTIAL_REF_REJECTED in result.codes
    assert SecurityDiagnosticCode.INLINE_SECRET_REJECTED in result.codes


def test_s022_http_array_descriptor_rejects_decoder_plugin_attempt():
    result = validate_s022_http_array_source_descriptor(
        _array_descriptor(
            metadata={
                "format": "npy",
                "decoder_id": "python.import:custom_decoder",
                "materialization_target": "array-resource",
                "decoder_config": {"python_import": "bad.plugin"},
            },
        ),
        allowed_source_refs=(SOURCE_REF,),
    )

    assert not result.accepted
    assert SecurityDiagnosticCode.DECODER_PLUGIN_DISABLED in result.codes


def test_s022_http_array_descriptor_rejects_bad_contract_details_and_cache_mode():
    result = validate_s022_http_array_source_descriptor(
        _array_descriptor(
            dtype="object",
            shape=(4,),
            coordinate_system="pixel",
            materialization_policy=MaterializationPolicy.VIEWPORT_MOSAIC,
            cache_policy={"mode": "shared-readonly"},
            metadata={
                "format": "png",
                "decoder_id": "gsp.decoder.png.v1",
                "materialization_target": "texture-resource",
            },
        ),
        allowed_source_refs=(SOURCE_REF,),
    )

    assert not result.accepted
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in result.codes
    assert SecurityDiagnosticCode.DECODER_UNSUPPORTED in result.codes
    assert SecurityDiagnosticCode.CACHE_POLICY_UNSUPPORTED in result.codes
