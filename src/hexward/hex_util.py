from enum import Enum, auto
from dataclasses import dataclass
from typing import NamedTuple

# TODO: Considering caching sqrt(3) since it's used in many places
# TODO: Add easy conversion from math degrees?

DIRECTION_NAMES = {
    0: "East",
    30: "Southeast",
    60: "Southeast",
    90: "South",
    120: "Southwest",
    150: "Southwest",
    180: "West",
    210: "Northwest",
    240: "Northwest",
    270: "North",
    300: "Northeast",
    330: "Northeast",
    360: "East",
}

class Size(NamedTuple):
    width: int
    height: int

    def __bool__(self):
        return self.width > 0 and self.height > 0

@dataclass
class HexPoint:
    q: int
    r: int
    s: int

    def __add__(self, other: 'HexPoint') -> 'HexPoint':
        return HexPoint(self.q + other.q, self.r + other.r, self.s + other.s)

    def __sub__(self, other: 'HexPoint') -> 'HexPoint':
        return HexPoint(self.q - other.q, self.r - other.r, self.s - other.s)

    def __mul__(self, other) -> 'HexPoint':
        if isinstance(other, HexPoint):
            return HexPoint(self.q * other.q, self.r * other.r, self.s * other.s)
        elif isinstance(other, int):
            return HexPoint(self.q * other, self.r * other, self.s * other)
        return NotImplemented
    
    def __lt__(self, other: 'HexPoint') -> bool:
        return int(self) < int(other)
    
    def __gt__(self, other: 'HexPoint') -> bool:
        return int(self) > int(other)
    
    def __le__(self, other: 'HexPoint') -> bool:
        return int(self) <= int(other)
    
    def __ge__(self, other: 'HexPoint') -> bool:
        return int(self) >= int(other)

    def __eq__(self, other) -> bool:
        if isinstance(other, HexPoint):
            return self.q == other.q and self.r == other.r and self.s == other.s
        return NotImplemented

    def __int__(self) -> int:
        if hasattr(self, '_int'):
            return self._int
        self._int = cube_to_spiral(self)
        return self._int
    
    def __str__(self) -> str:
        return f"HexPoint(q={self.q}, r={self.r}, s={self.s})"
    
    def __hash__(self) -> int:
        return hash((self.q, self.r, self.s))


CUBE_DIRECTIONS = [
    HexPoint(1, 0, -1),
    HexPoint(0, 1, -1),
    HexPoint(-1, 1, 0),
    HexPoint(-1, 0, 1),
    HexPoint(0, -1, 1),
    HexPoint(1, -1, 0),
]

class GridOrientation(Enum):
    POINTY_TOP = auto()
    FLAT_TOP = auto()

    def toggle(self):
        if self == GridOrientation.POINTY_TOP:
            return GridOrientation.FLAT_TOP
        return GridOrientation.POINTY_TOP

# TODO: Find places still doing this themselves instead of calling here.
def _angle_to_math_angle(angle: int) -> int:
    return (-1 * (angle - 90)) % 360

def _math_angle_to_angle(angle: int) -> int:
    return (-1 * (angle + 90)) % 360

def _cube_to_oddr(q, r, s) -> tuple[int, int]:
    """Convert cube coordinates to offset coordinates for pointy top orientation"""
    parity = r % 2
    col = q + (r - parity) / 2
    row = r
    return col, row

def _oddr_to_cube(x, y) -> HexPoint:
    """Convert offset coordinates to cube coordinates for pointy top orientation"""
    parity = x % 2
    q = y - (x - parity) / 2
    r = x
    return HexPoint(q, r, -q-r)


def _cube_to_oddq(q, r, s) -> tuple[int, int]:
    """Convert cube coordinates to offset coordinates for flat top orientation"""
    parity = q % 2
    col = q
    row = r + (q - parity) / 2
    return col, row

def _oddq_to_cube(x, y) -> HexPoint:
    """Convert offset coordinates to cube coordinates for flat top orientation"""
    parity = x % 2
    q = x
    r = y - (x - parity) / 2
    return HexPoint(q, r, -q-r)

def cube_distance(a: HexPoint, b: HexPoint) -> int:
    return (abs(a.q - b.q) + abs(a.r - b.r) + abs(a.s - b.s)) // 2


def cube_neighbor(hex: HexPoint, direction: int) -> HexPoint:
    return hex + CUBE_DIRECTIONS[direction]


def cube_ring(center: HexPoint, radius: int) -> list[HexPoint]:
    """ Return a list of cells that are <radius> distance from the center."""
    if radius < 0:
        raise ValueError("Radius must be positive")
    if radius == 0:
        return [center]

    results = []

    point = center + (CUBE_DIRECTIONS[4] * radius)

    for i in range(6):
        for _ in range(radius):
            results.append(point)
            point = cube_neighbor(point, i)
    return results


def _spiral_index_start_of_ring(radius: int) -> int:
    if radius == 0:
        return 0
    return 1 + 3 * radius * (radius - 1)

def _spiral_index_to_radius(index: int) -> int:
    if index == 0:
        return 0
    # Solve quadratic equation: index = 1 + 3r(r-1)
    # 3r^2 - 3r - (index-1) = 0
    # Using quadratic formula with a=3, b=-3, c=-(index-1)
    return int((3 + (9 + 12*(index-1))**0.5) / 6)


def cube_to_spiral(point: HexPoint):
    center = HexPoint(0, 0, 0)
    radius = cube_distance(point, center)
    ring_hexes = cube_ring(center, radius)
    for i, ring_hex in enumerate(ring_hexes):
        if point == ring_hex:
            return i + _spiral_index_start_of_ring(radius)
    raise ValueError("Hex not found in ring")

def spiral_to_cube(index: int) -> HexPoint:
    center = HexPoint(0, 0, 0)
    radius = _spiral_index_to_radius(index)
    ringstart = _spiral_index_start_of_ring(radius)
    return cube_ring(center, radius)[index - ringstart]

def hex_angles(orientation: GridOrientation):
    if orientation == GridOrientation.POINTY_TOP:
        return (90, 150, 210, 270, 330, 30)

    # TODO: Make sure this order is correct.
    return (0, 60, 120, 180, 240, 300)

def direction_name(angle: int) -> str:
    if angle in DIRECTION_NAMES:
        return DIRECTION_NAMES[angle]
    raise ValueError(f"Invalid angle: {angle}")

def cube_round(frac_q: float, frac_r: float, frac_s: float = None) -> HexPoint:

    if frac_s is None:
        frac_s = -frac_q - frac_r
    q = round(frac_q)
    r = round(frac_r)
    s = round(frac_s)   

    q_diff = abs(q - frac_q)
    r_diff = abs(r - frac_r)
    s_diff = abs(s - frac_s)

    if q_diff > r_diff and q_diff > s_diff:
        q = -r-s
    elif r_diff > s_diff:
        r = -q-s
    else:
        s = -q-r

    return HexPoint(q, r, s)
