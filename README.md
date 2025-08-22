# Hexward

A Python library for working with hexagonal grids, featuring coordinate systems, grid operations, and pygame integration for visualization.

## Installation

```bash
pip install hexward
```

## Quick Start

```python
import hexward

# Create a hexagonal map
map = hexward.HexMap(radius=50, GridOrientation.POINTY_TOP)

# Add data to the map. Points use cube (q, r, s) notation for location, but
# there are helper functions to convert to others if useful to you.
map.set(hexward.HexPoint(1, 0, -1), "some data")

# Get distance between hexes
distance = hexward.cube_distance(
    hexward.HexPoint(0, 0, 0), 
    hexward.HexPoint(1, 0, -1)
)
```

## Features

- **HexCell**: Individual hexagonal cells with coordinate conversion and drawing
- **HexMap**: Collections of hexagonal cells with grid operations
- **HexPoint**: Cube coordinates for hexagonal grid positions
- **Grid Operations**: Distance calculation, neighbor finding, ring generation
- **Coordinate Systems**: Support for both pointy-top and flat-top orientations
- **Pygame Integration**: Basic drawing capabilities for visualization

## Version

Current version: 0.4.0

## License

See [LICENSE](LICENSE) file for details.
