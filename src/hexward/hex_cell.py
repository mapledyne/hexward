from .hex_util import (
    CUBE_DIRECTIONS,
    GridOrientation,
    HexPoint,
    Size,
    _cube_to_oddr,
    _oddr_to_cube,
    _cube_to_oddq,
    _oddq_to_cube,
    cube_distance,
    hex_angles,
    _angle_to_math_angle,
    _math_angle_to_angle,
)
from typing import Any
import math

class HexCell:

    # region Dunder Methods

    def __init__(self, orientation: GridOrientation, point: HexPoint, radius: int, data: Any = None):
        self._orientation = orientation
        self._radius = radius
        self._point = point
        self._data = data
        self._size = Size(0, 0)
        self._pixel_xy: tuple[int, int] | None = None

    def __int__(self) -> int:
        return int(self._point)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._point}|{int(self)})"

    # endregion Dunder Methods

    # region Properties

    @property
    def orientation(self):
        return self._orientation
    
    @property
    def radius(self):
        return self._radius
    
    @property
    def point(self):
        return self._point
    
    @point.setter
    def point(self, value: HexPoint):
        self._point = value
    
    @property
    def q(self):
        return self._point.q
    
    @property
    def r(self):
        return self._point.r
    
    @property
    def s(self):
        return self._point.s
    
    @property
    def qrs(self) -> tuple[int, int, int]:
        return self._point.q, self._point.r, self._point.s
    
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value: Any):
        self._data = value
    
    @property
    def xy(self) -> tuple[int, int]:
        if self.orientation == GridOrientation.POINTY_TOP:
            return _cube_to_oddr(self._point)
        else:
            return _cube_to_oddq(self._point)
    
    @xy.setter
    def xy(self, value: tuple[int, int]):
        if self.orientation == GridOrientation.POINTY_TOP:
            self._point = _oddr_to_cube(value[0], value[1])
        else:
            self._point = _oddq_to_cube(value[0], value[1])
    
    @property
    def x(self):
        return self.xy[0]
    
    @property
    def y(self):
        return self.xy[1]

    @property
    def neighbors(self):
        return [self + direction for direction in CUBE_DIRECTIONS]

    @property
    def size(self):
        if not self._size:
            size_long = 2 * self.radius
            size_short = math.sqrt(3) * self.radius
            if self.orientation == GridOrientation.POINTY_TOP:
                self._size = Size(size_short, size_long)
            else:
                self._size = Size(size_long, size_short)
        return self._size
    
    @property
    def pixel_xy(self) -> tuple[int, int]:
        if self._pixel_xy is None:
        
            if self.orientation == GridOrientation.POINTY_TOP:
                x = math.sqrt(3) * self.q + math.sqrt(3)/2 * self.r
                y = (3 / 2) * self.r
                # scale cartesian coordinates
                x = x * self._radius   # (self.size.width / 2)
                y = y * self._radius    # (self.size.height / 2)
                self._pixel_xy = (x, y)
            else:
                x = (3 / 2) * self.q
                y = math.sqrt(3)/2 * self.q + math.sqrt(3) * self.r
                # scale cartesian coordinates
                x = x * self._radius   # (self.size.width / 2)
                y = y * self._radius    # (self.size.height / 2)
                self._pixel_xy = (x, y)
        return self._pixel_xy

    @property
    def corner_angles(self):
        return hex_angles(self.orientation.toggle())

    @property
    def edge_angles(self):
        return hex_angles(self.orientation)

    # endregion Properties

    # region Methods

    def clearcache(self):
        self._pixel_xy = None

#    def draw(self, color: pygame.Color, border_color: pygame.Color , border_width: int = 1) -> pygame.Surface:
    def draw(self, color, border_color, border_width: int = 1):
        try:
            import pygame
        except ImportError:
            raise RuntimeError("Pygame is not installed. Drawing is not available.")

        # Add padding for border width
        surface_width = self.size.width + (2 * border_width)
        surface_height = self.size.height + (2 * border_width)
        
        hex_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        hex_surface.fill((0, 0, 0, 0))
        
        points = []
        for angle in self.corner_angles:
            math_angle = _angle_to_math_angle(angle)
            rad = math.radians(math_angle)
            # TODO: Does this math work for flat top?
            # Center hex on padded surface by adding padding to coordinates
            x = (surface_width/2) + self.radius * math.cos(rad)
            y = (surface_height/2) + self.radius * math.sin(rad)
            points.append((x, y))
            
        pygame.draw.polygon(hex_surface, color, points)
        pygame.draw.polygon(hex_surface, border_color, points, border_width)
        return hex_surface

    def distance_to(self, other: 'HexCell') -> int:
        return cube_distance(self._point, other._point)

    def pixel_at_angle(self, angle: int) -> tuple[int, int]:
        # Convert angle to standard math angle (0 = right, 90 = up)
        # by subtracting 90 and negating
        angle = -1 * (angle - 90)
        rad = math.radians(angle)
        if self.orientation == GridOrientation.POINTY_TOP:
            x = self.radius * math.cos(rad)
            y = -self.radius * math.sin(rad)
        else:
            # TODO: Validate this math for flat top.
            x = self.radius * math.cos(rad)
            y = -self.radius * math.sin(rad)
        return (x, y)
    
    def nearest_direction_from_angle(self, angle: int) -> int:
        # Normalize angle to 0-360 range
        
        normalized_angle = angle % 360
        
        # Compare angle to each corner angle and find closest match
        min_diff = float('inf')
        closest_direction = 0
        
        for direction, corner_angle in enumerate(self.edge_angles):
            # Calculate shortest angle difference accounting for wrapping
            angle_diff = min(
                abs(corner_angle - normalized_angle),
                abs(corner_angle - (normalized_angle + 360)),
                abs((corner_angle + 360) - normalized_angle)
            )
            
            if angle_diff < min_diff:
                min_diff = angle_diff
                closest_direction = direction
                
        return closest_direction

    def nearest_corner_from_angle(self, angle: int) -> int:
        # Normalize angle to 0-360 range
        angle = angle % 360
        
        # Corner angles are offset from direction angles by 30 degrees
        direction_angles = []
        if self.orientation == GridOrientation.POINTY_TOP:
            direction_angles = [0, 60, 120, 180, 240, 300]
        else:
            direction_angles = [30, 90, 150, 210, 270, 330]

        # Find direction (0-5) that minimizes angle difference
        idx = min(range(6), key=lambda i: abs(direction_angles[i] - angle))
        return direction_angles[idx]

    # endregion Methods

