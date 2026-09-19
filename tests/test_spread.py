import numpy as np

from firewatch.firesim.spread import BURNED, BURNING, UNBURNED, FireGrid, _shift


def test_shift():
    m = np.zeros((3, 3), dtype=bool)
    m[1, 1] = True
    assert _shift(m, 1, 0)[2, 1]
    assert _shift(m, 0, -1)[1, 0]
    assert _shift(m, 1, 1).sum() == 1


def test_fire_spreads_and_burns_out():
    grid = FireGrid(np.full((30, 30), 0.8), seed=1)
    grid.ignite(15, 15)
    grid.run(5)
    assert (grid.state != UNBURNED).sum() > 5
    assert grid.state[15, 15] == BURNED


def test_no_fuel_no_spread():
    grid = FireGrid(np.zeros((10, 10)), seed=1)
    grid.ignite(5, 5)
    assert not (grid.state == BURNING).any()


def test_firebreak_stops_fire():
    fuel = np.ones((20, 20))
    fuel[:, 10] = 0  # firebreak column
    grid = FireGrid(fuel, seed=2)
    grid.ignite(10, 2)
    grid.run(100)
    assert (grid.state[:, 11:] == UNBURNED).all()


def test_wind_pushes_fire_downwind():
    grid = FireGrid(np.full((40, 80), 0.4), wind=(0.0, 3.0), seed=3)  # blowing east
    grid.ignite(20, 40)
    grid.run(10)
    _, cols = np.nonzero(grid.state != UNBURNED)
    assert (cols > 40).sum() > 2 * (cols < 40).sum()
