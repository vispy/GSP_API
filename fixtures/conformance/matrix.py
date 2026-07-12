"""Backend conformance matrix for the current fixture replay layer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

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
            reason=(
                "Datoviz runtime conformance replay is deferred; capability probes are validated "
                "separately."
            ),
        ),
    )
