# stdlib imports
from typing import Literal, Union

# pip imports
from pydantic import BaseModel

# =============================================================================
#
# =============================================================================


class PydanticBuffer(BaseModel):
    count: int
    """number of elements in the buffer"""
    buffer_type: str
    """type of the buffer elements, corresponds to BufferType enum value"""
    data_base64: str
    """data encoded in base64 format"""


class PydanticTransformChain(BaseModel):
    pass


class PydanticTransBuf(BaseModel):
    type: Literal["buffer", "transformChain"]
    transBuf: PydanticBuffer | PydanticTransformChain


# =============================================================================
#
# =============================================================================

PydanticGroups = Union[int, list[int], list[list[int]]]

# =============================================================================
#
# =============================================================================


class PydanticPixels(BaseModel):
    uuid: str
    positions: PydanticTransBuf
    colors: PydanticTransBuf
    groups: PydanticGroups


class PydanticPoints(BaseModel):
    uuid: str
    positions: PydanticTransBuf
    sizes: PydanticTransBuf
    face_colors: PydanticTransBuf
    edge_colors: PydanticTransBuf
    edge_widths: PydanticTransBuf


class PydanticSegments(BaseModel):
    uuid: str
    positions: PydanticTransBuf
    line_widths: PydanticTransBuf
    cap_style: str
    colors: PydanticTransBuf


class PydanticVisual(BaseModel):
    type: Literal["pixels", "points", "segments"]
    visual: PydanticPixels | PydanticPoints | PydanticSegments


# =============================================================================
#
# =============================================================================


class PydanticCanvas(BaseModel):
    uuid: str
    width: int
    height: int
    dpi: float


class PydanticViewport(BaseModel):
    uuid: str
    x: int
    y: int
    width: int
    height: int


class PydanticModelMatrix(BaseModel):
    model_matrix: PydanticTransBuf


class PydanticCamera(BaseModel):
    uuid: str
    view_matrix: PydanticTransBuf
    projection_matrix: PydanticTransBuf


class PydanticScene(BaseModel):
    canvas: PydanticCanvas
    viewports: list[PydanticViewport]
    visuals: list[PydanticVisual]
    model_matrices: list[PydanticModelMatrix]
    cameras: list[PydanticCamera]
