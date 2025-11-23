# typing imports
from typing import Sequence, TypedDict, Literal
import json
import warnings

# pip imports
import requests
from http_constants.status import HttpStatus

# local imports
from gsp.types.renderer_base import RendererBase
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.types.transbuf import TransBuf
from gsp_pydantic.serializer import PydanticSerializer
from gsp_pydantic.types.pydantic_dict import PydanticDict


###############################################################################
#   Type for the network payload
#
class NetworkPayload(TypedDict):
    renderer_name: Literal["matplotlib", "datoviz"]
    data: PydanticDict


class NetworkRenderer(RendererBase):
    def __init__(self, canvas: Canvas, server_base_url: str, remote_renderer_name: Literal["matplotlib", "datoviz"] = "matplotlib") -> None:
        self._canvas = canvas
        self._server_base_url = server_base_url
        self._remote_renderer_name: Literal["matplotlib", "datoviz"] = remote_renderer_name

    def get_canvas(self) -> Canvas:
        return self._canvas

    def close(self) -> None:
        warnings.warn(f"Closing NetworkRenderer does not release any resources.", UserWarning)

    def get_remote_renderer_name(self) -> Literal["matplotlib", "datoviz"]:
        return self._remote_renderer_name

    def render(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
    ) -> bytes:

        # =============================================================================
        #
        # =============================================================================
        pydanticSerializer = PydanticSerializer(self._canvas)
        pydantic_scene_dict = pydanticSerializer.serialize(
            viewports=viewports,
            visuals=visuals,
            model_matrices=model_matrices,
            cameras=cameras,
        )

        payload: NetworkPayload = {
            "renderer_name": self._remote_renderer_name,
            "data": pydantic_scene_dict,
        }

        # =============================================================================
        # do network request
        # =============================================================================
        # Send the POST request with JSON data
        call_url = f"{self._server_base_url}/render"
        headers = {"Content-Type": "application/json"}
        response = requests.post(call_url, data=json.dumps(payload), headers=headers)

        # =============================================================================
        #
        # =============================================================================

        # Check the response status
        if response.status_code != HttpStatus.OK:
            raise Exception(f"Request failed with status code {response.status_code}")

        # return png data as bytes
        image_png_data = response.content
        return image_png_data
