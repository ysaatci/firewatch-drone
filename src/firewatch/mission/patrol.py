"""Coverage patrol planning.

Generates a lawnmower ("boustrophedon") pattern over a rectangular area so the camera
footprint sweeps the whole area with the requested overlap.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from firewatch.geo.geolocate import offset_to_latlon


@dataclass(frozen=True)
class Waypoint:
    lat: float
    lon: float
    alt_agl: float


def swath_width(alt_agl: float, hfov: float) -> float:
    """Ground width in metres covered by a nadir camera at the given altitude."""
    return 2 * alt_agl * math.tan(math.radians(hfov) / 2)


def lawnmower_ne(
    width_m: float, height_m: float, swath_m: float, overlap: float = 0.2
) -> list[tuple[float, float]]:
    """Lawnmower pattern over a width (east) x height (north) box starting at (0, 0).

    Returns (north, east) points. Lanes run north-south and step east.
    """
    if not 0 <= overlap < 1:
        raise ValueError("overlap must be in [0, 1)")
    spacing = swath_m * (1 - overlap)
    n_lanes = max(1, math.ceil(width_m / spacing))
    points: list[tuple[float, float]] = []
    for i in range(n_lanes):
        east = min(i * spacing + swath_m / 2, width_m)
        south_to_north = i % 2 == 0
        ends = (0.0, height_m) if south_to_north else (height_m, 0.0)
        points.extend((n, east) for n in ends)
    return points


def plan_patrol(
    origin_lat: float,
    origin_lon: float,
    width_m: float,
    height_m: float,
    alt_agl: float = 100.0,
    hfov: float = 60.0,
    overlap: float = 0.2,
) -> list[Waypoint]:
    """Plan a coverage patrol with the south-west corner at the origin."""
    swath = swath_width(alt_agl, hfov)
    return [
        Waypoint(*offset_to_latlon(origin_lat, origin_lon, n, e), alt_agl)
        for n, e in lawnmower_ne(width_m, height_m, swath, overlap)
    ]


if __name__ == "__main__":
    wps = plan_patrol(36.7870, 31.4420, width_m=1000, height_m=600)
    print(f"{len(wps)} waypoints")
    for wp in wps:
        print(f"  {wp.lat:.6f}, {wp.lon:.6f} @ {wp.alt_agl} m")
