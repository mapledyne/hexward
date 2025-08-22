"""
Hexward - A hexagonal grid library for Python

A comprehensive library for working with hexagonal grids, including coordinate systems,
grid operations, and pygame integration for visualization.

Main classes:
    - HexCell: Represents a single hexagonal cell with coordinate conversion and drawing
    - HexMap: A collection of hexagonal cells with grid operations
    - HexPoint: Cube coordinates for hexagonal grid positions
    - Size: Utility class for width/height dimensions

Enums:
    - GridOrientation: POINTY_TOP or FLAT_TOP grid orientations

Example usage:
    >>> import hexward
    >>> map = hexward.HexMap(radius=50)
    >>> cell = hexward.HexCell(hexward.GridOrientation.POINTY_TOP, hexward.HexPoint(0, 0, 0), 50)
    >>> map.set(hexward.HexPoint(1, 0, -1), "some data")
"""

# Core classes
from .hex_cell import HexCell
from .hex_map import HexMap
from .hex_util import (
    HexPoint,
    Size,
    GridOrientation,
)

# Utility functions
from .hex_util import (
    cube_distance,
    cube_neighbor,
    cube_ring,
    cube_to_spiral,
    spiral_to_cube,
    hex_angles,
    direction_name,
    cube_round,
    CUBE_DIRECTIONS,
    DIRECTION_NAMES,
)

# Version info
__version__ = "0.4.0"
__author__ = "Michael Knowles"

# Convenience imports for common use cases
__all__ = [
    # Main classes
    "HexCell",
    "HexMap",
    "HexPoint",
    "Size",
    "GridOrientation",
    
    # Utility functions
    "cube_distance",
    "cube_neighbor",
    "cube_ring",
    "cube_to_spiral",
    "spiral_to_cube",
    "hex_angles",
    "direction_name",
    "cube_round",

    # Constants
    "CUBE_DIRECTIONS",
    "DIRECTION_NAMES",

    # Metadata
    "__version__",
    "__author__",
]
