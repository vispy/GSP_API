"""Render item definition."""

# stdlib imports
from dataclasses import dataclass

# local imports
from gsp.core.viewport import Viewport
from gsp.core.camera import Camera
from gsp.types.visual_base import VisualBase
from gsp.types.buffer import Buffer


@dataclass
class RenderItem:
    """Render item is a dataclasss containing all necessary information for rendering a visual in a viewport."""

    viewport: Viewport
    """Viewport where the visual will be rendered."""
    visual_base: VisualBase
    """Visual to be rendered."""
    model_matrix: Buffer
    """Model matrix for transforming the visual."""
    camera: Camera
    """Camera used for rendering the visual."""
