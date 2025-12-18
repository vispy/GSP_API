"""Marker shape enumeration for GSP visualization.

This module defines the available marker shapes that can be used
in the GSP (Graphical Scene Protocol) API for rendering points and markers.
"""

from enum import Enum


class MarkerShape(Enum):
    """Common marker shapes for rendering points and markers.

    This enumeration defines the available marker shapes that can be used
    when rendering points, markers, or other graphical elements in the GSP API.

    Attributes:
        disc: A circular/disc-shaped marker.
        square: A square-shaped marker.
        club: A club-shaped marker (similar to a playing card club symbol).
    """

    disc = "disc"
    square = "square"
    club = "club"
