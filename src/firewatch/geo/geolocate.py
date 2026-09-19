"""Project an image pixel onto the ground to get its GPS position.

Uses a pinhole camera model and assumes flat ground at the drone's take-off altitude.
Phase 2 replaces the flat-ground assumption with a terrain elevation model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

EARTH_RADIUS_M = 6_378_137.0


@dataclass(frozen=True)
class DronePose:
    lat: float  # degrees
    lon: float  # degrees
    alt_agl: float  # metres above ground
    yaw: float  # heading, degrees clockwise from north


@dataclass(frozen=True)
class Camera:
    width: int  # pixels
    height: int  # pixels
    hfov: float  # horizontal field of view, degrees
    pitch: float  # gimbal angle below horizon, degrees (90 = straight down)


def pixel_to_ned(u: float, v: float, pose: DronePose, cam: Camera) -> tuple[float, float] | None:
    """Return the (north, east) ground offset in metres from the drone to pixel (u, v).

    Returns None if the pixel's ray points at or above the horizon.
    """
    fx = (cam.width / 2) / math.tan(math.radians(cam.hfov) / 2)
    x = (u - cam.width / 2) / fx  # image right
    y = (v - cam.height / 2) / fx  # image down (square pixels)

    yaw, pitch = math.radians(pose.yaw), math.radians(cam.pitch)
    fwd = (math.cos(yaw), math.sin(yaw), 0.0)
    right = (-math.sin(yaw), math.cos(yaw), 0.0)
    down = (0.0, 0.0, 1.0)

    # Camera axes in the local NED frame.
    optical = [math.cos(pitch) * f + math.sin(pitch) * d for f, d in zip(fwd, down, strict=True)]
    img_down = [-math.sin(pitch) * f + math.cos(pitch) * d for f, d in zip(fwd, down, strict=True)]

    ray = [o + x * r + y * d for o, r, d in zip(optical, right, img_down, strict=True)]
    if ray[2] <= 1e-9:
        return None
    t = pose.alt_agl / ray[2]
    return t * ray[0], t * ray[1]


def offset_to_latlon(lat: float, lon: float, north: float, east: float) -> tuple[float, float]:
    """Shift a lat/lon by a small north/east offset in metres."""
    dlat = math.degrees(north / EARTH_RADIUS_M)
    dlon = math.degrees(east / (EARTH_RADIUS_M * math.cos(math.radians(lat))))
    return lat + dlat, lon + dlon


def pixel_to_latlon(u: float, v: float, pose: DronePose, cam: Camera) -> tuple[float, float] | None:
    """Return the (lat, lon) of the ground point seen at pixel (u, v)."""
    ne = pixel_to_ned(u, v, pose, cam)
    if ne is None:
        return None
    return offset_to_latlon(pose.lat, pose.lon, *ne)


if __name__ == "__main__":
    pose = DronePose(lat=36.7870, lon=31.4420, alt_agl=100.0, yaw=0.0)  # near Manavgat
    cam = Camera(width=1280, height=720, hfov=60.0, pitch=45.0)
    for px in [(640, 360), (0, 360), (1280, 720)]:
        print(px, "->", pixel_to_latlon(*px, pose, cam), "offset m:", pixel_to_ned(*px, pose, cam))
