import numpy as np

from gsp_extra.camera_controls.window_event_base import WindowEventBase
from gsp_extra.camera_controls.window_event_types import KeyboardEvent, MouseEvent, EventType
from gsp.types.visual_base import VisualBase
from gsp.types.buffer import Buffer
from gsp.types.buffer_type import BufferType
from .. import glm
from ..bufferx import Bufferx


class ObjectControlAwsd:
    """Implements camera controls using AWSD keys for movement and mouse for orientation."""

    def __init__(self, model_matrix_buffer: Buffer, window_event: WindowEventBase):
        # sanity checks
        assert model_matrix_buffer.get_type() == BufferType.mat4, "model_matrix must be of type mat4"
        assert model_matrix_buffer.get_count() == 1, "model_matrix must have a count of 1"

        # copy arguments
        self._model_matrix_buffer = model_matrix_buffer
        self._model_matrix_numpy = Bufferx.to_numpy(self._model_matrix_buffer)[0]
        self._window_event = window_event
        self._speed_x = 0.1
        self._speed_z = 0.1

        # Subscribe to keyboard and mouse events
        self._window_event.key_press_event.subscribe(self._on_key_event)
        self._window_event.key_release_event.subscribe(self._on_key_event)

    def close(self):
        self._window_event.key_press_event.unsubscribe(self._on_key_event)
        self._window_event.key_release_event.unsubscribe(self._on_key_event)

    def _on_key_event(self, keyboard_event: KeyboardEvent):
        if keyboard_event.event_type == EventType.KEY_PRESS:
            translate_vector = np.array([0, 0, 0], dtype=np.float32)

            if keyboard_event.key_name == "w":
                translate_vector[2] -= self._speed_z
            elif keyboard_event.key_name == "s":
                translate_vector[2] += self._speed_z
            elif keyboard_event.key_name == "a":
                translate_vector[0] -= self._speed_x
            elif keyboard_event.key_name == "d":
                translate_vector[0] += self._speed_x

            # generate translate matrix
            translate_matrix = glm.translate(translate_vector)
            # update model_matrix_numpy
            self._model_matrix_numpy = np.matmul(translate_matrix, self._model_matrix_numpy)
            # update model_matrix_buffer
            self._model_matrix_buffer.set_data(bytearray(self._model_matrix_numpy.tobytes()), 0, 1)
