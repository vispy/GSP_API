from datetime import datetime as datetime
from enum import Enum
from typing import Literal

class GspMessage:
    message_id: int
    command_name: str

class CanvasCreate(GspMessage):
    canvas_uuid: str
    width: int
    height: int
    dpi: float

class CanvasSetDpi(GspMessage):
    canvas_uuid: str
    dpi: float

class CanvasSetSize(GspMessage):
    canvas_uuid: str
    width: int
    height: int

class ViewportCreate(GspMessage):
    viewport_uuid: str
    canvas_uuid: str
    x: int
    y: int
    width: int
    height: int

class ViewportSetPosition(GspMessage):
    viewport_uuid: str
    x: int
    y: int

class ViewportSetSize(GspMessage):
    viewport_uuid: str
    width: int
    height: int

class TransformLink(GspMessage): ...

class TransformLinkOperator(TransformLink):
    operator: Literal['add', 'sub', 'mul', 'div']
    operand: float | int

class Transform(GspMessage):
    transform_uuid: str
    links: list[TransformLink]

class BufferType(Enum):
    int32 = 'int32'
    float32 = 'float32'
    float64 = 'float64'

class Buffer(GspMessage):
    buffer_uuid: str
    count: int
    type: BufferType
    data: bytes
TransBuffer = Transform | Buffer

class Visual(GspMessage):
    visual_uuid: str

class Points(Visual):
    positions: TransBuffer
    sizes: TransBuffer
    face_colors: TransBuffer
    edge_colors: TransBuffer
    edge_widths: TransBuffer
    groups: TransBuffer
