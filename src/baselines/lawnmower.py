"""Lawnmower baseline: priority-blind boustrophedon sweep of one strip per UAV."""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from src.baselines.solution import Solution
from src.data_gen.instance import Instance

MAP_SIZE = 10.0  # km, the map is [0, MAP_SIZE]^2 (see configs/data.yaml)
LANE_HEIGHT = 1.0  # km


def assign_strips(inst: Instance) -> list:
    """Return strip_of_depot[k]: the strip index flown by depot k.

    Each strip goes to the nearest depot (strip centre at mid-height). If two strips
    pick the same depot, a minimum-cost one-to-one assignment is used instead.
    """
    width = MAP_SIZE / inst.K
    centres = np.array([[(s + 0.5) * width, MAP_SIZE / 2] for s in range(inst.K)])
    cost = np.linalg.norm(centres[:, None] - inst.depots[None, :], axis=2)  # strip x depot
    nearest = cost.argmin(axis=1)
    if len(set(nearest)) == inst.K:
        depot_of_strip = nearest
    else:
        strips, depot_of_strip = linear_sum_assignment(cost)
    strip_of_depot = [0] * inst.K
    for strip, depot in enumerate(depot_of_strip):
        strip_of_depot[depot] = strip
    return strip_of_depot


def sweep_order(inst: Instance, strip: int) -> list:
    """Targets of one vertical strip in boustrophedon order."""
    width = MAP_SIZE / inst.K
    x, y = inst.targets[:, 0], inst.targets[:, 1]
    strip_of_target = np.minimum((x // width).astype(int), inst.K - 1)
    members = np.where(strip_of_target == strip)[0]
    lane = np.minimum((y[members] // LANE_HEIGHT).astype(int), int(MAP_SIZE / LANE_HEIGHT) - 1)
    key_x = np.where(lane % 2 == 0, x[members], -x[members])  # odd lanes go right-to-left
    order = np.lexsort((key_x, lane))
    return [int(t) for t in members[order]]


def solve(inst: Instance, time_limit: float | None = None, seed: int = 0) -> Solution:
    """Each UAV sweeps its strip in order, skipping targets that no longer fit.

    A target is taken if flying to it and then home stays within the budget. The
    sweep is a single pass over the strip. time_limit and seed are unused.
    """
    routes = []
    for k, strip in enumerate(assign_strips(inst)):
        route, position, flown = [], k, 0.0
        for t in sweep_order(inst, strip):
            node = inst.K + t
            leg = inst.dist[position, node]
            if flown + leg + inst.dist[node, k] <= inst.budget:
                route.append(t)
                flown += leg
                position = node
        routes.append(route)
    return Solution(routes=routes, status="ok")
