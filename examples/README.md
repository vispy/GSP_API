# GSP_API Examples

This directory contains example scripts demonstrating the features and capabilities of the GSP_API visualization library. Most legacy examples use Matplotlib by default through `examples/common/example_helper.py`. Some also target the optional legacy Datoviz wrapper or the network renderer, and the `vispy2_protocol_*.py` examples exercise the newer protocol producer path.

## Quick Start

Run any example with your preferred backend:

```bash
# Using Matplotlib (default)
GSP_RENDERER=matplotlib python examples/example_name.py

# Using legacy Datoviz v0.3 wrapper support
GSP_RENDERER=datoviz-v03 python examples/example_name.py

# Using the network renderer with a Matplotlib remote backend
GSP_RENDERER=network GSP_REMOTE_RENDERER=matplotlib python examples/example_name.py
```

---

## Examples by Category

### Basic Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `buffer_example.py` | Buffer class usage and data management | How to create and manage GPU buffers |
| `simple_model_matrix.py` | Basic model matrix transformations | Applying transformations to visual elements |
| `transform_example.py` | Transform operation fundamentals | Basic transform operations on objects |
| `transform_build_sample.py` | Building and composing transforms | Creating complex transform chains |

### Visualization Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `points_example.py` | Rendering point clouds and scatter plots | Visualizing point data with custom styling |
| `markers_example.py` | Using markers for data visualization | Different marker types and customization |
| `segments_example.py` | Drawing line segments and connections | Creating line-based visualizations |
| `paths_example.py` | Rendering arbitrary paths and curves | Drawing complex geometric paths |
| `image_example.py` | Displaying images and raster data | Image rendering and texture mapping |
| `jupiter_image_function.py` | Function-style image generation | Building an image visual from generated data |
| `texts_example.py` | Text rendering and typography | Adding and styling text in visualizations |
| `texts_animated_example.py` | Animated text elements | Text animation and dynamic updates |
| `vispy2_protocol_scatter.py` | VisPy2 protocol scatter producer | High-level scatter API rendered through the protocol backend |
| `vispy2_protocol_marker.py` | VisPy2 protocol marker producer | Marker shapes, fills, strokes, and pixel sizes through the protocol backend |
| `vispy2_protocol_segment.py` | VisPy2 protocol segment producer | Independent stroked segments with width and cap semantics |
| `vispy2_protocol_path.py` | VisPy2 protocol path producer | Open multi-subpath polylines with cap/join semantics |
| `vispy2_protocol_image_scalar.py` | VisPy2 protocol scalar image producer | Scalar gray image with explicit clim through ImageVisual v1 |
| `protocol_color_mapping.py` | Protocol color mapping reference example | ColorScale, scalar visual encodings, and ColorbarGuide rendered through Matplotlib |
| `vispy2_protocol_color_mapping.py` | VisPy2 scalar color mapping producer | ColorScale, scalar image/point encodings, and ColorbarGuide through VisPy2 |
| `vispy2_protocol_imshow.py` | VisPy2 protocol image producer | High-level image API rendered through the protocol backend |
| `vispy2_protocol_point_over_image.py` | VisPy2 protocol overlay producer | Point/image composition through the protocol backend |
| `vispy2_protocol_guides.py` | VisPy2 protocol guide API | Scatter, image, limits, labels, title, ticks, and grid intent |

### 3D and Camera Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `object3d_example.py` | Rendering 3D objects and models | 3D object visualization and manipulation |
| `object3d_obj_example.py` | Loading and rendering OBJ models | OBJ mesh loading through the object hierarchy |
| `camera_control_example.py` | Interactive camera control and navigation | Camera manipulation and viewport control |
| `transform_visual_example.py` | Visual transforms and coordinate systems | Coordinate transformation visualization |
| `transform_serialization_example.py` | Saving and loading transform state | Transform persistence and serialization |

### Mesh Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `mesh_example.py` | Mesh rendering with selectable material modes | Geometry, material, camera, and light setup |
| `mesh_basic_example.py` | Basic mesh material rendering | Solid face color and wireframe edges |
| `mesh_normal_example.py` | Normal-based mesh material rendering | Face colors derived from view-space normals |
| `mesh_depth_example.py` | Depth-based mesh material rendering | Face colors derived from view-space depth |
| `mesh_phong_example.py` | Phong-shaded mesh rendering | Directional and ambient lighting |
| `mesh_textured_example.py` | Textured mesh rendering | Texture loading and mesh UV attributes |

