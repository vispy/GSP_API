# Pyramid data visualization for neural signals
# This implements a multi-resolution image pyramid for efficient viewing of large electrophysiology datasets
# The pyramid allows smooth zooming by loading appropriate resolution levels on demand

from pathlib import Path
from typing import Optional, Tuple, Dict
import numpy as np
import numpy.typing as npt
import datoviz as dvz  # Datoviz graphics library for high-performance visualization

from datoviz._panel import Panel as _DvzPanel  # TODO _panel to fix in datoviz ?
from datoviz._figure import Figure as _DvzFigure
from datoviz._texture import Texture as _DvzTexture
from datoviz.visuals import Visual as _DvzVisual
from datoviz._axes import Axes as _DvzAxes
from datoviz._event import Event as _DvzEvent
from datoviz.interact import Panzoom

# Configuration constants
n_channels: int = 384  # Number of recording channels (typical for Neuropixels probes)
sample_rate: int = 2500  # Sampling rate in Hz
data_dtype: type = np.float16  # Data type for memory-efficient storage
value_min: float = -5e-4  # Minimum value for data normalization
value_max: float = +5e-4  # Maximum value for data normalization
texture_size: int = 2048  # Maximum texture size in pixels (GPU texture limit)
max_resolution: int = 11  # Maximum resolution level in the pyramid (2^11 = 2048x downsampling)


# Global data storage
# bounds: Dict[int, Tuple[int, int]] = {}  # Unused: could store bounds for each resolution level
files: Dict[int, Optional[np.memmap]] = {}  # Cache for memory-mapped files at different resolution levels


def file_path_build(resolution_level: int) -> Path:
    """Generate file path for a given resolution level.

    Args:
        resolution_level: Resolution level (0 = full resolution, higher = more downsampled)

    Returns:
        Path to the binary data file for this resolution
    """
    CUR_DIR: Path = Path(__file__).resolve().parent  # Directory containing this script
    return Path(CUR_DIR / f"../pyramid/res_{resolution_level:02d}.bin")


def load_file(resolution_level: int) -> Optional[np.memmap]:
    """Load a memory-mapped array from disk for a given resolution level.

    Memory mapping allows efficient access to large files without loading them entirely into RAM.
    The data is stored as float16 (2 bytes per value) with shape (n_samples, n_channels).

    Args:
        resolution_level: Resolution level to load

    Returns:
        Memory-mapped numpy array of shape (n_samples, n_channels), or None if file doesn't exist
    """
    file_path = file_path_build(resolution_level)
    if not file_path.exists():
        return
    file_size = file_path.stat().st_size  # Get file size in bytes
    assert file_size % (n_channels * 2) == 0  # Verify file size is consistent (2 bytes per float16)
    n_samples = int(round(file_size / (n_channels * 2)))  # Calculate number of time samples
    array_numpy = np.memmap(file_path, shape=(n_samples, n_channels), dtype=data_dtype, mode="r")
    print(f"Memmap file with shape {array_numpy.shape}")
    return array_numpy


def safe_slice(data: npt.NDArray, i0: int, i1: int, fill_value: float = 0.0) -> npt.NDArray:
    """Extract a slice from data with bounds checking and padding.

    Unlike standard array slicing, this handles indices that are out of bounds
    by filling those regions with a specified value. This is useful when requesting
    data near the edges of the available dataset.

    Args:
        data: Input array to slice from
        i0: Start index (can be negative)
        i1: End index (can exceed array length)
        fill_value: Value to use for out-of-bounds regions

    Returns:
        Array of length (i1-i0) with data from valid regions and fill_value elsewhere
    """
    n = i1 - i0  # Requested length
    shape = (n,) + data.shape[1:]  # Output shape preserves other dimensions
    result = np.full(shape, fill_value, dtype=data.dtype)  # Initialize with fill value

    # Calculate valid slice bounds within the data array
    s0 = max(i0, 0)  # Start index clamped to valid range
    s1 = min(i1, data.shape[0])  # End index clamped to valid range

    # Calculate where to place the valid data in the result
    d0 = s0 - i0  # Offset in destination array
    d1 = d0 + (s1 - s0)  # End offset in destination array

    result[d0:d1] = data[s0:s1]  # Copy valid data
    return result


def load_data(resolution_level: int, sample_index_start: int, sample_index_end: int) -> Optional[npt.NDArray[np.uint8]]:
    """Load and normalize a time slice of data at a specific resolution level.

    This function:
    1. Loads the appropriate resolution level file (if not cached)
    2. Extracts the requested time range
    3. Normalizes values to 0-255 for GPU texture upload

    Args:
        resolution_level: Resolution level (0 = full resolution, higher = more downsampled)
        sample_index_start: Start sample index at this resolution
        sample_index_end: End sample index at this resolution

    Returns:
        Uint8 array of shape (i1-i0, n_channels) suitable for GPU texture, or None if no data
    """
    assert sample_index_start < sample_index_end
    # Load file if not already cached
    if resolution_level not in files:
        files[resolution_level] = load_file(resolution_level)
    data = files[resolution_level]
    if data is None or data.size == 0:
        return
    # Extract the requested time range with bounds checking
    out = safe_slice(data, sample_index_start, sample_index_end)
    if out.size == 0:
        return
    # Normalize to 0-255 range for texture upload
    vmin, vmax = (-5e-4, +5e-4)
    return dvz.to_byte(out, vmin, vmax)  # Convert float values to uint8


