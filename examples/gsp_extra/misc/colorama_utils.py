"""Colorama utility functions."""

# pip imports
import colorama


# =============================================================================
# Colorama alias
# =============================================================================
def text_cyan(text: str) -> str:
    """Return the given text string colored in cyan."""
    return colorama.Fore.CYAN + text + colorama.Style.RESET_ALL


def text_magenta(text: str) -> str:
    """Return the given text string colored in magenta."""
    return colorama.Fore.MAGENTA + text + colorama.Style.RESET_ALL
