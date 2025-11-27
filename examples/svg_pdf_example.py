# stdlib imports
import os
import pathlib

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Paths
from gsp.types import Buffer, BufferType, CapStyle, JoinStyle
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.cmap_utils import CmapUtils


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(512, 512, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    # Generate multiple polylines (for example, 3 sine waves with offsets)

    def generate_lines(line_count: int, points_per_line: int):
        lines_positions = []
        lines_colors = []
        lines_widths = []

        for line_index in range(line_count):
            x = np.linspace(-0.9, +0.9, points_per_line)
            y = np.sin(x * 10 + line_index * 0.3) / line_count + line_index * 1.4 / line_count  # vertical offset for each line
            y -= 0.7
            z = np.zeros_like(x)
            # Make color vary along the line (map y to color)
            colors_values = CmapUtils.get_color_map_numpy("plasma", y)

            # Vary linewidth by slope magnitude
            gradients = np.abs(np.gradient(y))
            gradients_normalized = (gradients - gradients.min()) / (gradients.max() - gradients.min())
            line_width = 1 + 10.0 * gradients_normalized

            # Build vertex positions for this line
            line_positions = (np.array([x, y, z]).T).tolist()

            lines_positions.append(line_positions)
            lines_colors.append(colors_values.tolist())
            lines_widths.append(line_width)

        return lines_positions, lines_colors, lines_widths

    num_lines = 10
    points_per_line = 300
    vertex_positions, vertex_colors, line_widths = generate_lines(num_lines, points_per_line)

    # =============================================================================
    #
    # =============================================================================

    # Random positions - Create buffer from numpy array
    positions_numpy = np.array(vertex_positions, dtype=np.float32).reshape(-1, 3)
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    path_sizes_numpy = np.array([points_per_line for line in range(num_lines)], dtype=np.uint32)
    path_sizes_buffer = Bufferx.from_numpy(path_sizes_numpy, BufferType.uint32)

    # all pixels red - Create buffer and fill it with a constant
    colors_numpy = np.array(vertex_colors, dtype=np.float32).reshape(-1, 4)
    colors_buffer = Bufferx.from_numpy(colors_numpy, BufferType.rgba8)

    line_widths_numpy = np.array(line_widths, dtype=np.float32).reshape(-1, 1)
    line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

    # Create the Pixels visual and add it to the viewport
    paths = Paths(positions_buffer, path_sizes_buffer, colors_buffer, line_widths_buffer, CapStyle.ROUND, JoinStyle.ROUND)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # Create a renderer
    renderer = MatplotlibRenderer(canvas)

    # =============================================================================
    # Render to PNG
    # =============================================================================

    # render the scene
    rendered_image_png = renderer.render([viewport], [paths], [model_matrix], [camera], image_format="png")

    # Save the rendered image to a PNG file
    example_basename = pathlib.Path(__file__).stem
    output_png_path = pathlib.Path(__file__).parent / "output" / f"{example_basename}_output.png"
    with open(output_png_path, "wb") as file_writer:
        file_writer.write(rendered_image_png)
    print(f"Saved rendered PNG image to: {output_png_path}")

    # =============================================================================
    # Render to PDF
    # =============================================================================

    rendered_image_pdf = renderer.render([viewport], [paths], [model_matrix], [camera], image_format="pdf")

    # Save the rendered image to a PDF file
    output_pdf_path = pathlib.Path(__file__).parent / "output" / f"{example_basename}_output.pdf"
    with open(output_pdf_path, "wb") as file_writer:
        file_writer.write(rendered_image_pdf)
    print(f"Saved rendered PDF image to: {output_pdf_path}")

    # =============================================================================
    # Render to SVG
    # =============================================================================

    rendered_image_svg = renderer.render([viewport], [paths], [model_matrix], [camera], image_format="svg")
    # Save the rendered image to a SVG file
    output_svg_path = pathlib.Path(__file__).parent / "output" / f"{example_basename}_output.svg"
    with open(output_svg_path, "wb") as file_writer:
        file_writer.write(rendered_image_svg)
    print(f"Saved rendered SVG image to: {output_svg_path}")


if __name__ == "__main__":
    main()
