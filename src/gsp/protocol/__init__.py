"""Protocol spine for GSP sessions.

This package contains transport-independent protocol models. It is designed to
coexist with the legacy object graph while the protocol layer is introduced.
"""

from .capabilities import AdaptationDecision, AdaptationOutcome, CapabilitySnapshot, TransportKind
from .commands import CommandBatch, CommandKind, ProtocolCommand
from .data_sources import (
    CredentialPolicy,
    DataLocality,
    DataSourceDescriptor,
    DataSourceKind,
    FakeTiledImageProvider,
    MaterializationPolicy,
    TileAvailability,
    TileEncoding,
    TileIndex,
    TileRequest,
    TileResult,
    TileStatus,
    TiledImageQueryPayload,
    TiledImageSource,
    ViewportMosaicResult,
    ViewportTileRequest,
)
from .extensions import (
    ExtensionKind,
    ExtensionManifest,
    ExtensionSupportLevel,
    TILED_IMAGE_EXTENSION_CAPABILITY,
    TILED_IMAGE_EXTENSION_ID,
    TILED_IMAGE_EXTENSION_VERSION,
    tiled_image_extension_manifest,
)
from .ids import ObjectRef, new_id, validate_id
from .query import QueryCoordinateSpace, QueryHitPolicy, QueryPayload, QueryRequest, QueryResult, QueryStatus, VisualFamily
from .resources import AttributeSource, BufferResource, ResourceLocality, ResourceMutability, ResourceUsage
from .transports import CommandResult, InProcessGSPServer, InProcessTransport, InitializeResult
from .visuals import CoordinateSpace, ImageInterpolation, ImageOrigin, ImageVisual, PointVisual

__all__ = [
    "AdaptationDecision",
    "AdaptationOutcome",
    "AttributeSource",
    "BufferResource",
    "CapabilitySnapshot",
    "CommandBatch",
    "CommandKind",
    "CommandResult",
    "CoordinateSpace",
    "CredentialPolicy",
    "DataLocality",
    "DataSourceDescriptor",
    "DataSourceKind",
    "ImageInterpolation",
    "ImageOrigin",
    "ImageVisual",
    "ExtensionKind",
    "ExtensionManifest",
    "ExtensionSupportLevel",
    "FakeTiledImageProvider",
    "InitializeResult",
    "InProcessGSPServer",
    "InProcessTransport",
    "MaterializationPolicy",
    "ObjectRef",
    "PointVisual",
    "ProtocolCommand",
    "QueryCoordinateSpace",
    "QueryHitPolicy",
    "QueryPayload",
    "QueryRequest",
    "QueryResult",
    "QueryStatus",
    "ResourceLocality",
    "ResourceMutability",
    "ResourceUsage",
    "TILED_IMAGE_EXTENSION_CAPABILITY",
    "TILED_IMAGE_EXTENSION_ID",
    "TILED_IMAGE_EXTENSION_VERSION",
    "TileAvailability",
    "TileEncoding",
    "TileIndex",
    "TileRequest",
    "TileResult",
    "TileStatus",
    "TiledImageQueryPayload",
    "TiledImageSource",
    "TransportKind",
    "ViewportMosaicResult",
    "ViewportTileRequest",
    "VisualFamily",
    "new_id",
    "tiled_image_extension_manifest",
    "validate_id",
]
