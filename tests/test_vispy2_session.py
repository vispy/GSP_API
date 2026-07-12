"""Focused tests for the bounded experimental Datoviz session preview."""

from __future__ import annotations

from typing import Any

import pytest

from gsp.protocol import CapabilitySnapshot, TransportKind
import gsp_vispy2 as vp
import gsp_vispy2.session as session_module


class FakeRenderer:
    instances: list["FakeRenderer"] = []
    fail_init = False
    fail_add_point = False
    fail_show = False

    def __init__(self, **kwargs: Any) -> None:
        if self.__class__.fail_init:
            raise RuntimeError("native renderer creation failed")
        self.kwargs = kwargs
        self.calls: list[tuple[object, ...]] = []
        self.closed = False
        self.__class__.instances.append(self)

    def configure_view2d_axes(self, view: object, **kwargs: Any) -> None:
        self.calls.append(("axes", view, kwargs))

    def add_point_visual(self, visual: object) -> None:
        if self.__class__.fail_add_point:
            raise RuntimeError("native point attachment failed")
        self.calls.append(("point", visual))

    def add_marker_visual(self, visual: object) -> None:
        self.calls.append(("marker", visual))

    def add_segment_visual(self, visual: object) -> None:
        self.calls.append(("segment", visual))

    def add_path_visual(self, visual: object) -> None:
        self.calls.append(("path", visual))

    def add_image_visual(self, visual: object) -> None:
        self.calls.append(("image", visual))

    def add_text_visual(self, visual: object) -> None:
        self.calls.append(("text", visual))

    def add_mesh_visual(self, visual: object) -> None:
        self.calls.append(("mesh", visual))

    def add_colorbar_guide(self, guide: object) -> None:
        self.calls.append(("colorbar", guide))

    def show(self, *, frame_count: int) -> None:
        if self.__class__.fail_show:
            raise RuntimeError("native app execution failed")
        self.calls.append(("show", frame_count))

    def close(self) -> None:
        self.calls.append(("close",))
        self.closed = True


@pytest.fixture(autouse=True)
def fake_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeRenderer.instances.clear()
    FakeRenderer.fail_init = False
    FakeRenderer.fail_add_point = False
    FakeRenderer.fail_show = False
    capabilities = CapabilitySnapshot(
        server_name="datoviz-test",
        protocol_versions=("0.2",),
        transports=(TransportKind.INPROC,),
    )
    monkeypatch.setattr(session_module, "_renderer_factory", FakeRenderer)
    monkeypatch.setattr(session_module, "_capability_loader", lambda: capabilities)


def _figure() -> vp.Figure:
    figure, axes = vp.subplots()
    axes.scatter([0.0, 1.0], [1.0, 0.0])
    return figure


def test_open_session_inspects_capabilities_without_creating_renderer() -> None:
    with vp.open_session("datoviz") as session:
        inspection = session.inspect(_figure(), operation="display")
        assert inspection.executable
        assert inspection.capabilities.server_name == "datoviz-test"
        inspection.require_executable()
        assert FakeRenderer.instances == []


def test_bounded_blocking_show_owns_and_closes_display() -> None:
    with vp.open_session("datoviz") as session:
        display = session.show(_figure(), block=True, frame_count=2)
        renderer = FakeRenderer.instances[-1]
        assert display.backend == "datoviz"
        assert display.blocking is True
        assert ("show", 2) in renderer.calls
        assert not display.closed
    assert display.closed
    assert renderer.closed


def test_explicit_nonblocking_display_polls_exactly_one_frame() -> None:
    session = vp.open_session("datoviz")
    display = session.show(_figure(), block=False)
    renderer = FakeRenderer.instances[-1]
    assert not any(call[0] == "show" for call in renderer.calls)
    session.poll(display)
    session.poll(display)
    assert [call for call in renderer.calls if call[0] == "show"] == [
        ("show", 1),
        ("show", 1),
    ]
    session.close()


def test_close_is_idempotent_and_all_operations_reject_after_close() -> None:
    session = vp.open_session("datoviz")
    display = session.show(_figure(), block=False)
    session.close()
    session.close()
    renderer = FakeRenderer.instances[-1]
    assert renderer.calls.count(("close",)) == 1
    with pytest.raises(vp.SessionLifecycleError, match="session is closed"):
        session.inspect(_figure())
    with pytest.raises(vp.SessionLifecycleError, match="session is closed"):
        session.show(_figure())
    with pytest.raises(vp.SessionLifecycleError, match="session is closed"):
        session.poll(display)


def test_multiple_axes_reject_before_renderer_execution_with_diagnostic() -> None:
    figure = vp.Figure()
    figure.add_axes()
    figure.add_axes()
    with vp.open_session("datoviz") as session:
        plan = session.inspect(figure)
        assert not plan.executable
        assert plan.diagnostics[0].code == "session.figure.multiple_axes_unsupported"
        with pytest.raises(vp.SessionExecutionError, match="at most one axes"):
            session.show(figure)
    assert FakeRenderer.instances == []


def test_poll_rejects_foreign_and_blocking_displays() -> None:
    first = vp.open_session("datoviz")
    second = vp.open_session("datoviz")
    display = first.show(_figure(), block=False)
    with pytest.raises(ValueError, match="not owned"):
        second.poll(display)
    blocking = first.show(_figure(), block=True)
    with pytest.raises(ValueError, match="block=False"):
        first.poll(blocking)
    first.close()
    second.close()


def test_renderer_creation_failure_is_normalized_with_diagnostic() -> None:
    FakeRenderer.fail_init = True
    with vp.open_session("datoviz") as session:
        with pytest.raises(vp.SessionExecutionError, match="creation failed"):
            session.show(_figure())
        assert session.diagnostics[-1].code == "session.backend.preparation_failed"


def test_partial_attachment_failure_closes_renderer_and_is_normalized() -> None:
    FakeRenderer.fail_add_point = True
    with vp.open_session("datoviz") as session:
        with pytest.raises(vp.SessionExecutionError, match="attachment failed"):
            session.show(_figure())
        renderer = FakeRenderer.instances[-1]
        assert renderer.closed
        assert renderer.calls[-1] == ("close",)
        assert session.diagnostics[-1].code == "session.backend.preparation_failed"


def test_blocking_and_poll_failures_are_normalized_and_owned() -> None:
    FakeRenderer.fail_show = True
    with vp.open_session("datoviz") as session:
        with pytest.raises(vp.SessionExecutionError, match="execution failed"):
            session.show(_figure(), block=True)
        blocking_renderer = FakeRenderer.instances[-1]
        assert blocking_renderer.closed
        assert session.diagnostics[-1].code == "session.backend.execution_failed"

        display = session.show(_figure(), block=False)
        with pytest.raises(vp.SessionExecutionError, match="execution failed"):
            session.poll(display)
        assert not display.closed
        assert session.diagnostics[-1].code == "session.backend.poll_failed"
    assert display.closed


def test_context_exception_closes_multiple_owned_displays() -> None:
    with pytest.raises(RuntimeError, match="application failure"):
        with vp.open_session("datoviz") as session:
            first = session.show(_figure(), block=False)
            second = session.show(_figure(), block=False)
            raise RuntimeError("application failure")
    assert first.closed
    assert second.closed
    assert all(renderer.closed for renderer in FakeRenderer.instances)


def test_bare_figure_show_remains_matplotlib(monkeypatch: pytest.MonkeyPatch) -> None:
    figure = _figure()
    sentinel = (object(), object())
    monkeypatch.setattr(vp.Figure, "render_matplotlib", lambda self: sentinel)
    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None)
    assert figure.show() == sentinel
