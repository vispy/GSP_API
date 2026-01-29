""" "Pydantic models for GSP data types."""

# stdlib imports
from typing import Literal, Union, Any

# pip imports
from pydantic import BaseModel

# =============================================================================
#
# =============================================================================


class PydanticBuffer(BaseModel):
    """Pydantic model representing a buffer with encoded data.

    This class stores buffer data in a serializable format using base64 encoding.
    """

    count: int
    """number of elements in the buffer"""
    buffer_type: str
    """type of the buffer elements, corresponds to BufferType enum value"""
    data_base64: str
    """data encoded in base64 format"""


class PydanticTransformChain(BaseModel):
    """Pydantic model representing a chain of transformations.

    Contains a dictionary representing the transformation chain configuration.
    """

    transform_chain: dict[str, Any]


class PydanticTransBuf(BaseModel):
    """Pydantic model for a transform buffer union type.

    Can represent either a buffer or a transform chain, discriminated by the type field.
    """

    type: Literal["buffer", "transform_chain"]
    transBuf: PydanticBuffer | PydanticTransformChain


# =============================================================================
#
# =============================================================================

PydanticGroups = Union[int, list[int], list[list[int]]]
"""Type alias for groups which can be an int, a list of ints, or a list of list of ints."""


# =============================================================================
#
# =============================================================================


class PydanticCanvas(BaseModel):
    """Pydantic model representing a canvas for rendering.

    Defines the rendering surface with dimensions and resolution.
    """

    uuid: str
    width: int
    height: int
    dpi: float


class PydanticViewport(BaseModel):
    """Pydantic model representing a viewport region.

    Defines a rectangular viewing area within the canvas.
    """

    uuid: str
    x: int
    y: int
    width: int
    height: int


class PydanticModelMatrix(BaseModel):
    """Pydantic model representing a model transformation matrix.

    Contains the transformation matrix for positioning objects in the scene.
    """

    model_matrix: PydanticTransBuf


class PydanticCamera(BaseModel):
    """Pydantic model representing a camera.

    Defines the camera's view and projection transformations for rendering the scene.
    """

    uuid: str
    view_matrix: PydanticTransBuf
    projection_matrix: PydanticTransBuf


class PydanticTexture(BaseModel):
    """Pydantic model representing a texture.

    Contains pixel data and its dimensions.
    """

    uuid: str
    data: PydanticTransBuf
    width: int
    height: int


# =============================================================================
#
# =============================================================================


class PydanticImage(BaseModel):
    """Pydantic model representing image visual elements.

    Images are 2D arrays of pixel data with configurable position, extent, and interpolation.
    """

    uuid: str
    position: PydanticTransBuf
    image_extent: tuple[float, float, float, float]
    texture: PydanticTexture
    interpolation: str


class PydanticMarkers(BaseModel):
    """Pydantic model representing marker visual elements.

    Markers are geometric shapes (circles, squares, etc.) positioned in space
    with configurable appearance properties.
    """

    uuid: str
    marker_shape: str
    positions: PydanticTransBuf
    sizes: PydanticTransBuf
    face_colors: PydanticTransBuf
    edge_colors: PydanticTransBuf
    edge_widths: PydanticTransBuf


class PydanticPaths(BaseModel):
    """Pydantic model representing path visual elements.

    Paths are continuous lines or curves with configurable line styles and colors.
    """

    uuid: str
    positions: PydanticTransBuf
    path_sizes: PydanticTransBuf
    colors: PydanticTransBuf
    line_widths: PydanticTransBuf
    cap_style: str
    join_style: str


class PydanticPixels(BaseModel):
    """Pydantic model representing pixel visual elements.

    Pixels are individual colored points organized into groups.
    """

    uuid: str
    positions: PydanticTransBuf
    colors: PydanticTransBuf
    groups: PydanticGroups


class PydanticPoints(BaseModel):
    """Pydantic model representing point visual elements.

    Points are circular elements with configurable size and appearance,
    including face color, edge color, and edge width.
    """

    uuid: str
    positions: PydanticTransBuf
    sizes: PydanticTransBuf
    face_colors: PydanticTransBuf
    edge_colors: PydanticTransBuf
    edge_widths: PydanticTransBuf


class PydanticSegments(BaseModel):
    """Pydantic model representing line segment visual elements.

    Segments are individual line segments with configurable width, color, and cap style.
    """

    uuid: str
    positions: PydanticTransBuf
    line_widths: PydanticTransBuf
    cap_style: str
    colors: PydanticTransBuf


class PydanticTexts(BaseModel):
    """Pydantic model representing text visual elements.

    Text elements with configurable position, font properties, colors, and orientation.
    """

    uuid: str
    positions: PydanticTransBuf
    texts: list[str]
    colors: PydanticTransBuf
    font_sizes: PydanticTransBuf
    anchors: PydanticTransBuf
    angles: PydanticTransBuf
    font_name: str


class PydanticVisual(BaseModel):
    """Pydantic model for a visual element union type.

    Discriminated union that can represent any of the visual element types,
    distinguished by the type field.
    """

    type: Literal["image", "markers", "paths", "pixels", "points", "segments", "texts"]
    visual: PydanticImage | PydanticMarkers | PydanticPaths | PydanticPixels | PydanticPoints | PydanticSegments | PydanticTexts


# =============================================================================
#
# =============================================================================


class PydanticScene(BaseModel):
    """Pydantic model representing a complete scene.

    Aggregates all scene elements including canvas, viewports, visual elements,
    transformation matrices, and cameras.
    """

    canvas: PydanticCanvas
    viewports: list[PydanticViewport]
    visuals: list[PydanticVisual]
    model_matrices: list[PydanticModelMatrix]
    cameras: list[PydanticCamera]
