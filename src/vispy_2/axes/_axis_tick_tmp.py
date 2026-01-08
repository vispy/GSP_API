"""Nice Numbers algorithm for axis tick spacing.

This module implements the "Nice Numbers" algorithm for automatically determining
optimal tick spacing and positions for scientific visualization axes.
"""

import math
import numpy as np
from typing import Tuple, List, Optional


class TickGenerator:
    """Compute tick spacing, positions, and labels using "nice number" heuristics."""

    @staticmethod
    def nice_number(value: float, round_up: bool = False) -> float:
        """Find a "nice" number approximately equal to the given value.

        Nice numbers are powers of 10 times 1, 2, or 5.
        """
        if value == 0:
            return 0

        exponent = math.floor(math.log10(abs(value)))
        fraction = abs(value) / (10**exponent)

        if round_up:
            if fraction <= 1:
                nice_fraction = 1
            elif fraction <= 2:
                nice_fraction = 2
            elif fraction <= 5:
                nice_fraction = 5
            else:
                nice_fraction = 10
        else:
            if fraction < 1.5:
                nice_fraction = 1
            elif fraction < 3:
                nice_fraction = 2
            elif fraction < 7:
                nice_fraction = 5
            else:
                nice_fraction = 10

        return nice_fraction * (10**exponent) * (1 if value >= 0 else -1)

    @classmethod
    def calculate_tick_spacing(cls, data_min: float, data_max: float, target_ticks: int = 5) -> Tuple[float, float, float]:
        """Calculate nice tick spacing for the given data range."""
        if data_min == data_max:
            if data_min == 0:
                return 1.0, -1.0, 1.0
            magnitude = abs(data_min)
            tick_spacing = cls.nice_number(magnitude / 5)
            return tick_spacing, data_min - tick_spacing, data_min + tick_spacing

        data_range = data_max - data_min
        rough_step = data_range / target_ticks
        tick_spacing = cls.nice_number(rough_step)

        nice_min = math.floor(data_min / tick_spacing) * tick_spacing
        nice_max = math.ceil(data_max / tick_spacing) * tick_spacing

        return tick_spacing, nice_min, nice_max

    @classmethod
    def generate_tick_positions(cls, data_min: float, data_max: float, target_ticks: int = 5, max_ticks: int = 20) -> np.ndarray:
        """Generate nice tick positions for the given data range."""
        tick_spacing, nice_min, nice_max = cls.calculate_tick_spacing(data_min, data_max, target_ticks)

        nice_min = max(nice_min, data_min)

        num_ticks = int(round((nice_max - nice_min) / tick_spacing)) + 1

        if num_ticks > max_ticks:
            multiplier = math.ceil(num_ticks / max_ticks)
            tick_spacing *= multiplier
            nice_min = math.floor(data_min / tick_spacing) * tick_spacing
            nice_max = math.ceil(data_max / tick_spacing) * tick_spacing
            nice_min = max(nice_min, data_min)
            num_ticks = int(round((nice_max - nice_min) / tick_spacing)) + 1

        ticks = np.linspace(nice_min, nice_max, num_ticks)

        data_range = data_max - data_min
        extended_min = data_min
        extended_max = data_max + 0.1 * data_range

        mask = (ticks >= extended_min) & (ticks <= extended_max)
        return ticks[mask]

    @staticmethod
    def format_tick_label(value: float, tick_spacing: float) -> str:
        """Format a tick label with appropriate precision."""
        if value == 0:
            return "0"

        if tick_spacing >= 1:
            if abs(value - round(value)) < 1e-10:
                return f"{int(round(value))}"
            return f"{value:.1f}"

        decimal_places = max(0, -int(math.floor(math.log10(tick_spacing))))

        if abs(value) < 1e-3 or abs(value) >= 1e6:
            return f"{value:.2e}"
        return f"{value:.{decimal_places}f}"

    @classmethod
    def generate_ticks_and_labels(cls, data_min: float, data_max: float, target_ticks: int = 5, max_ticks: int = 20) -> Tuple[np.ndarray, List[str]]:
        """Generate both tick positions and their formatted labels."""
        positions = cls.generate_tick_positions(data_min, data_max, target_ticks, max_ticks)
        tick_spacing, _, _ = cls.calculate_tick_spacing(data_min, data_max, target_ticks)
        labels = [cls.format_tick_label(pos, tick_spacing) for pos in positions]
        return positions, labels


class AxisTicker:
    """Manage axis tick generation with nice numbers.

    Provides a convenient interface for generating ticks and can maintain state
    between updates.

    Args:
        target_ticks (int): Target number of tick intervals.
        max_ticks (int): Maximum number of ticks to prevent overcrowding.
    """

    def __init__(self, target_ticks: int = 5, max_ticks: int = 20) -> None:
        """Initialize the AxisTicker."""
        self.target_ticks: int = target_ticks
        self.max_ticks: int = max_ticks
        self._last_range: Optional[Tuple[float, float]] = None
        self._cached_ticks: Optional[np.ndarray] = None
        self._cached_labels: Optional[List[str]] = None

    def get_ticks(self, data_min: float, data_max: float, force_update: bool = False) -> Tuple[np.ndarray, List[str]]:
        """Get tick positions and labels for the given data range.

        Args:
            data_min (float): Minimum value of the data range.
            data_max (float): Maximum value of the data range.
            force_update (bool): Force recalculation even if the range hasn't changed.

        Returns:
            Tuple[np.ndarray, List[str]]: ``(positions, labels)`` for the current range.
        """
        current_range: Tuple[float, float] = (data_min, data_max)

        # Check if we can use cached results
        if not force_update and self._last_range == current_range:
            assert self._cached_ticks is not None, f"Cache inconsistency: ticks missing for range {current_range}"
            assert self._cached_labels is not None, f"Cache inconsistency: labels missing for range {current_range}"
            return self._cached_ticks, self._cached_labels

        # Generate new ticks
        positions: np.ndarray
        labels: List[str]
        positions, labels = TickGenerator.generate_ticks_and_labels(data_min, data_max, self.target_ticks, self.max_ticks)

        # Cache results
        self._last_range = current_range
        self._cached_ticks = positions
        self._cached_labels = labels

        return positions, labels

    def update_settings(self, target_ticks: Optional[int] = None, max_ticks: Optional[int] = None) -> None:
        """Update ticker settings and clear cache.

        Args:
            target_ticks (Optional[int]): New target number of tick intervals.
            max_ticks (Optional[int]): New maximum number of ticks.
        """
        if target_ticks is not None:
            self.target_ticks = target_ticks
        if max_ticks is not None:
            self.max_ticks = max_ticks

        # Clear cache when settings change
        self._last_range = None
        self._cached_ticks = None
        self._cached_labels = None


if __name__ == "__main__":
    # Minimal usage example for manual testing
    span_min, span_max = 0.37, 8.93
    axes_ticker = AxisTicker(target_ticks=5, max_ticks=20)
    ticks, labels = axes_ticker.get_ticks(span_min, span_max)
    spacing, nice_min, nice_max = TickGenerator.calculate_tick_spacing(span_min, span_max, 5)

    print("Data range:", (span_min, span_max))
    print("Nice bounds:", (nice_min, nice_max))
    print("Tick spacing:", spacing)
    print("Ticks:", ticks)
    print("Labels:", labels)
