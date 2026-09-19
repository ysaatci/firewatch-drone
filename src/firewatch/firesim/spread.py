"""Toy cellular-automaton fire spread model.

Good enough to drive integration tests and the simulation loop. Phase 4 swaps this for
Cell2Fire / ForeFire with real fuel, slope and weather data.
"""

from __future__ import annotations

import numpy as np

UNBURNED, BURNING, BURNED = 0, 1, 2

# 8-neighbourhood offsets as (drow, dcol); row 0 is north.
_NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class FireGrid:
    """Grid of cells that are unburned, burning, or burned out.

    fuel: array in [0, 1], base probability that fire spreads into the cell per step.
    wind: (north, east) vector; spread downwind is boosted, upwind is damped.
    """

    def __init__(
        self,
        fuel: np.ndarray,
        wind: tuple[float, float] = (0.0, 0.0),
        seed: int | None = None,
    ):
        self.fuel = np.clip(np.asarray(fuel, dtype=float), 0.0, 1.0)
        self.state = np.full(self.fuel.shape, UNBURNED, dtype=np.int8)
        self.wind = np.asarray(wind, dtype=float)
        self.rng = np.random.default_rng(seed)

    def ignite(self, row: int, col: int) -> None:
        if self.fuel[row, col] > 0:
            self.state[row, col] = BURNING

    def step(self) -> None:
        burning = self.state == BURNING
        prob_not_ignited = np.ones(self.fuel.shape)
        for dr, dc in _NEIGHBOURS:
            # Fire moving from a neighbour at (-dr, -dc) into the cell travels (dr, dc):
            # north component is -dr (rows grow southward), east is dc.
            direction = np.array([-dr, dc], dtype=float)
            direction /= np.linalg.norm(direction)
            wind_factor = np.exp(0.5 * float(self.wind @ direction))
            src = _shift(burning, dr, dc)
            p = np.clip(self.fuel * wind_factor * 0.5, 0.0, 1.0)
            prob_not_ignited *= np.where(src, 1.0 - p, 1.0)

        ignites = (self.state == UNBURNED) & (self.rng.random(self.fuel.shape) > prob_not_ignited)
        self.state[burning] = BURNED
        self.state[ignites] = BURNING

    def run(self, steps: int) -> None:
        for _ in range(steps):
            if not (self.state == BURNING).any():
                break
            self.step()

    def perimeter(self) -> np.ndarray:
        """Boolean mask of currently burning cells (the active fire front)."""
        return self.state == BURNING


def _shift(mask: np.ndarray, dr: int, dc: int) -> np.ndarray:
    """out[r, c] = mask[r - dr, c - dc], with zeros outside the grid."""
    out = np.zeros_like(mask)
    h, w = mask.shape
    out[max(dr, 0) : h + min(dr, 0), max(dc, 0) : w + min(dc, 0)] = mask[
        max(-dr, 0) : h + min(-dr, 0), max(-dc, 0) : w + min(-dc, 0)
    ]
    return out


if __name__ == "__main__":
    grid = FireGrid(np.full((20, 40), 0.6), wind=(0.0, 2.0), seed=0)  # wind blowing east
    grid.ignite(10, 5)
    grid.run(12)
    chars = {UNBURNED: ".", BURNING: "*", BURNED: "#"}
    print("\n".join("".join(chars[v] for v in row) for row in grid.state))
