#!/usr/bin/env python3
"""Server example using Flask to render a scene from JSON input.

- use Flask to create a simple web server
- render with matplotlib or datoviz based on environment variable
"""
# stdlib imports
import io
import pathlib
from datetime import datetime

# pip imports
from flask import Flask, request, send_file, Response, typing
import argparse
import colorama
import pathlib

# local imports
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_pydantic.serializer.pydantic_parser import PydanticParser
from gsp_pydantic.types.pydantic_dict import PydanticDict
from gsp_network.renderer.network_renderer import NetworkPayload

flask_app = Flask(__name__)

debug_save_payload: bool = False
"""Enable saving of received payloads and rendered images for debugging."""
debug_save_serial: int = 0
"""Serial number for debug saved files."""


# =============================================================================
# Colorama alias
# =============================================================================
def text_cyan(text: str) -> str:
    """Return the given text string wrapped in ANSI escape codes for cyan color.

    Args:
        text (str): The text to color.

    Returns:
        str: The colored text string.
    """
    return colorama.Fore.CYAN + text + colorama.Style.RESET_ALL


# =============================================================================
# flask callback
# =============================================================================
@flask_app.route("/render", methods=["POST"])
def render_scene_json() -> Response:
    """Flask route to render a scene from JSON input.

    Returns:
        Response: Flask response containing the rendered PNG image.
    """
    payload: NetworkPayload = request.get_json()

    # Log the received payload for debugging
    print("Received payload")

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

    # =============================================================================
    # Save payload+image on debug
    # =============================================================================
    if debug_save_payload:
        global debug_save_serial

        # get path for payload+image
        debug_save_serial += 1
        basename = f"payload_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{debug_save_serial}"
        folder_path = pathlib.Path(__file__).parent / "network_server_debug"
        payload_path = folder_path / f"{basename}.json"
        image_path = folder_path / f"{basename}.png"

        # save payload
        # folder_path.mkdir(parents=True, exist_ok=True)
        with open(payload_path, "w") as payload_file:
            payload_file.write(request.get_data(as_text=True))
        print(f"Saved payload to: {text_cyan(str(payload_path))}")
        # save image
        with open(image_path, "wb") as image_file:
            image_file.write(image_png_data)
        print(f"Saved rendered image to: {text_cyan(str(image_path))}")

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
    """Sample class to demonstrate server functionality."""

    def __init__(self):
        """Initialize the server sample."""
        pass

    def run(self):
        """Run the Flask server."""
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