### Advanced Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `animator_example.py` | Creating animations with the Animator | Dynamic animations with keyframes |
| `session_01_record_example.py` | Recording visualization sessions | Capturing and exporting visualization data |
| `session_02_player_example.py` | Replaying recorded sessions | Playback and analysis of recorded sessions |
| `network_client_example.py` | Network communication and remote visualization | Client-server visualization patterns |
| `pydantic_cycle_example.py` | Data validation with Pydantic | Type-safe data handling in visualizations |
| `svg_pdf_example.py` | Exporting to vector formats | SVG and PDF export capabilities |

### Viewport and Layout Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `viewport_events_example.py` | Handling viewport events and interactions | Mouse, keyboard, and resize events |
| `viewport_inch_matplotlib.py` | Matplotlib viewport sizing | Inch-based viewport configuration |
| `viewport_multi_example.py` | Multiple viewports in one scene | Multi-panel visualizations |
| `viewport_overlapping_example.py` | Overlapping viewport layouts | Complex viewport arrangements |
| `viewport_ndc_metric.py` | Normalized device coordinates | NDC coordinate system usage |

### Axes and Grid Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `vispy_axes_display_example.py` | Displaying coordinate axes | Axis visualization and labels |
| `vispy_axes_managed_example.py` | Managed axis systems | Automatic axis management |
| `vispy_axes_managed_multiple_example.py` | Multiple managed axes | Multi-axis layouts |
| `vispy_axes_panzoom_example.py` | Pan and zoom on axes | Interactive axis navigation |
| `vispy_axes_multiple_panzoom_example.py` | Multiple axes with pan/zoom | Multi-axis interaction |
| `vispy_axes_image_pyramid.py` | Image pyramids for efficient rendering | Level-of-detail image rendering |
| `vispy_plot_example.py` | Line plots and curves | 2D line plot visualization |
| `vispy_scatter_example.py` | Scatter plots and point clouds | Scatter plot rendering |

### Groups and Rendering Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `groups_example.py` | Visual grouping and organization | Organizing visuals into groups |
| `dynamic_groups_example.py` | Dynamic group management | Real-time group manipulation |
| `pixels_example.py` | Pixel-level rendering | Direct pixel manipulation |

### Specialized Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `vispy_basic_example.py` | Basic vispy canvas setup | Getting started with vispy |
| `vispy_imshow_example.py` | VisPy-style image display | Image display through the VisPy-inspired API |
| `_big_tester_example.py` | Large-scale performance testing | Stress testing with many elements |
| `_big_tester_cmdline.py` | Command-line performance testing | CLI-based testing framework |

### Image Pyramid Examples (Internal)

| File | Description | Demonstrates |
|------|-------------|--------------|
| `_axes_image_pyramid_*.py` | Various image pyramid implementations | Different LOD and tiling strategies |
| `_vispy_axes_managed_example_*.py` | Different axis management patterns | Various axis configuration approaches |

---

## Running Examples

### Single Example

```bash
GSP_RENDERER=matplotlib python examples/points_example.py
```

### With Arguments

Many examples support command-line arguments. Check the script for details:

```bash
python examples/example_name.py --help
```


### S023 Visual QA Pack

The S023 protocol visual-family review pack renders formal protocol scenes through Matplotlib and Datoviz v0.4 and writes contact sheets plus manual notes:

```bash
PYTHONPATH=../datoviz:. \
DYLD_LIBRARY_PATH=../datoviz/build/src \
DVZ_SHADERC_RUNTIME_LIBRARY=../datoviz/build/src/libshaderc_shared.dylib \
uv run python -m gsp.qa.visual run \
  --backends matplotlib,datoviz \
  --out artifacts/visual_qa/s023/latest-local \
  --run-id latest-local \
  --contact-sheet \
  --resolution 800x600
```

Inspect `artifacts/visual_qa/s023/latest-local/contact_sheets/s023_all_cases.png` and record decisions in `artifacts/visual_qa/s023/latest-local/manual_notes.yaml`. If Datoviz v0.4 is not active, use `--backends matplotlib` for a reference-only run.

### S026 Color Mapping Visual QA Pack

The S026 suite extends the protocol visual QA cases with scalar color mapping and colorbar scenes:

