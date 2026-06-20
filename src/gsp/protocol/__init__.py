"""Protocol spine for GSP sessions.

This package contains transport-independent protocol models. It is designed to
coexist with the legacy object graph while the protocol layer is introduced.
"""

from .capabilities import AdaptationDecision, AdaptationOutcome, CapabilitySnapshot, TransportKind
from .commands import CommandBatch, CommandKind, ProtocolCommand
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
    "ImageInterpolation",
    "ImageOrigin",
    "ImageVisual",
    "InitializeResult",
    "InProcessGSPServer",
    "InProcessTransport",
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
    "TransportKind",
    "VisualFamily",
    "new_id",
    "validate_id",
]
