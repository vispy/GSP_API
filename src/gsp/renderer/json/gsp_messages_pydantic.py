from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic.dataclasses import dataclass

@dataclass 
class GspMessage:
    message_id: int
    """id is increasing integer identifier for each message"""
    command_name: str

# =============================================================================
# Canvas
# =============================================================================

@dataclass
class CanvasCreate(GspMessage):
    canvas_uuid: str
    """unique identifier for the canvas"""
    width: int
    """width of the canvas in pixels"""
    height: int
    """height of the canvas in pixels"""
    dpi: float
    """dots per inch (DPI) of the canvas"""

@dataclass
class CanvasSetDpi(GspMessage):
    canvas_uuid: str
    """unique identifier for the canvas"""
    dpi: float
    """dots per inch (DPI) of the canvas"""

@dataclass
class CanvasSetSize(GspMessage):
    canvas_uuid: str
    """unique identifier for the canvas"""
    width: int
    """width of the canvas in pixels"""
    height: int
    """height of the canvas in pixels"""

# =============================================================================
# Viewport
# =============================================================================

@dataclass
class ViewportCreate(GspMessage):
    viewport_uuid: str
    """unique identifier for the viewport"""
    canvas_uuid: str
    """unique identifier for the parent canvas"""
    x: int
    """x position of the viewport"""
    y: int
    """y position of the viewport"""
    width: int
    """width of the viewport"""
    height: int
    """height of the viewport"""

@dataclass
class ViewportSetPosition(GspMessage):
    viewport_uuid: str
    """unique identifier for the viewport"""
    x: int
    """x position of the viewport"""
    y: int
    """y position of the viewport"""

@dataclass
class ViewportSetSize(GspMessage):
    viewport_uuid: str
    """unique identifier for the viewport"""
    width: int
    """width of the viewport"""
    height: int
    """height of the viewport"""

# =============================================================================
# 
# =============================================================================


@dataclass
class TransformLink(GspMessage):
    ...

@dataclass
class TransformLinkOperator(TransformLink):
    operator: Literal['add', 'sub', 'mul', 'div']
    """operator to apply between the two operands"""
    operand: float | int
    """second operand for the operation"""

@dataclass
class Transform(GspMessage):
    transform_uuid: str
    """unique identifier for the transform"""
    links: list[TransformLink]
    """list of links defining the transform"""


# =============================================================================
# Buffer
# =============================================================================
class BufferType(Enum):
    """Type of elements in a Buffer"""
    int32 = 'int32'
    float32 = 'float32'
    float64 = 'float64'

@dataclass
class Buffer(GspMessage):
    """typed array of a single dimension"""
    buffer_uuid: str
    """unique identifier for the buffer"""
    count: int
    """number of elements of <type> in the buffer"""
    type: BufferType
    """type of each elements in the buffer"""
    data: bytes
    """Contiguous byte array representing the buffer data"""

TransBuffer = Transform | Buffer

# =============================================================================
# Visual
# =============================================================================
@dataclass
class Visual(GspMessage):
    visual_uuid: str
    """unique identifier for the visual"""

@dataclass
class Points(Visual):
    positions: TransBuffer
    """Transform or Buffer representing point positions"""
    sizes: TransBuffer
    """Transform or Buffer representing point sizes"""
    face_colors: TransBuffer
    """Transform or Buffer representing point face colors"""
    edge_colors: TransBuffer
    """Transform or Buffer representing point edge colors"""
    edge_widths: TransBuffer
    """Transform or Buffer representing point edge widths"""
    groups: TransBuffer
    """Transform or Buffer representing point groups"""