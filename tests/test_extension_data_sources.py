"""Tests for the M011 extension and virtual data-source proof."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from gsp.protocol import (
    AdaptationOutcome,
    CapabilitySnapshot,
    CredentialPolicy,
    DataLocality,
    ExtensionKind,
    ExtensionManifest,
    FakeTiledImageProvider,
    QueryRequest,
    QueryResult,
    QueryStatus,
    TILED_IMAGE_EXTENSION_CAPABILITY,
    TILED_IMAGE_QUERY_PAYLOAD_KIND,
    TileIndex,
    TileRequest,
    TiledImageQueryPayload,
    TiledImageSource,
    TransportKind,
    ViewportTileRequest,
    extension_capability,
    tiled_image_extension_manifest,
    validate_extension_manifest,
    validate_tiled_image_source_manifest_link,
)
from gsp_matplotlib.tiled_image import query_tiled_image_source, render_tiled_image_source


def _source() -> TiledImageSource:
    return TiledImageSource(
        id="source:tiles",
        shape=(8, 8, 4),
        tile_shape=(4, 4),
        levels=1,
        level_downsample=(1,),
        extent=(-1.0, 1.0, -1.0, 1.0),
    )


def test_tiled_image_extension_manifest_is_static_metadata():
    manifest = tiled_image_extension_manifest()

    assert manifest.id == "gsp.tiled-image"
    assert manifest.version == "0.1"
    assert manifest.capability == TILED_IMAGE_EXTENSION_CAPABILITY
    assert extension_capability(manifest.id, manifest.version) == TILED_IMAGE_EXTENSION_CAPABILITY
    assert manifest.implementations["matplotlib"] == "reference"
    assert manifest.implementations["datoviz"] == "unsupported"
    assert manifest.fallback_policy == "reject"
    assert validate_extension_manifest(manifest) is manifest


def test_extension_manifest_rejects_non_static_or_misnamespaced_contracts():
    with pytest.raises(ValueError, match="dot-separated"):
        ExtensionManifest(id="BadExtension", version="0.1", kind=ExtensionKind.DATA_SOURCE, title="Bad")

    with pytest.raises(ValueError, match="numeric"):
        ExtensionManifest(id="gsp.bad", version="v1", kind=ExtensionKind.DATA_SOURCE, title="Bad")

    with pytest.raises(ValueError, match="query payload"):
        ExtensionManifest(
            id="gsp.bad",
            version="0.1",
            kind=ExtensionKind.QUERY_PAYLOAD,
            title="Bad",
            query_contract={"payload": "other@0.1.query"},
        )


def test_tiled_image_source_rejects_executable_credentials_and_remote_fetch():
    with pytest.raises(ValueError, match="credential_policy=none"):
        TiledImageSource(
            id="source:bad-credentials",
            shape=(8, 8, 4),
            tile_shape=(4, 4),
            credential_policy=CredentialPolicy.PRECONFIGURED,
        )

    with pytest.raises(ValueError, match="synthetic/in-memory"):
        TiledImageSource(
            id="source:bad-locality",
            shape=(8, 8, 4),
            tile_shape=(4, 4),
            locality=DataLocality.SERVER_FETCH,
        )


def test_fake_tiled_provider_returns_direct_numpy_tile_and_mosaic():
    source = _source()
    provider = FakeTiledImageProvider(source)

    tile = provider.get_tile(TileRequest(source_id=source.id, tile=TileIndex(level=0, x=1, y=1)))
    mosaic = provider.get_viewport_mosaic(
        ViewportTileRequest(source_id=source.id, level=0, source_rect=(2, 2, 4, 4))
    )

    assert tile.data is not None
    assert tile.data.shape == (4, 4, 4)
    np.testing.assert_array_equal(tile.data[0, 0], [4, 4, 0, 255])
    np.testing.assert_array_equal(tile.data[-1, -1], [7, 7, 0, 255])
    assert mosaic.data.shape == (4, 4, 4)
    np.testing.assert_array_equal(mosaic.data[0, 0], [2, 2, 0, 255])
    assert [index for index in mosaic.tile_indices] == [
        TileIndex(level=0, x=0, y=0),
        TileIndex(level=0, x=1, y=0),
        TileIndex(level=0, x=0, y=1),
        TileIndex(level=0, x=1, y=1),
    ]


def test_fake_tiled_provider_clips_partial_edge_mosaic_deterministically():
    source = _source()
    provider = FakeTiledImageProvider(source)

    mosaic = provider.get_viewport_mosaic(
        ViewportTileRequest(source_id=source.id, level=0, source_rect=(-2, -1, 5, 6))
    )

    assert mosaic.source_rect == (0, 0, 3, 5)
    assert mosaic.data.shape == (5, 3, 4)
    np.testing.assert_array_equal(mosaic.data[0, 0], [0, 0, 0, 255])
    np.testing.assert_array_equal(mosaic.data[-1, -1], [2, 4, 0, 255])
    assert [index for index in mosaic.tile_indices] == [
        TileIndex(level=0, x=0, y=0),
        TileIndex(level=0, x=0, y=1),
    ]


def test_capability_snapshot_advertises_tiled_image_extension_support():
    caps = CapabilitySnapshot(
        server_name="matplotlib-reference",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        extensions=(TILED_IMAGE_EXTENSION_CAPABILITY,),
        supports_extension_manifests=True,
        supports_virtual_data_sources=True,
        supports_tiled_image_sources=True,
        supports_synthetic_data_sources=True,
        max_tiles_per_request=256,
        max_mosaic_pixels=4096,
    )

    assert caps.supports_extension(TILED_IMAGE_EXTENSION_CAPABILITY)
    assert caps.adapt_extension(TILED_IMAGE_EXTENSION_CAPABILITY).outcome == AdaptationOutcome.ACCEPT
    assert caps.adapt_extension_manifest(tiled_image_extension_manifest()).outcome == AdaptationOutcome.ACCEPT
    rejected = caps.adapt_extension("gsp.remote-fetch@0.1")
    assert rejected.outcome == AdaptationOutcome.REJECT
    assert rejected.diagnostic is not None


def test_capability_snapshot_rejects_unadvertised_static_extension_manifest():
    manifest = tiled_image_extension_manifest()
    caps = CapabilitySnapshot(
        server_name="minimal",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        supports_extension_manifests=True,
    )

    rejected = caps.adapt_extension_manifest(manifest)

    assert rejected.outcome == AdaptationOutcome.REJECT
    assert "gsp.tiled-image@0.1" in rejected.diagnostic


def test_tiled_image_source_validates_static_manifest_linkage():
    source = _source()
    manifest = tiled_image_extension_manifest()

    source.validate_manifest_link(manifest)
    validate_tiled_image_source_manifest_link(source, manifest)

    with pytest.raises(ValueError, match="extension_version"):
        source_with_wrong_version = TiledImageSource(
            id="source:tiles",
            shape=(8, 8, 4),
            tile_shape=(4, 4),
            extension_version="0.2",
        )
        source_with_wrong_version.validate_manifest_link(manifest)

    with pytest.raises(ValueError, match="source_kind"):
        source.validate_manifest_link(
            ExtensionManifest(
                id="gsp.tiled-image",
                version="0.1",
                kind=ExtensionKind.DATA_SOURCE,
                title="Broken tiled image manifest",
                schema={"source_kind": "other", "credential_policy": "none"},
            )
        )


def test_matplotlib_reference_renders_tiled_viewport_mosaic():
    source = _source()
    provider = FakeTiledImageProvider(source)
    fig, ax = plt.subplots()
    try:
        artist = render_tiled_image_source(
            ax,
            source,
            provider,
            source_rect=(2, 2, 4, 4),
            extent=(-1.0, 1.0, -1.0, 1.0),
            visual_id="visual:tiled-image",
        )

        assert artist.get_gid() == "visual:tiled-image"
        assert artist.get_array().shape == (4, 4, 4)
        np.testing.assert_array_equal(artist.get_array()[0, 0], [2, 2, 0, 255])
    finally:
        plt.close(fig)


def test_matplotlib_reference_renders_clipped_tiled_mosaic_at_clipped_extent():
    source = _source()
    provider = FakeTiledImageProvider(source)
    fig, ax = plt.subplots()
    try:
        artist = render_tiled_image_source(
            ax,
            source,
            provider,
            source_rect=(-2, -2, 4, 4),
            extent=(-1.0, 1.0, -1.0, 1.0),
            visual_id="visual:tiled-image",
        )

        assert artist.get_array().shape == (2, 2, 4)
        assert tuple(artist.get_extent()) == (0.0, 1.0, -1.0, 0.0)
        np.testing.assert_array_equal(artist.get_array()[0, 0], [0, 0, 0, 255])
        np.testing.assert_array_equal(artist.get_array()[-1, -1], [1, 1, 0, 255])
    finally:
        plt.close(fig)


def test_tiled_image_query_reports_tile_and_source_coordinates():
    source = _source()
    provider = FakeTiledImageProvider(source)

    result = query_tiled_image_source(
        QueryRequest(id="query:tiled", panel_id="panel:main", coordinate=(0.25, 0.25)),
        source,
        provider,
        source_rect=(2, 2, 4, 4),
        extent=(-1.0, 1.0, -1.0, 1.0),
        visual_id="visual:tiled-image",
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "visual:tiled-image"
    assert result.texel == (3, 4)
    assert result.value == (4, 3, 0, 255)
    assert result.displayed_rgba == (4 / 255.0, 3 / 255.0, 0.0, 1.0)
    assert result.extension_payload_kind == TILED_IMAGE_QUERY_PAYLOAD_KIND
    assert isinstance(result.extension_payload, TiledImageQueryPayload)
    assert result.extension_payload.source_id == "source:tiles"
    assert result.extension_payload.tile_x == 1
    assert result.extension_payload.tile_y == 0
    assert result.extension_payload.texel_x == 0
    assert result.extension_payload.texel_y == 3


def test_tiled_image_query_uses_clipped_extent_for_partial_edge_source_rect():
    source = _source()
    provider = FakeTiledImageProvider(source)

    outside_rendered = query_tiled_image_source(
        QueryRequest(id="query:tiled-edge-miss", panel_id="panel:main", coordinate=(-0.5, 0.5)),
        source,
        provider,
        source_rect=(-2, -2, 4, 4),
        extent=(-1.0, 1.0, -1.0, 1.0),
        visual_id="visual:tiled-image",
    )
    inside_rendered = query_tiled_image_source(
        QueryRequest(id="query:tiled-edge-hit", panel_id="panel:main", coordinate=(0.25, -0.25)),
        source,
        provider,
        source_rect=(-2, -2, 4, 4),
        extent=(-1.0, 1.0, -1.0, 1.0),
        visual_id="visual:tiled-image",
    )

    assert outside_rendered.status == QueryStatus.MISS
    assert inside_rendered.status == QueryStatus.HIT
    assert inside_rendered.texel == (0, 0)
    assert inside_rendered.value == (0, 0, 0, 255)
    assert isinstance(inside_rendered.extension_payload, TiledImageQueryPayload)
    assert inside_rendered.extension_payload.source_x == 0
    assert inside_rendered.extension_payload.source_y == 0
    assert inside_rendered.extension_payload.tile_x == 0
    assert inside_rendered.extension_payload.tile_y == 0


def test_tiled_image_query_miss_uses_existing_non_hit_semantics():
    source = _source()
    provider = FakeTiledImageProvider(source)

    result = query_tiled_image_source(
        QueryRequest(id="query:tiled-miss", panel_id="panel:main", coordinate=(2.0, 2.0)),
        source,
        provider,
        source_rect=(0, 0, 4, 4),
        extent=(-1.0, 1.0, -1.0, 1.0),
    )

    assert result.status == QueryStatus.MISS
    assert not result.hit
    assert result.extension_payload is None


def test_query_result_requires_extension_payload_kind_and_value_together():
    with pytest.raises(ValueError, match="provided together"):
        QueryResult(
            request_id="query:bad-extension",
            status=QueryStatus.HIT,
            hit=True,
            panel_coordinate=(0.0, 0.0),
            extension_payload_kind=TILED_IMAGE_QUERY_PAYLOAD_KIND,
        )