```bash
uv run python -m gsp.qa.visual run \
  --suite s026 \
  --backends matplotlib \
  --out artifacts/visual_qa/s026/latest-local \
  --run-id latest-local \
  --contact-sheet \
  --resolution 800x600
```

Inspect `artifacts/visual_qa/s026/latest-local/contact_sheets/s026_all_cases.png` for the Matplotlib reference output. Datoviz scalar color mapping remains capability-gated until the S026 Datoviz probe mission.

### Testing Optional Backends

Matplotlib is the default release-readiness path. If the optional legacy Datoviz wrapper is installed,
you can smoke-test an example against both local renderer names:

```bash
for backend in matplotlib datoviz-v03; do
  echo "Testing with $backend..."
  GSP_RENDERER=$backend python examples/points_example.py
done
```

---

## Key Concepts Across Examples

### Backend Selection
Examples that use `ExampleHelper` select their renderer with the `GSP_RENDERER` environment variable at runtime. Valid values are `matplotlib`, `datoviz-v03`, and `network`; network mode also reads `GSP_REMOTE_RENDERER` with `matplotlib` or `datoviz-v03`.

Matplotlib is the default and reference backend for the current legacy example helper. The legacy Datoviz wrapper is optional and installed with `pip install -e ".[datoviz-legacy]"`. Plain `datoviz` names the Datoviz v0.4 protocol backend used by the S023 visual QA and protocol demos, not the legacy renderer helper.

### Common Pattern
Most examples follow this pattern:

```python
import numpy as np

from common.example_helper import ExampleHelper
from gsp.constants import Constants
from gsp.core import Camera, Canvas, Viewport
from gsp.types import BufferType
from gsp.visuals import Points
from gsp_extra.bufferx import Bufferx

canvas = Canvas(width=256, height=256, dpi=127.5, background_color=Constants.Color.white)
viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height(), Constants.Color.transparent)

positions = Bufferx.from_numpy(np.array([[0.0, 0.0, 0.0]], dtype=np.float32), BufferType.vec3)
sizes = Bufferx.from_numpy(np.array([32.0], dtype=np.float32), BufferType.float32)
face_colors = Bufferx.from_numpy(np.array([[255, 0, 0, 255]], dtype=np.uint8), BufferType.rgba8)
edge_colors = Bufferx.from_numpy(np.array([[0, 0, 0, 255]], dtype=np.uint8), BufferType.rgba8)
edge_widths = Bufferx.from_numpy(np.array([1.0], dtype=np.float32), BufferType.float32)

points = Points(positions, sizes, face_colors, edge_colors, edge_widths)
model_matrix = Bufferx.mat4_identity()
camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

renderer_name = ExampleHelper.get_renderer_name()
renderer = ExampleHelper.create_renderer(renderer_name, canvas)
image = renderer.render([viewport], [points], [model_matrix], [camera])
ExampleHelper.save_output_image(image, f"minimal_points_{renderer_name}.png")
```

### Data Handling
Examples use `numpy` for efficient data handling and `Buffer` objects for GPU memory management.

### Event Handling
Interactive examples show how to handle:
- Mouse events (click, move, drag)
- Keyboard events
- Viewport resize events

---

## Creating New Examples

When creating a new example, follow these guidelines:

1. **Use descriptive names**: `example_<feature_name>.py` or `<feature>_example.py`
2. **Add docstrings**: Explain what the example demonstrates
3. **State backend coverage**: Verify Matplotlib, then note whether Datoviz or network is supported
4. **Keep it focused**: Demonstrate one feature clearly
5. **Add comments**: Explain non-obvious code
6. **Update this README**: Add the example to the appropriate category

---

## Troubleshooting

### Backend Import Errors
If you get "DatoViz not available", the optional legacy backend may not be installed:

```bash
pip install -e ".[datoviz-legacy]"
```

### Display Issues
Some examples require a display server. If running headless, they may output to files instead.

### Performance
Large examples may be slow depending on your hardware. Use smaller datasets for quick testing.

---

## Resources

- **Main Documentation**: See `../docs/` for full API documentation
- **API Reference**: Check docstrings in `../src/gsp/`
- **Testing**: Run `PYTHONPATH=. uv run pytest` to validate the test suite
- **Contributing**: See main README for contribution guidelines
