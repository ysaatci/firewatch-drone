import pytest

from firewatch.mission.patrol import lawnmower_ne, plan_patrol, swath_width


def test_swath_width_60deg():
    assert swath_width(100, 60) == pytest.approx(115.47, rel=1e-3)


def test_lawnmower_covers_width_and_stays_in_bounds():
    pts = lawnmower_ne(1000, 600, swath_m=100, overlap=0.2)
    assert len(pts) == 2 * 13  # ceil(1000 / 80) lanes, 2 points each
    for n, e in pts:
        assert 0 <= n <= 600
        assert 0 <= e <= 1000
    assert max(e for _, e in pts) + 50 >= 1000  # last lane's footprint reaches the edge


def test_lawnmower_alternates_direction():
    pts = lawnmower_ne(300, 500, swath_m=100, overlap=0)
    assert pts[:4] == [(0, 50), (500, 50), (500, 150), (0, 150)]


def test_invalid_overlap():
    with pytest.raises(ValueError):
        lawnmower_ne(100, 100, 50, overlap=1.0)


def test_plan_patrol_waypoints():
    wps = plan_patrol(36.787, 31.442, 500, 500, alt_agl=80)
    assert wps and all(wp.alt_agl == 80 for wp in wps)
    assert wps[0].lat == pytest.approx(36.787)
