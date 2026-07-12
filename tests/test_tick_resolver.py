"""Tests for deterministic protocol tick resolution."""

import math

import pytest

import gsp_vispy2 as vp
from gsp.protocol import TickSpec, TickSpecKind, resolve_ticks


def test_auto_linear_nice_ticks_are_deterministic_for_crossing_zero_range():
    ticks = resolve_ticks(TickSpec(kind=TickSpecKind.AUTO_LINEAR_NICE_V0, target_count=7), (-1.0, 1.0))

    assert ticks.source == TickSpecKind.AUTO_LINEAR_NICE_V0
    assert ticks.step == 0.5
    assert ticks.values == (-1.0, -0.5, 0.0, 0.5, 1.0)
    assert ticks.labels == ("-1.0", "-0.5", "0", "0.5", "1.0")


def test_auto_linear_nice_ticks_cover_large_and_small_domains():
    large = resolve_ticks(TickSpec(kind=TickSpecKind.AUTO_LINEAR_NICE_V0, target_count=5), (0.0, 5000.0))
    small = resolve_ticks(TickSpec(kind=TickSpecKind.AUTO_LINEAR_NICE_V0, target_count=4), (0.001, 0.009))

    assert large.step == 1000.0
    assert large.values == (0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0)
    assert large.labels == ("0", "1e+03", "2e+03", "3e+03", "4e+03", "5e+03")
    assert small.step == 0.002
    assert small.values == (0.002, 0.004, 0.006, 0.008)
    assert small.labels == ("2e-03", "4e-03", "6e-03", "8e-03")


def test_auto_linear_nice_ticks_accept_reversed_domains():
    ticks = resolve_ticks(TickSpec(kind=TickSpecKind.AUTO_LINEAR_NICE_V0, target_count=7), (1.0, -1.0))

    assert ticks.source == TickSpecKind.AUTO_LINEAR_NICE_V0
    assert ticks.step == 0.5
    assert ticks.values == (-1.0, -0.5, 0.0, 0.5, 1.0)
    assert ticks.labels == ("-1.0", "-0.5", "0", "0.5", "1.0")


def test_auto_linear_nice_expands_degenerate_domains_deterministically():
    zero = resolve_ticks(TickSpec(kind=TickSpecKind.AUTO_LINEAR_NICE_V0, target_count=4), (0.0, 0.0))
    nonzero = resolve_ticks(TickSpec(kind=TickSpecKind.AUTO_LINEAR_NICE_V0, target_count=4), (10.0, 10.0))

    assert zero.values == (-0.5, -0.25, 0.0, 0.25, 0.5)
    assert zero.step == 0.25
    assert nonzero.values == (5.0, 7.5, 10.0, 12.5, 15.0)
    assert nonzero.step == 2.5


def test_explicit_ticks_and_labels_are_preserved_exactly():
    spec = TickSpec(
        kind=TickSpecKind.EXPLICIT,
        explicit_values=(0.0, 0.5, 1.0),
        explicit_labels=("zero", "half", "one"),
        target_count=None,
    )

    ticks = resolve_ticks(spec, (-1.0, 1.0))

    assert ticks.values == (0.0, 0.5, 1.0)
    assert ticks.labels == ("zero", "half", "one")
    assert ticks.step is None


def test_explicit_ticks_are_preserved_exactly_for_reversed_domains():
    spec = TickSpec(
        kind=TickSpecKind.EXPLICIT,
        explicit_values=(1.0, 0.0, -1.0),
        explicit_labels=("right", "center", "left"),
        target_count=None,
    )

    ticks = resolve_ticks(spec, (1.0, -1.0))

    assert ticks.values == (1.0, 0.0, -1.0)
    assert ticks.labels == ("right", "center", "left")
    assert ticks.step is None


def test_explicit_ticks_without_labels_get_deterministic_labels():
    ticks = resolve_ticks(
        TickSpec(kind=TickSpecKind.EXPLICIT, explicit_values=(0.0, 0.125, 1000.0), target_count=None),
        (0.0, 1.0),
    )

    assert ticks.labels == ("0", "0.125", "1000")


def test_reference_resolver_rejects_nonfinite_ranges_and_backend_adapted_specs():
    with pytest.raises(ValueError, match="finite"):
        resolve_ticks(TickSpec(), (0.0, math.inf))
    with pytest.raises(ValueError, match="backend-adapted"):
        resolve_ticks(TickSpec(kind=TickSpecKind.BACKEND_ADAPTED), (0.0, 1.0))


def test_tick_resolution_does_not_mutate_vispy2_data_visuals():
    fig, ax = vp.subplots()
    point = ax.scatter([0.0], [0.0], id="visual:points")

    resolve_ticks(TickSpec(), ax.get_xlim())

    assert fig.visuals() == (point,)
