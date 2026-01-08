"""Module for formatting axis tick labels."""

import math
from typing import List, Tuple


class AxisTickFormatter:
    """Format axis tick labels based on step size and notation rules.

    Args:
        scientific_threshold (int): Minimum absolute exponent to switch to scientific notation.
    """

    def __init__(self, scientific_threshold: int = 6) -> None:
        """Initialize the formatter with a scientific notation threshold.

        Args:
            scientific_threshold (int): Exponent magnitude at which labels use scientific notation.
        """
        self.scientific_threshold: int = scientific_threshold

    def precision(self, step: float) -> int:
        """Determine the number of decimal places from the tick step.

        Args:
            step (float): Tick spacing.

        Returns:
            int: Number of decimal places to keep.
        """
        if step <= 0:
            return 0
        return max(0, -math.floor(math.log10(step)))

    def format(self, value: float, step: float) -> str:
        """Format the tick label for a value using the step size.

        Args:
            value (float): Tick value to format.
            step (float): Tick spacing used to infer precision.

        Returns:
            str: Formatted tick label.
        """
        if value == 0:
            return "0"

        magnitude = abs(value)
        if magnitude > 0:
            order = math.floor(math.log10(magnitude))
            if abs(order) >= self.scientific_threshold:
                return f"{value:.0e}"

        decimals = self.precision(step)
        return f"{value:.{decimals}f}"
