# pip imports
from pydantic import BaseModel


class PydanticBuffer(BaseModel):
    count: int
    buffer_type: str
    data: bytes


class PydanticTransformChain(BaseModel):
    pass


class PydanticTransBuf(BaseModel):
    pass


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


class PydanticVisualBase(BaseModel):
    uuid: str


class PydanticModelMatrix(BaseModel):
    model_matrix: PydanticTransBuf


class PydanticCamera(BaseModel):
    uuid: str
    view_matrix: PydanticTransBuf
    projection_matrix: PydanticTransBuf


class PydanticScene(BaseModel):
    canvas: PydanticCanvas
    viewports: list[PydanticViewport]
    visuals: list[PydanticVisualBase]
    model_matrices: list[PydanticModelMatrix]
    cameras: list[PydanticCamera]
