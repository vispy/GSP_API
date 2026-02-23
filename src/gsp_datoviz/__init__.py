"""GSP Datoviz package."""

from . import animator
from . import renderer
from . import utils
from . import viewport_events

# =============================================================================
# Register network renderer into GSP
# =============================================================================
from .renderer_registration import register_renderer_datoviz

register_renderer_datoviz()
