# stdlib imports
from typing import Sequence, Any

# local imports
from gsp.types.serializer_base import SerializerBase
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.core.camera import Camera
from gsp.types.transbuf import TransBuf
from .pydantic_types import PydanticCanvas, PydanticViewport, PydanticVisualBase, PydanticModelMatrix, PydanticCamera, PydanticScene
from .pydantic_types import PydanticTransBuf, PydanticBuffer, PydanticTransformChain


# =============================================================================
#
# =============================================================================
class PydanticSerializer(SerializerBase):

    def __init__(self, canvas: Canvas):
        self._canvas = canvas

    def serialize(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
    ) -> dict[str, Any]:

        # =============================================================================
        #
        # =============================================================================

        pydanticCanvas = PydanticCanvas(
            uuid=self._canvas.get_uuid(),
            width=self._canvas.get_width(),
            height=self._canvas.get_height(),
            dpi=self._canvas.get_dpi(),
        )
        pydanticViewports = [
            PydanticViewport(
                uuid=viewport.get_uuid(),
                x=viewport.get_x(),
                y=viewport.get_y(),
                width=viewport.get_width(),
                height=viewport.get_height(),
            )
            for viewport in viewports
        ]
        pydantic_visuals = PydanticSerializer._visuals_to_pydantic(visuals)
        pydantic_model_matrices = [PydanticModelMatrix(model_matrix=PydanticSerializer._transbuf_to_pydantic(model_matrix)) for model_matrix in model_matrices]
        pydantic_cameras = [
            PydanticCamera(
                uuid=camera.get_uuid(),
                view_matrix=PydanticSerializer._transbuf_to_pydantic(camera.get_view_matrix()),
                projection_matrix=PydanticSerializer._transbuf_to_pydantic(camera.get_projection_matrix()),
            )
            for camera in cameras
        ]

        # =============================================================================
        #
        # =============================================================================

        pydantic_scene = PydanticScene(
            canvas=pydanticCanvas,
            viewports=pydanticViewports,
            visuals=pydantic_visuals,
            model_matrices=pydantic_model_matrices,
            cameras=pydantic_cameras,
        )

        json_dict = pydantic_scene.model_dump()

        # Implement JSON rendering logic here
        return json_dict  # Placeholder for JSON byte output

    # =============================================================================
    # Static methods
    # =============================================================================

    @staticmethod
    def _transbuf_to_pydantic(transbuf: TransBuf) -> PydanticTransBuf:
        return PydanticTransBuf()  # Placeholder implementation

    @staticmethod
    def _visuals_to_pydantic(visuals: Sequence[VisualBase]) -> list[PydanticVisualBase]:
        pydantic_visuals: list[PydanticVisualBase] = []
        for vis in visuals:
            pydantic_visuals.append(PydanticVisualBase(uuid=vis.get_uuid()))
        return pydantic_visuals