def find_indices(resolution_level: int, time_min: float, time_max: float) -> Tuple[int, int]:
    """Convert time range to sample indices at a specific resolution level.

    At resolution level 0, the sample rate is full (2500 Hz).
    At resolution level r, the effective sample rate is sample_rate / 2^r.
    This downsampling allows efficient viewing of large time ranges.

    Args:
        resolution_level: Resolution level (0-11)
        time_min: Start time in seconds
        time_max: End time in seconds

    Returns:
        Tuple (sample_index_min, sample_index_max) of sample indices at this resolution level
    """
    assert resolution_level >= 0
    assert resolution_level <= max_resolution
    # resolution_level, time_min, time_max  # Statement with no effect (could be removed)
    assert time_min < time_max
    # Convert time to sample index, accounting for downsampling at this resolution
    sample_index_min = int(round(time_min * sample_rate / 2.0**resolution_level))
    sample_index_max = int(round(time_max * sample_rate / 2.0**resolution_level))
    return sample_index_min, sample_index_max


# -------------------------------------------------------------------------------------------------
# GPU Texture and Visual Management
# -------------------------------------------------------------------------------------------------


def make_texture(app: dvz.App, width: int, height: int) -> _DvzTexture:
    """Create a GPU texture for displaying the signal data.

    The texture stores the 2D image of signals (time x channels) that will be
    rendered on the GPU. Single channel (grayscale) is sufficient.

    Args:
        app: Datoviz application instance
        width: Texture width (typically n_channels = 384)
        height: Texture height (typically tex_size = 2048)

    Returns:
        Datoviz texture object
    """
    texture = app.texture(ndim=2, shape=(width, height), n_channels=1, dtype=np.dtype(np.uint8))
    return texture


def make_visual(axes: _DvzAxes, x: float, y: float, w: float, h: float, texture: _DvzTexture, app: dvz.App) -> _DvzVisual:
    """Create a visual element for rendering the signal texture.

    This creates an image visual that displays the texture in the scene.
    The image is positioned in data coordinates but sized in NDC (Normalized Device Coordinates).

    Args:
        axes: Datoviz axes object for coordinate transformations
        x: X position in data coordinates (time)
        y: Y position in data coordinates (channel number)
        w: Width in NDC coordinates
        h: Height in NDC coordinates
        texture: GPU texture to display
        app: Datoviz application instance

    Returns:
        Datoviz image visual object
    """
    # Convert scalar coordinates to required 2D array format
    x_numpy = np.atleast_2d([x])
    y_numpy = np.atleast_2d([y])
    size = np.array([[w, h]])  # Size in NDC coordinates
    anchor = np.array([[-1.0, +1.0]])  # Top-left anchor point
    position = axes.normalize(x_numpy, y_numpy)  # Convert data coords to normalized coords

    visual = app.image(
        position=position,
        size=size,
        anchor=anchor,  # Anchor at top-left
        texture=texture,
        permutation=(1, 0),  # Transpose texture (swap width/height)
        rescale="rescale",  # Enable texture rescaling
        unit="ndc",  # Size specified in Normalized Device Coordinates
        mode="colormap",  # Apply colormap to grayscale data
        colormap="binary",  # Black-to-white colormap
    )
    return visual


def update_image(visual: _DvzVisual, texture: _DvzTexture, res: int, sample_index_min: int, sample_index_max: int) -> Optional[bool]:
    """Update the GPU texture with new data from the specified resolution and time range.

    This function:
    1. Loads the appropriate data slice
    2. Uploads it to the GPU texture
    3. Adjusts texture coordinates to show only the used portion of the texture

    Args:
        visual: Datoviz image visual to update
        texture: GPU texture to update
        res: Resolution level to load
        sample_index_min: Start sample index
        sample_index_max: End sample index

    Returns:
        True if successful, None if failed
    """
    if res < 0 or res > max_resolution:
        return None
    image = load_data(res, sample_index_min, sample_index_max)
    if image is None:
        print("Error loading data")
        return
    height, width = image.shape
    if height > texture_size:
        print("Texture too big")
        return None
    assert image.dtype == np.uint8
    assert width == n_channels
    assert height <= texture_size

    # Upload data to GPU texture
    texture.data(image)

    # Adjust texture coordinates to use only the filled portion
    # t represents the fraction of the texture height that contains data
    t = (sample_index_max - sample_index_min) / float(texture_size)
    texcoords = np.array([[0, 0, t, 1]], dtype=np.float32)  # (u0, v0, u1, v1)
    visual.set_texcoords(texcoords)

    return True


