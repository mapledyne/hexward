from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any
from .hex_util import GridOrientation, HexPoint, Size, cube_round, cube_ring
from .hex_cell import HexCell

if TYPE_CHECKING:
    try:
        import pygame
    except ImportError:
        # pygame not available - type hints will use string literals
        pass


# TODO: Add things so we can do map[point] and for cell in map.
# TODO: Proper exceptions for when acting on an invalid cell (like pixel_to_hex)
# TODO: Offer a way to mask a hex from apygame surface back into a hex size.
class HexMap:

    # region Dunder Methods

    def __init__(self, radius: int = 100, orientation: GridOrientation = GridOrientation.POINTY_TOP, cell_type: type[HexCell] = HexCell):
        self._orientation = orientation
        self._radius = radius
        self._grid: dict[HexPoint, HexCell] = {}
        self._spacing = Size(0, 0)
        self._reference = HexCell(orientation, HexPoint(0, 0, 0), radius)
        self._offset = Size(0, 0)
        self._cell_type = cell_type

    def __contains__(self, point: HexPoint) -> bool:
        if isinstance(point, HexPoint):
            return point in self._grid
    
    def __getitem__(self, point: HexPoint) -> HexCell:
        return self._grid[point]

    def __iter__(self):
        return iter(self._grid.values())
    
    def __len__(self):
        return len(self._grid)
    
    # endregion Dunder Methods

    # region Properties
    @property
    def radius(self):
        return self._radius
    
    @property
    def orientation(self):
        return self._orientation

    @property
    def size(self):
        return self._reference.size

    @property
    def width(self):
        return self.size.width
    
    @property
    def height(self):
        return self.size.height

    @property
    def spacing(self):
        if not self._spacing:
            if self.orientation == GridOrientation.POINTY_TOP:
                self._spacing.width = self.width
                self._spacing.height = 0.75 * self.height
            else:
                self._spacing.width = 0.75 * self.width
                self._spacing.height = self.height

        return self._spacing

    # endregion Properties

    # region Private Methods

    def _pixel_to_pointy_hex(self, target_x: int, target_y: int) -> HexPoint:
        x = (target_x - self.radius) / self._radius
        y = (target_y) / self._radius

        q = math.sqrt(3)/3 * x - (1/3) * y
        r = (2 / 3) * y
        return cube_round(q, r)

    def _pixel_to_flat_hex(self, target_x: int, target_y: int) -> HexPoint:
        x = target_x / (self.size.width / 2)
        y = target_y / (self.size.height / 2)

        q = (2 / 3) * x
        r = (-1 / 3) * x + math.sqrt(3) / 3 * y
        return cube_round(q, r)

    # endregion Private Methods

    # region Public methods
    def pixel_to_hex(self, target_x: int, target_y: int) -> HexPoint:
        x = target_x - self._offset.width
        y = target_y - self._offset.height
        if self.orientation == GridOrientation.POINTY_TOP:
            return self._pixel_to_pointy_hex(x, y)
        else:
            return self._pixel_to_flat_hex(x, y)

    def set(self, point: HexPoint, data: Any = None) -> HexCell:
        if isinstance(data, HexCell):
            data = data.data
        if isinstance(point, tuple):
            point = HexPoint(*point)

        self._grid[point] = self._cell_type(self.orientation, point, self.radius, data)
        return self._grid[point]

    def get(self, point: HexPoint) -> HexCell:
        return self._grid[point]
    
    def remove(self, point: HexPoint):
        self._grid.pop(point, None)
    
    def swap(self, point1: HexPoint, point2: HexPoint):
        if point1 not in self or point2 not in self:
            raise ValueError("One or both points are not in the map")
        
        self._grid[point1].data, self._grid[point2].data = self._grid[point2].data, self._grid[point1].data
        self._grid[point1].clearcache()
        self._grid[point2].clearcache()

    def fill_to_radius(self, radius: int):
        for i in range(radius):
            for point in cube_ring(HexPoint(0, 0, 0), i):
                if point not in self:
                    self.set(point, None)

    def draw(self, color: "pygame.Color | None" = None, border_color: "pygame.Color | None" = None, border_width: int = 1) -> "pygame.Surface":
        try:
            import pygame
        except ImportError:
            raise RuntimeError("Pygame is not installed. Drawing is not available.")
        
        # Set defaults inside the function
        if color is None:
            color = pygame.Color(255, 255, 255)
        if border_color is None:
            border_color = pygame.Color(0, 0, 0)

        # Handle empty grid case
        if not self._grid:
            # Return empty surface with minimal size
            empty_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            empty_surface.fill((0, 0, 0, 0))
            return empty_surface

        # Calculate bounds of grid
        min_x = min(cell.pixel_xy[0] for cell in self._grid.values())
        max_x = max(cell.pixel_xy[0] for cell in self._grid.values()) 
        min_y = min(cell.pixel_xy[1] for cell in self._grid.values())
        max_y = max(cell.pixel_xy[1] for cell in self._grid.values())

        # Calculate the offset needed to make all coordinates positive
        # We need to ensure the leftmost/topmost hex has enough space for its full width/height
        offset_x = -min_x + self.width/2  # + border_width
        offset_y = -min_y + self.height/2  # + border_width
        
        self._offset = Size(offset_x, offset_y)

        # Create surface large enough for entire grid with proper padding
        width = int(max_x - min_x + self.width)  # + 2 * border_width)
        height = int(max_y - min_y + self.height) #  + 2 * border_width)
        
        grid_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        grid_surface.fill((0, 0, 0, 0))

        # Draw each cell offset by min_x/y to align with surface
        for cell in self._grid.values():
            hex_surface = cell.draw(color, border_color, border_width)

            # Calculate position relative to the grid surface with proper offset
            # pixel_xy gives us the center point, so we need to offset by the hex surface size
            x = int(cell.pixel_xy[0] + offset_x - hex_surface.get_width()/2)
            y = int(cell.pixel_xy[1] + offset_y - hex_surface.get_height()/2)
            
            grid_surface.blit(hex_surface, (x, y))

        return grid_surface

    # endregion Public methods