#!/usr/bin/env python3
"""
Server example using Flask to render a scene from JSON input.

- use Flask to create a simple web server
- render with matplotlib or datoviz based on environment variable
"""

# stdlib imports
import io
import os
from typing import Literal
import typing

# pip imports
from flask import Flask, request, send_file, Response
import argparse
import colorama

# local imports
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_pydantic.serializer.pydantic_parser import PydanticParser
from gsp_pydantic.types.pydantic_dict import PydanticDict
from gsp_network.renderer.network_renderer import NetworkPayload

flask_app = Flask(__name__)


# =============================================================================
# Colorama alias
# =============================================================================
def text_cyan(text: str) -> str:
    return colorama.Fore.CYAN + text + colorama.Style.RESET_ALL


# =============================================================================
# flask callback
# =============================================================================
@flask_app.route("/render", methods=["POST"])
def render_scene_json() -> Response:
    payload: NetworkPayload = request.get_json()

    # Log the received payload for debugging
    print(f"Received payload")

    ###############################################################################
    # Load the scene from JSON
    #

    pydanticDict: PydanticDict = payload["data"]

    pydanticParser = PydanticParser()
    parsed_canvas, parsed_viewports, parsed_visuals, parsed_model_matrices, parsed_cameras = pydanticParser.parse(pydanticDict)

    ###############################################################################
    # Render the loaded scene with matplotlib or datoviz based on environment variable
    #
    renderer_name = payload["renderer_name"]
    if renderer_name == "matplotlib":
        renderer = MatplotlibRenderer(parsed_canvas)
    else:
        renderer = DatovizRenderer(parsed_canvas, offscreen=True)
    image_png_data = renderer.render(parsed_viewports, parsed_visuals, parsed_model_matrices, parsed_cameras, return_image=True)

    print(f"Rendered image size: {text_cyan(str(len(image_png_data)))} bytes")

    ###############################################################################
    # Return the rendered image as a PNG file
    #
    return send_file(
        io.BytesIO(image_png_data),
        mimetype="image/png",
        as_attachment=True,
        download_name="rendered_scene.png",
    )


# =============================================================================
#
# =============================================================================


class ServerSample:
    """
    Sample class to demonstrate server functionality.
    """

    def __init__(self):
        pass

    def run(self):
        flask_app.run(threaded=False, debug=False)  # Enable debug mode if desired


#######################################################################################

if __name__ == "__main__":
    argParser = argparse.ArgumentParser(
        description="Run the network server for rendering. see ./examples/network_client.py for usage.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    args = argParser.parse_args()

    server = ServerSample()
    server.run()
