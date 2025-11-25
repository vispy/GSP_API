# typing imports
import io
import os
from typing import Sequence, TypedDict, Literal
import json
import warnings

# pip imports
import requests
from http_constants.status import HttpStatus
import numpy as np
import matplotlib.pyplot
import matplotlib.image
import matplotlib.animation
import matplotlib.artist
import matplotlib.figure

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
    """
    Note: this requires a running gsp_network server. See the README for instructions.
    IMPORTANT: it DOES NOT depends on GSP matplotlib renderer, it only uses pip matplotlib to display the remotely rendered images.
    """

    def __init__(self, canvas: Canvas, server_base_url: str, remote_renderer_name: Literal["matplotlib", "datoviz"] = "matplotlib") -> None:
        self._canvas = canvas
        self._server_base_url = server_base_url
        self._remote_renderer_name: Literal["matplotlib", "datoviz"] = remote_renderer_name

        # Create a figure
        figure_width = self._canvas.get_width() / self._canvas.get_dpi()
        figure_height = self._canvas.get_height() / self._canvas.get_dpi()
        self._figure: matplotlib.figure.Figure = matplotlib.pyplot.figure(figsize=(figure_width, figure_height), dpi=self._canvas.get_dpi())
        assert self._figure.canvas.manager is not None, f"matplotlib figure canvas manager is None"
        self._figure.canvas.manager.set_window_title(f"Network ({self._remote_renderer_name})")

        # get the only axes in the figure
        self._mpl_axes = self._figure.add_axes((0, 0, 1, 1))
        # hide the borders
        self._mpl_axes.axis("off")

        # create an np.array to hold the image
        image_data_np = np.zeros((self._canvas.get_height(), self._canvas.get_width(), 3), dtype=np.uint8)
        self._axes_image = self._mpl_axes.imshow(image_data_np)

    def get_canvas(self) -> Canvas:
        return self._canvas

    def close(self) -> None:
        #
        pass

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
        # Serialize the scene and create the payload
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
        # do network request to send the payload and get the rendered image
        # =============================================================================
        # Send the POST request with JSON data
        call_url = f"{self._server_base_url}/render"
        headers = {"Content-Type": "application/json"}
        response = requests.post(call_url, data=json.dumps(payload), headers=headers)

        # Check the response status
        if response.status_code != HttpStatus.OK:
            raise Exception(f"Request failed with status code {response.status_code}")
        image_png_data = response.content

        # =============================================================================
        # Render the image in the matplotlib figure
        # =============================================================================
        assert self._axes_image is not None, f"PANIC self._axes_image is None"
        # update the image data
        image_data_io = io.BytesIO(image_png_data)
        image_data_np = matplotlib.image.imread(image_data_io, format="png")
        self._axes_image.set_data(image_data_np)

        # return png data as bytes
        return image_png_data

    def show(self) -> None:
        # handle non-interactive mode for tests
        inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
        if inTest:
            return

        matplotlib.pyplot.show()
        # self._figure.show()

    def get_mpl_figure(self) -> matplotlib.figure.Figure:
        return self._figure
