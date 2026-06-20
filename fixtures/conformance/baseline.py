"""In-process fixtures for the GSP v0.1 conformance baseline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from gsp.protocol import (
    BufferResource,
    CapabilitySnapshot,
    ImageOrigin,
    ImageVisual,
    PointVisual,
    QueryRequest,
    ResourceUsage,
    TransportKind,
)
from gsp_matplotlib.protocol_query import QueryVisualEntry


@dataclass(frozen=True, slots=True)
class ConformanceScene:
    """Point-over-image conformance scene with direct protocol objects."""

    point: PointVisual
    image: ImageVisual
    query: QueryRequest
    entries: tuple[QueryVisualEntry, ...]


def point_visual_fixture() -> PointVisual:
    """Return the canonical v0.1 point visual fixture."""
    return PointVisual(
        id="visual:point-fixture",
        positions=np.array([[0.25, 0.25], [-0.5, -0.5]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255], [0, 0, 255, 255]], dtype=np.uint8),
        sizes=np.array([0.25, 0.09], dtype=np.float32),
    )


def image_visual_fixture() -> ImageVisual:
    """Return the canonical v0.1 image visual fixture."""
    return ImageVisual(
        id="visual:image-fixture",
        image=np.array(
            [
                [[10, 20, 30, 255], [40, 50, 60, 255]],
                [[70, 80, 90, 255], [100, 110, 120, 255]],
            ],
            dtype=np.uint8,
        ),
        extent=(-1.0, 1.0, -1.0, 1.0),
        origin=ImageOrigin.UPPER,
    )


def point_over_image_scene() -> ConformanceScene:
    """Return a point-over-image query scene for reference conformance."""
    point = point_visual_fixture()
    image = image_visual_fixture()
    query = QueryRequest(id="query:point-over-image", panel_id="panel:main", coordinate=(0.25, 0.25))
    return ConformanceScene(
        point=point,
        image=image,
        query=query,
        entries=(QueryVisualEntry(image, z_order=0), QueryVisualEntry(point, z_order=1)),
    )


def capability_snapshot_fixture() -> CapabilitySnapshot:
    """Return the v0.1 reference capability snapshot fixture."""
    return CapabilitySnapshot(
        server_name="gsp-v0.1-reference",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        buffer_dtypes=("float32", "float64", "uint8", "rgba8"),
        texture_formats=("rgba8", "float32"),
        visual_families=("point", "image"),
        query_modes=("panel-query", "point-item", "image-texel"),
        output_formats=("matplotlib-artist",),
        deterministic=True,
        metadata={"fixture": "v0.1-conformance"},
    )


def position_buffer_resource_fixture() -> BufferResource:
    """Return a direct-memory buffer fixture for the local in-process path."""
    positions = point_visual_fixture().positions
    return BufferResource(
        id="buffer:point-positions",
        dtype="float32",
        shape=positions.shape,
        byte_length=positions.nbytes,
        usage=(ResourceUsage.ATTRIBUTE,),
        data=memoryview(positions),
    )
