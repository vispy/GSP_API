"""Deterministic reference tick resolution for semantic axis guides."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .guides import TickSpec, TickSpecKind


@dataclass(frozen=True, slots=True)
class ResolvedTicks:
    """Resolved tick values and labels for one axis guide."""

    values: tuple[float, ...]
    labels: tuple[str, ...]
    step: float | None
    source: TickSpecKind

    def __post_init__(self) -> None:
        if len(self.values) != len(self.labels):
            raise ValueError("resolved tick labels must match resolved tick values")


def resolve_ticks(tick_spec: TickSpec, data_range: tuple[float, float]) -> ResolvedTicks:
    """Resolve a semantic tick spec into deterministic tick values and labels."""
    start, end = _finite_range(data_range)
    if tick_spec.kind == TickSpecKind.NONE:
        return ResolvedTicks(values=(), labels=(), step=None, source=tick_spec.kind)
    if tick_spec.kind == TickSpecKind.EXPLICIT:
        labels = tick_spec.explicit_labels or tuple(_format_tick(value, None) for value in tick_spec.explicit_values)
        return ResolvedTicks(
            values=tuple(tick_spec.explicit_values),
            labels=tuple(labels),
            step=None,
            source=tick_spec.kind,
        )
    if tick_spec.kind == TickSpecKind.BACKEND_ADAPTED:
        raise ValueError("backend-adapted ticks cannot be resolved by the GSP reference resolver")
    low, high = sorted((start, end))
    return _resolve_auto_linear_nice(low, high, tick_spec.target_count or 7, tick_spec.kind)


def _resolve_auto_linear_nice(start: float, end: float, target_count: int, source: TickSpecKind) -> ResolvedTicks:
    low, high = _expanded_range(start, end)
    step = _nice_step(low, high, target_count)
    first = math.ceil(low / step) * step
    last = math.floor(high / step) * step
    count = max(0, int(round((last - first) / step)) + 1)
    values = tuple(_round_tick(first + index * step, step) for index in range(count))
    labels = tuple(_format_tick(value, step) for value in values)
    return ResolvedTicks(values=values, labels=labels, step=step, source=source)


def _finite_range(data_range: tuple[float, float]) -> tuple[float, float]:
    start, end = data_range
    if not math.isfinite(start) or not math.isfinite(end):
        raise ValueError("tick range values must be finite")
    return float(start), float(end)


def _expanded_range(start: float, end: float) -> tuple[float, float]:
    if start < end:
        return start, end
    if start == 0:
        return -0.5, 0.5
    delta = abs(start) * 0.5
    return start - delta, end + delta


def _nice_step(start: float, end: float, target_count: int) -> float:
    if target_count <= 0:
        raise ValueError("target_count must be positive")
    data_range = abs(end - start)
    if data_range == 0:
        return _fallback_step(start)
    raw_step = data_range / max(1, target_count)
    exponent = math.floor(math.log10(raw_step))
    base = 10**exponent
    fraction = raw_step / base
    for nice in (1.0, 2.0, 2.5, 5.0, 10.0):
        if fraction <= nice:
            return float(nice * base)
    return float(10.0 * base)


def _fallback_step(value: float) -> float:
    if value == 0:
        return 1.0
    exponent = math.floor(math.log10(abs(value)))
    return float(10**exponent)


def _round_tick(value: float, step: float) -> float:
    decimals = max(0, -math.floor(math.log10(step))) + 2
    rounded = round(value, decimals)
    return 0.0 if rounded == 0 else rounded


def _format_tick(value: float, step: float | None) -> str:
    if value == 0:
        return "0"
    if step is None:
        return f"{value:g}"
    magnitude = abs(value)
    order = math.floor(math.log10(magnitude)) if magnitude > 0 else 0
    if abs(order) >= 3:
        return f"{value:.0e}"
    decimals = max(0, -math.floor(math.log10(step)))
    return f"{value:.{decimals}f}"