def get_extent(axes: _DvzAxes) -> Tuple[float, float, float, float]:
    """Get the visible extent with padding added horizontally.

    Adds 50% padding on each side of the time axis to enable smooth panning.
    This allows the texture to extend beyond the visible region.

    Args:
        axes: Datoviz axes object

    Returns:
        Tuple (xmin, xmax, ymin, ymax) of extended bounds
    """
    (xmin, xmax), (ymin, ymax) = axes.bounds()  # Get current visible bounds
    w = xmax - xmin  # Visible width
    k = 0.5  # Padding factor (50% on each side)
    xmin -= k * w  # Extend left
    xmax += k * w  # Extend right
    return (xmin, xmax, ymin, ymax)


def update_image_position(visual: _DvzVisual, axes: _DvzAxes) -> None:
    """Update the position and size of the image visual to match the current view.

    Recalculates the visual's position and size in NDC coordinates based on the
    current axes bounds. This ensures the texture is properly positioned and scaled.

    Args:
        visual: Datoviz image visual to update
        axes: Datoviz axes object with current view bounds
    """
    xmin, xmax, ymin, ymax = get_extent(axes)

    # Calculate size in NDC coordinates by normalizing corner points
    p = axes.normalize(np.array([[xmin], [xmax]]), np.array([[ymin], [ymax]]))
    w_ndc = p[1][0] - p[0][0]  # Width in NDC
    h_ndc = p[1][1] - p[0][1]  # Height in NDC

    # Position at top-left corner of the extended region
    x = np.array([[xmin]], dtype=np.float64)  # Left edge in data coords
    y = np.array([[n_channels]], dtype=np.float64)  # Top edge (max channel)
    size = np.array([[w_ndc, h_ndc]], dtype=np.float32)

    # Update visual with new position and size
    visual.set_data(position=axes.normalize(x, y), size=size)


# -------------------------------------------------------------------------------------------------
# Main Application Setup
# -------------------------------------------------------------------------------------------------
def main():
    """Main function to set up and run the pyramid data visualization application."""
    # Initial view parameters
    time_min: float
    time_max: float
    time_min, time_max = 1000.0, 1500.0  # Initial time window (seconds)
    current_resolution: int = 11  # Start at lowest resolution (most downsampled)

    # Create the Datoviz application and scene hierarchy
    app: dvz.App = dvz.App(background="white")  # Main application window
    figure: _DvzFigure = app.figure()  # Figure container
    panel: _DvzPanel = figure.panel()  # Panel for rendering
    panzoom: Panzoom = panel.panzoom(fixed="y")  # Enable pan/zoom with fixed Y axis (channels don't zoom)
    axes: _DvzAxes = panel.axes((time_min, time_max), (0, n_channels))  # Set up coordinate system

    # Create GPU texture and visual for displaying the signals
    texture: _DvzTexture = make_texture(app, n_channels, texture_size)
    visual: _DvzVisual = make_visual(axes, time_min, n_channels, 2.0, 2.0, texture, app=app)
    # Load and display initial data
    i0, i1 = find_indices(current_resolution, time_min, time_max)
    assert i1 - i0 <= texture_size  # Ensure data fits in texture
    update_image(visual, texture, current_resolution, i0, i1)
    panel.add(visual)  # Add visual to the panel

    @app.connect(figure)
    def on_frame(ev: _DvzEvent) -> None:
        """Frame callback for dynamic level-of-detail updates.

        This callback runs every frame and:
        1. Checks if the view has changed significantly (zoom or pan)
        2. Determines the appropriate resolution level for the current zoom
        3. Reloads data if resolution changed or view shifted significantly

        The pyramid approach ensures:
        - Zoomed out: use downsampled data (higher res level) - less detail, more time coverage
        - Zoomed in: use full resolution data (lower res level) - more detail, less time coverage
        """
        nonlocal current_resolution, time_min, time_max
        new_tmin, new_tmax, _, _ = get_extent(axes)

        # Find the appropriate resolution level for the current view
        # Start from full resolution (0) and increase until data fits in texture
        for new_res in range(0, max_resolution + 1):
            i0, i1 = find_indices(new_res, new_tmin, new_tmax)
            if i1 - i0 <= texture_size:  # Data fits in texture at this resolution
                break

        # Update texture if:
        # 1. Resolution changed (zoomed in/out significantly)
        # 2. Panned more than 25% of the visible width
        if new_res != current_resolution or np.abs((new_tmin - time_min) / (time_max - time_min)) > 0.25:
            i0, i1 = find_indices(new_res, new_tmin, new_tmax)
            if update_image(visual, texture, new_res, i0, i1) is None:
                return
            print(f"Update image, res {new_res}")
            update_image_position(visual, axes)  # Reposition the visual
            visual.update()  # Trigger visual refresh
            current_resolution = new_res  # Update current resolution
            time_min, time_max = new_tmin, new_tmax  # Update current time range

    # Run the application event loop
    app.run()  # Start interactive visualization
    app.destroy()  # Clean up resources when window is closed


# =============================================================================
#
# =============================================================================

if __name__ == "__main__":
    main()
