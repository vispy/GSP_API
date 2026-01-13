"""Module for locating axis ticks."""

# stdlib imports
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

    def compute_location_dunit(self, min_dunit: float, max_dunit: float) -> Tuple[List[float], float]:
        """Generate tick positions in data units and the step size for an interval.

        Args:
            min_dunit (float): Minimum data value in data unit.
            max_dunit (float): Maximum data value in data unit.

        Returns:
            Tuple[List[float], float]: List of tick positions and the step size used.
        """
        tick_step = self.tick_step(min_dunit, max_dunit)

        start = math.ceil(min_dunit / tick_step) * tick_step
        end = math.floor(max_dunit / tick_step) * tick_step

        # Keep both bounds inclusive and guard against floating-point drift.
        tick_count = int(round((end - start) / tick_step)) + 1
        tick_positions = [start + tick_index * tick_step for tick_index in range(max(0, tick_count))]

        # Final rounding pass
        tick_positions = [self._round_tick(tick_position, tick_step) for tick_position in tick_positions]

        return tick_positions, tick_step

    def _fallback_step(self, value: float) -> float:
        if value == 0:
            return 1.0
        exponent = math.floor(math.log10(abs(value)))
        return 10**exponent

    def _round_tick(self, tick_value: float, tick_step: float) -> float:
        decimals = max(0, -math.floor(math.log10(tick_step)))
        return round(tick_value, decimals + 2)


# =============================================================================
# Usage Example
# =============================================================================

if __name__ == "__main__":
    from vispy_2.axes.axis_tick_formater import AxisTickFormatter

    tick_locator = AxisTickLocator(target_ticks=7)
    tick_formatter = AxisTickFormatter()

    min_dunit = 500
    max_dunit = 510

    tick_positions, tick_step = tick_locator.compute_location_dunit(min_dunit, max_dunit)

    tick_labels = [tick_formatter.format(tick_position, tick_step) for tick_position in tick_positions]

    for tick_position, tick_label in zip(tick_positions, tick_labels):
        print(f"{tick_position:8.3f} -> {tick_label}")
