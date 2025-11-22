import numpy as np

from gsp_extra.camera_controls.window_event_base import WindowEventBase
from gsp_extra.camera_controls.window_event_types import KeyboardEvent, MouseEvent, EventType
from gsp.types.visual_base import VisualBase
from gsp.types.buffer import Buffer
from gsp.types.buffer_type import BufferType
from .. import glm
from ..bufferx import Bufferx
from .trackball import Trackball


class ObjectControlsTrackball:
    """Implements camera controls using AWSD keys for movement and mouse for orientation."""

    def __init__(self, model_matrix_buffer: Buffer, window_event: WindowEventBase):
        # sanity checks
        assert model_matrix_buffer.get_type() == BufferType.mat4, "model_matrix must be of type mat4"
        assert model_matrix_buffer.get_count() == 1, "model_matrix must have a count of 1"

        # copy arguments
        self._model_matrix_buffer = model_matrix_buffer
        self._model_matrix_numpy = Bufferx.to_numpy(self._model_matrix_buffer)[0]
        self._window_event = window_event
        self._trackball = Trackball()

        # Subscribe to keyboard and mouse events
        self._window_event.button_press_event.subscribe(self._on_button_press)
        self._window_event.button_release_event.subscribe(self._on_button_release)
        self._window_event.mouse_move_event.subscribe(self._on_mouse_move)

    def close(self):
        self._window_event.button_press_event.unsubscribe(self._on_button_press)
        self._window_event.button_release_event.unsubscribe(self._on_button_release)
        self._window_event.mouse_move_event.unsubscribe(self._on_mouse_move)

    def _on_button_press(self, event: MouseEvent):
        pass

    def _on_button_release(self, event: MouseEvent):
        pass

    def _on_mouse_move(self, event: MouseEvent):
        pass
