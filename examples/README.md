# GSP_API Examples

This directory contains example scripts demonstrating the features and capabilities of the GSP_API visualization library. All examples work with both **Matplotlib** and **DatoViz** backends.

## Quick Start

Run any example with your preferred backend:

```bash
# Using Matplotlib (default)
GSP_BACKEND=matplotlib python examples/example_name.py

# Using DatoViz
GSP_BACKEND=datoviz python examples/example_name.py
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
| `texts_example.py` | Text rendering and typography | Adding and styling text in visualizations |
| `texts_animated_example.py` | Animated text elements | Text animation and dynamic updates |

### 3D and Camera Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `object3d_example.py` | Rendering 3D objects and models | 3D object visualization and manipulation |
| `camera_control_example.py` | Interactive camera control and navigation | Camera manipulation and viewport control |
| `transform_visual_example.py` | Visual transforms and coordinate systems | Coordinate transformation visualization |
| `transform_serialization_example.py` | Saving and loading transform state | Transform persistence and serialization |

### Advanced Examples

| File | Description | Demonstrates |
|------|-------------|--------------|
| `animator_example.py` | Creating animations with the Animator | Dynamic animations with keyframes |
| `session_record_example.py` | Recording visualization sessions | Capturing and exporting visualization data |
| `session_player_example.py` | Replaying recorded sessions | Playback and analysis of recorded sessions |
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
GSP_BACKEND=matplotlib python examples/points_example.py
```

### With Arguments

Many examples support command-line arguments. Check the script for details:

```bash
python examples/example_name.py --help
```

### Testing Both Backends

Create a quick test script:

```bash
for backend in matplotlib datoviz; do
  echo "Testing with $backend..."
  GSP_BACKEND=$backend python examples/points_example.py
done
```

---

## Key Concepts Across Examples

### Backend Independence
All examples are written to work with both Matplotlib and DatoViz backends. The backend is selected via the `GSP_BACKEND` environment variable at import time.

### Common Pattern
Most examples follow this pattern:

```python
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
import numpy as np

# Create canvas and viewport
canvas = Canvas()
viewport = Viewport()

# Create data
data = np.random.randn(1000, 2)

# Create visual
points = Points(data)
viewport.add_visual(points)

# Show result
canvas.show()
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
3. **Test both backends**: Ensure it works with Matplotlib and DatoViz
4. **Keep it focused**: Demonstrate one feature clearly
5. **Add comments**: Explain non-obvious code
6. **Update this README**: Add the example to the appropriate category

Use the `docs-examples-gsp` skill to help create examples:

```bash
docs-examples-gsp  # or ask: "Create an example showing..."
```

---

## Troubleshooting

### Backend Import Errors
If you get "DatoViz not available", the optional backend may not be installed:

```bash
pip install datoviz
```

### Display Issues
Some examples require a display server. If running headless, they may output to files instead.

### Performance
Large examples may be slow depending on your hardware. Use smaller datasets for quick testing.

---

## Resources

- **Main Documentation**: See `../docs/` for full API documentation
- **API Reference**: Check docstrings in `../src/gsp/`
- **Testing**: Run `test-validate-gsp` to validate examples work correctly
- **Contributing**: See main README for contribution guidelines
