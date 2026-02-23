"""GSP Matplotlib package initialization."""

__all__ = ["animator", "extra", "renderer", "utils", "viewport_events"]

from . import animator
from . import extra
from . import renderer
from . import utils
from . import viewport_events


# =============================================================================
# Register matplotlib renderer into GSP
# =============================================================================
from .renderer_registration import register_renderer_matplotlib

register_renderer_matplotlib()
