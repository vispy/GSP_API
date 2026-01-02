# stdlib imports
from dataclasses import dataclass

# local imports
from gsp.core.viewport import Viewport
from gsp.core.camera import Camera
from gsp.types.visual_base import VisualBase
from gsp.types.buffer import Buffer


@dataclass
class RenderItem:
    """Render item containing all necessary information for rendering a visual in a viewport."""

    viewport: Viewport
    visual_base: VisualBase
    model_matrix: Buffer
    camera: Camera
