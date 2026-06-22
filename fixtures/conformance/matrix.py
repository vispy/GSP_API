"""Backend conformance matrix for the current fixture replay layer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from gsp_datoviz.query import datoviz_v04_query_binding_diagnostics

from .replay import InProcessReplayResult, replay_conformance_fixtures


BackendConformanceStatus = Literal["pass", "skip"]


@dataclass(frozen=True, slots=True)
class BackendConformanceExpectation:
    """Expected conformance outcome for one backend in the current S018 replay layer."""

    backend_id: str
    status: BackendConformanceStatus
    reason: str
    replay: Callable[[], InProcessReplayResult] | None = None


def backend_conformance_matrix() -> tuple[BackendConformanceExpectation, ...]:
    """Return the explicit backend replay expectations for the current baseline."""
    return (
        BackendConformanceExpectation(
            backend_id="matplotlib",
            status="pass",
            reason="Matplotlib is the deterministic reference/conformance backend.",
            replay=replay_conformance_fixtures,
        ),
        BackendConformanceExpectation(
            backend_id="datoviz",
            status="skip",
            reason=_datoviz_skip_reason(),
        ),
    )


def _datoviz_skip_reason() -> str:
    try:
        import datoviz as dvz  # type: ignore[import-untyped]
    except ModuleNotFoundError:
        return "Datoviz is not importable; runtime conformance replay is deferred."

    diagnostics = datoviz_v04_query_binding_diagnostics(dvz)
    if diagnostics:
        return "Datoviz query binding is not ready for conformance replay: " + "; ".join(diagnostics)
    return (
        "Datoviz query binding is ready, but S018 conformance replay still needs a backend adapter "
        "with stable application visual-id mapping and guide/tiled-source expectations."
    )
