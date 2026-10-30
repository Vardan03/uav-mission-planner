"""Common return type of every baseline."""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Solution:
    """Routes for all UAVs plus timing and solver status.

    routes[k] is the list of target indices (0..N-1) visited by UAV k, in order.
    The depot at the start and end of each route is implicit.
    """

    routes: list
    solve_time: float = 0.0  # seconds, wall clock around solve() only
    status: str = ""
    extra: dict = field(default_factory=dict)


def timed(solve, inst, time_limit=None, seed: int = 0) -> Solution:
    """Call a baseline's solve() and store the wall-clock time in the solution."""
    start = time.perf_counter()
    sol = solve(inst, time_limit=time_limit, seed=seed)
    sol.solve_time = time.perf_counter() - start
    return sol
