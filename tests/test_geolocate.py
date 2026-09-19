import math

import pytest

from firewatch.geo.geolocate import (
    Camera,
    DronePose,
    offset_to_latlon,
    pixel_to_latlon,
    pixel_to_ned,
)

POSE = DronePose(lat=36.787, lon=31.442, alt_agl=100.0, yaw=0.0)


def test_nadir_center_is_directly_below():
    cam = Camera(1280, 720, hfov=60, pitch=90)
    n, e = pixel_to_ned(640, 360, POSE, cam)
    assert n == pytest.approx(0, abs=1e-6)
    assert e == pytest.approx(0, abs=1e-6)


def test_45_degree_center_is_alt_metres_ahead():
    cam = Camera(1280, 720, hfov=60, pitch=45)
    n, e = pixel_to_ned(640, 360, POSE, cam)
    assert n == pytest.approx(100.0)
    assert e == pytest.approx(0, abs=1e-6)


def test_yaw_east_points_east():
    cam = Camera(1280, 720, hfov=60, pitch=45)
    pose = DronePose(POSE.lat, POSE.lon, 100.0, yaw=90.0)
    n, e = pixel_to_ned(640, 360, pose, cam)
    assert n == pytest.approx(0, abs=1e-6)
    assert e == pytest.approx(100.0)


def test_nadir_right_edge_is_half_swath_east():
    cam = Camera(1280, 720, hfov=60, pitch=90)
    n, e = pixel_to_ned(1280, 360, POSE, cam)
    assert e == pytest.approx(100 * math.tan(math.radians(30)))
    assert n == pytest.approx(0, abs=1e-6)


def test_top_of_image_is_forward_when_nadir():
    cam = Camera(1280, 720, hfov=60, pitch=90)
    n, _ = pixel_to_ned(640, 0, POSE, cam)
    assert n > 0


def test_above_horizon_returns_none():
    cam = Camera(1280, 720, hfov=60, pitch=10)
    assert pixel_to_latlon(640, 0, POSE, cam) is None


def test_offset_to_latlon_one_km_north():
    lat, lon = offset_to_latlon(36.787, 31.442, 1000, 0)
    assert (lat - 36.787) * 111_320 == pytest.approx(1000, rel=0.01)
    assert lon == 31.442
