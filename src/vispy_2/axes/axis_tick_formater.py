"""Module for formatting axis tick labels."""

# stdlib imports
import math


class AxisTickFormatter:
    """Format axis tick labels based on step size and notation rules.

    Args:
        scientific_threshold (int): Minimum absolute exponent to switch to scientific notation.
    """

    def __init__(self, scientific_threshold: int = 3) -> None:
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
            # Avoid log10 domain errors and keep integers for degenerate steps.
            return 0
        return max(0, -math.floor(math.log10(step)))

    def format(self, tick_value: float, tick_step: float) -> str:
        """Format the tick label for a value using the step size.

        Args:
            tick_value (float): Tick value to format.
            tick_step (float): Tick spacing used to infer precision.

        Returns:
            str: Formatted tick label.
        """
        if tick_value == 0:
            return "0"

        # Determine if scientific notation is needed.
        magnitude = abs(tick_value)
        if magnitude > 0:
            order = math.floor(math.log10(magnitude))
            if abs(order) >= self.scientific_threshold:
                # Switch to scientific notation for very large/small values.
                return f"{tick_value:.0e}"

        # Standard decimal formatting based on step precision.
        decimals = self.precision(tick_step)
        return f"{tick_value:.{decimals}f}"
