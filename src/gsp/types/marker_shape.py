"""Marker shape enumeration for GSP visualization.

This module defines the available marker shapes that can be used
in the GSP (Graphical Scene Protocol) API for rendering points and markers.

Matplotlib list of markers: https://matplotlib.org/stable/api/markers_api.html
Datoviz list of markers: https://datoviz.org/visuals/marker/#code
"""

from enum import Enum


class MarkerShape(Enum):
    """Common marker shapes for rendering points and markers.

    This enumeration defines the available marker shapes that can be used
    when rendering points, markers, or other graphical elements in the GSP API.

    Attributes:
        disc: A circular/disc-shaped marker.
        triangle_down: A downward-pointing triangle marker.
        triangle_up: An upward-pointing triangle marker.
        triangle_left: A left-pointing triangle marker.
        triangle_right: A right-pointing triangle marker.
        square: A square-shaped marker.
        club: A club-shaped marker (similar to a playing card club symbol).
    """

    disc = "disc"
    asterisk = "asterisk"
    triangle_down = "triangle_down"
    triangle_up = "triangle_up"
    triangle_left = "triangle_left"
    triangle_right = "triangle_right"
    square = "square"
    cross = "cross"
    club = "club"
    diamond = "diamond"
    heart = "heart"
    spade = "spade"
    vbar = "vbar"
    hbar = "hbar"
