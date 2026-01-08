"""Module for locating axis ticks."""

import math
from typing import List, Tuple


class AxisTickLocator:
    """Compute visually pleasing tick positions for an axis.

    Args:
        target_ticks (int): Desired number of ticks; treated as a hint rather than a hard requirement.
        nice_fractions (Tuple[float, ...]): Ordered fractions used to snap the raw step to a human-friendly value.
    """

    def __init__(
        self,
        target_ticks: int = 6,
        nice_fractions: Tuple[float, ...] = (1, 2, 2.5, 5, 10),
    ) -> None:
        """Initialize the AxisTickLocator.

        Args:
            target_ticks (int): Desired number of ticks.
            nice_fractions (Tuple[float, ...]): Fractions for nice number calculation.
        """
        self.target_ticks: int = target_ticks
        self.nice_fractions: Tuple[float, ...] = nice_fractions

    def tick_step(self, vmin: float, vmax: float) -> float:
        """Return a suitable tick step for the interval.

        Args:
            vmin (float): Minimum data value.
            vmax (float): Maximum data value.

        Returns:
            float: Step size chosen to give well-spaced ticks.
        """
        if vmin == vmax:
            return self._fallback_step(vmin)

        data_range = abs(vmax - vmin)
        raw_step = data_range / max(1, self.target_ticks)

        # Decompose the raw step to snap it to a "nice" fraction of a power of ten.
        exponent = math.floor(math.log10(raw_step))
        base = 10**exponent
        fraction = raw_step / base

        for nice in self.nice_fractions:
            if fraction <= nice:
                return nice * base

        # Fallback (should rarely happen)
        return self.nice_fractions[-1] * base

    def ticks(self, vmin: float, vmax: float) -> Tuple[List[float], float]:
        """Generate tick positions and the step size for an interval.

        Args:
            vmin (float): Minimum data value.
            vmax (float): Maximum data value.

        Returns:
            Tuple[List[float], float]: List of tick positions and the step size used.
        """
        step = self.tick_step(vmin, vmax)

        start = math.ceil(vmin / step) * step
        end = math.floor(vmax / step) * step

        # Keep both bounds inclusive and guard against floating-point drift.
        n = int(round((end - start) / step)) + 1
        ticks = [start + i * step for i in range(max(0, n))]

        # Final rounding pass
        ticks = [self._round_tick(t, step) for t in ticks]

        return ticks, step

    def _fallback_step(self, value: float) -> float:
        if value == 0:
            return 1.0
        exponent = math.floor(math.log10(abs(value)))
        return 10**exponent

    def _round_tick(self, value: float, step: float) -> float:
        decimals = max(0, -math.floor(math.log10(step)))
        return round(value, decimals + 2)


if __name__ == "__main__":
    from .axis_tick_formater import AxisTickFormatter

    locator = AxisTickLocator(target_ticks=7)
    formatter = AxisTickFormatter()

    vmin, vmax = -3.7, 42.2

    ticks, step = locator.ticks(vmin, vmax)

    labels = [formatter.format(t, step) for t in ticks]

    for t, lbl in zip(ticks, labels):
        print(f"{t:8.3f} -> {lbl}")
