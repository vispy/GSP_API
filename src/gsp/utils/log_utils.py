"""Logging utilities using loguru.

Example usage:
from gsp.utils.log_utils import logger

logger.info("This is an info message.")
"""

from loguru import logger

# Configure loguru to output logs in a specific format
logger.remove()
# Log format: [LEVEL] file:line:function() — message
logger.add(
    sink=lambda msg: print(msg, end=""),
    colorize=True,
    format="<cyan>{level}</cyan> <blue>{file}:{line}</blue>:<magenta>{function}()</magenta> — {message}",
)
