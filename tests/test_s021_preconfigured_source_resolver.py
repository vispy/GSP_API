"""Tests for the S021 no-network preconfigured-source resolver proof."""

import numpy as np

from gsp.protocol import (
    CredentialPolicy,
    DataLocality,
    DataSourceDescriptor,
    DataSourceKind,
    SecurityDiagnosticCode,
    TileIndex,
    TileRequest,
    demo_no_network_preconfigured_source_resolver,
    s020_security_capability_metadata,
    validate_no_network_source_descriptor,
)


def test_demo_resolver_advertises_only_opaque_no_network_handles():
    resolver = demo_no_network_preconfigured_source_resolver()

    assert resolver.resolver_id == "gsp.test.synthetic-resolver"
    assert resolver.source_refs == ({"resolver_id": "gsp.test.synthetic-resolver", "source_id": "public-demo-pyramid"},)
    assert resolver.capability_record() == {
        "resolver_id": "gsp.test.synthetic-resolver",
        "source_kinds": ("tiled-image",),
        "credential_policies": ("none",),
        "network_io": False,
        "source_ids": ("public-demo-pyramid",),
    }


def test_demo_resolver_descriptor_validates_against_s020_security_surface():
    resolver = demo_no_network_preconfigured_source_resolver()
    descriptor = resolver.descriptor_for("public-demo-pyramid")

    result = validate_no_network_source_descriptor(descriptor, allowed_source_refs=resolver.source_refs)

    assert result.accepted
    assert descriptor.locality == DataLocality.PRECONFIGURED_SOURCE
    assert descriptor.credential_policy == CredentialPolicy.NONE
    assert descriptor.fetch_descriptor is None
    assert descriptor.source_ref == {"resolver_id": "gsp.test.synthetic-resolver", "source_id": "public-demo-pyramid"}


def test_demo_resolver_materializes_deterministic_tile_without_network_io():
    resolver = demo_no_network_preconfigured_source_resolver()
    resolved = resolver.resolve(resolver.descriptor_for("public-demo-pyramid"))

    assert resolved.accepted
    assert resolved.source is not None
    assert resolved.provider is not None
    tile = resolved.provider.get_tile(TileRequest(source_id=resolved.source.id, tile=TileIndex(level=0, x=1, y=1)))

    assert tile.data is not None
    assert tile.data.shape == (4, 4, 4)
    np.testing.assert_array_equal(tile.data[0, 0], [4, 4, 0, 255])
    np.testing.assert_array_equal(tile.data[-1, -1], [7, 7, 0, 255])


def test_demo_resolver_rejects_unknown_handle_with_stable_diagnostic():
    resolver = demo_no_network_preconfigured_source_resolver()
    descriptor = DataSourceDescriptor(
        id="source:unknown",
        kind=DataSourceKind.TILED_IMAGE,
        shape=(16, 16, 4),
        locality=DataLocality.PRECONFIGURED_SOURCE,
        source_ref={"resolver_id": resolver.resolver_id, "source_id": "unknown"},
    )

    security = validate_no_network_source_descriptor(descriptor, allowed_source_refs=resolver.source_refs)
    resolved = resolver.resolve(descriptor)

    assert not security.accepted
    assert SecurityDiagnosticCode.SOURCE_HANDLE_UNKNOWN in security.codes
    assert not resolved.accepted
    assert resolved.diagnostic == (
        "GSP_SOURCE_HANDLE_UNKNOWN: preconfigured-source source_ref is not advertised by the no-network resolver"
    )


def test_demo_resolver_rejects_fetch_descriptor_even_for_known_handle():
    resolver = demo_no_network_preconfigured_source_resolver()
    descriptor = resolver.descriptor_for("public-demo-pyramid")
    descriptor = DataSourceDescriptor(
        id=descriptor.id,
        kind=descriptor.kind,
        shape=descriptor.shape,
        locality=descriptor.locality,
        source_ref=descriptor.source_ref,
        fetch_descriptor={"url": "https://example.invalid/tiles/{z}/{x}/{y}.png"},
    )

    resolved = resolver.resolve(descriptor)

    assert not resolved.accepted
    assert resolved.diagnostic == "GSP_FETCH_DESCRIPTOR_REJECTED: fetch_descriptor is reserved and rejected in S020 no-network mode"


def test_security_capability_metadata_includes_preconfigured_resolver_record():
    resolver = demo_no_network_preconfigured_source_resolver()
    metadata = s020_security_capability_metadata(preconfigured_resolvers=(resolver.capability_record(),))

    assert metadata["data_sources"]["remote_fetch_descriptors"] == {"accepted": False}
    assert metadata["data_sources"]["supports_server_side_fetch"] == {"accepted": False}
    assert metadata["data_sources"]["preconfigured_resolvers"] == [
        {
            "resolver_id": "gsp.test.synthetic-resolver",
            "source_kinds": ["tiled-image"],
            "credential_policies": ["none"],
            "network_io": False,
            "source_ids": ["public-demo-pyramid"],
        }
    ]


def test_no_network_resolver_rejects_credentialed_registered_sources():
    resolver = demo_no_network_preconfigured_source_resolver()
    source = resolver.resolve(resolver.descriptor_for("public-demo-pyramid")).source
    assert source is not None

    credentialed = DataSourceDescriptor(
        id="source:credentialed",
        kind=DataSourceKind.TILED_IMAGE,
        shape=source.shape,
        locality=DataLocality.PRECONFIGURED_SOURCE,
        credential_policy=CredentialPolicy.PRECONFIGURED,
        source_ref={"resolver_id": "gsp.test.synthetic-resolver", "source_id": source.id},
    )

    resolved = resolver.resolve(credentialed)

    assert not resolved.accepted
    assert resolved.diagnostic == "GSP_CREDENTIAL_POLICY_UNSUPPORTED: no-network resolver supports only credential_policy=none"


def test_demo_resolver_rejects_known_handle_with_url_metadata():
    resolver = demo_no_network_preconfigured_source_resolver()
    descriptor = resolver.descriptor_for("public-demo-pyramid")
    descriptor = DataSourceDescriptor(
        id=descriptor.id,
        kind=descriptor.kind,
        shape=descriptor.shape,
        locality=descriptor.locality,
        source_ref=descriptor.source_ref,
        metadata={"url": "https://example.invalid/private"},
    )

    resolved = resolver.resolve(descriptor)

    assert not resolved.accepted
    assert resolved.diagnostic == "GSP_REMOTE_FETCH_DISABLED: field 'url' is URL-like"
