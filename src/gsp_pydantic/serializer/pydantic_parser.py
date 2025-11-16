# stdlib imports
from typing import Sequence, Any
import typing
import base64
import json

# pip imports
import pydantic_core

# local imports
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.types.transbuf import TransBuf
from gsp.types.buffer import Buffer
from gsp.types.buffer_type import BufferType
from gsp.core.camera import Camera
from ..types.pydantic_types import PydanticCanvas, PydanticViewport, PydanticModelMatrix, PydanticCamera, PydanticScene
from ..types.pydantic_types import PydanticVisual, PydanticPixels
from ..types.pydantic_types import PydanticTransBuf, PydanticBuffer, PydanticTransformChain
from ..types.pydantic_dict import PydanticDict


class PydanticParser:
    def __init__(self):
        pass

    def parse(self, json_dict: PydanticDict) -> tuple[
        Canvas,
        Sequence[Viewport],
        Sequence[VisualBase],
        Sequence[TransBuf],
        Sequence[Camera],
    ]:

        json_str = json.dumps(json_dict, indent=4)
        pydantic_scene = PydanticScene.model_validate(pydantic_core.from_json(json_str, allow_partial=True))

        # =============================================================================
        # Parse Pydantic Canvas
        # =============================================================================
        pydantic_canvas = pydantic_scene.canvas
        canvas = Canvas(pydantic_canvas.width, pydantic_canvas.height, pydantic_canvas.dpi)
        canvas._uuid = pydantic_canvas.uuid

        # =============================================================================
        # Parse Pydantic Viewports
        # =============================================================================
        viewports: list[Viewport] = []  # Placeholder implementation
        for pydantic_viewport in pydantic_scene.viewports:
            viewport = Viewport(
                pydantic_viewport.x,
                pydantic_viewport.y,
                pydantic_viewport.width,
                pydantic_viewport.height,
            )
            viewport._uuid = pydantic_viewport.uuid
            viewports.append(viewport)

        # =============================================================================
        # Parse Pydantic Visuals
        # =============================================================================
        visuals = []  # Placeholder implementation

        # =============================================================================
        # Parse Pydantic Model Matrices
        # =============================================================================
        model_matrices: list[TransBuf] = []  # Placeholder implementation
        for pydantic_model_matrix in pydantic_scene.model_matrices:
            model_matrix = PydanticParser._pydantic_to_transbuf(pydantic_model_matrix.model_matrix)
            model_matrices.append(model_matrix)

        # =============================================================================
        # Parse Pydanticy Cameras
        # =============================================================================
        cameras: list[Camera] = []
        for pydantic_camera in pydantic_scene.cameras:
            view_matrix = PydanticParser._pydantic_to_transbuf(pydantic_camera.view_matrix)
            projection_matrix = PydanticParser._pydantic_to_transbuf(pydantic_camera.projection_matrix)
            camera = Camera(view_matrix, projection_matrix)
            camera._uuid = pydantic_camera.uuid
            cameras.append(camera)

        # =============================================================================
        # Return the renderer arguments
        # =============================================================================
        return canvas, viewports, visuals, model_matrices, cameras

    @staticmethod
    def _pydantic_to_transbuf(pydantic_transbuf: PydanticTransBuf) -> TransBuf:
        if pydantic_transbuf.type == "buffer":
            pydantic_buffer = typing.cast(PydanticBuffer, pydantic_transbuf.transBuf)
            count = pydantic_buffer.count
            buffer_type = BufferType[pydantic_buffer.buffer_type]
            buffer_data = bytearray(base64.b64decode(pydantic_buffer.data_base64))
            buffer = Buffer.from_bytearray(buffer_data, buffer_type)
            assert buffer.get_count() == count, f"Buffer count mismatch: expected {count}, got {buffer.get_count()}"
            return buffer
        elif pydantic_transbuf.type == "transform_chain":
            raise NotImplementedError("Parsing of TransformChain is not implemented yet.")
        else:
            raise ValueError(f"Unknown PydanticTransBuf type: {pydantic_transbuf.type}")
