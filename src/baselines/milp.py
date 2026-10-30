"""Exact MILP for the team orienteering problem (PuLP + CBC), small N only."""
from __future__ import annotations

import numpy as np
import pulp

from src.baselines.solution import Solution
from src.data_gen.instance import Instance

DEFAULT_TIME_LIMIT = 300.0  # s
BUDGET_MARGIN = 1e-7  # km, keeps CBC's tolerance from exceeding B + 1e-6


def solve(inst: Instance, time_limit: float | None = None, seed: int = 0) -> Solution:
    """Solve to optimality (or until time_limit) with arc variables per vehicle.

    Variables: x[i,j,k] arc used by UAV k, y[i,k] target i visited by UAV k, t[i,k]
    arrival-distance variable (replaces MTZ: tighter). status is "optimal" only if CBC proved optimality,
    otherwise "time_limit" (or "infeasible"/"error").
    """
    time_limit = DEFAULT_TIME_LIMIT if time_limit is None else time_limit
    K, N, d, B = inst.K, inst.N, inst.dist, inst.budget
    targets = range(N)
    node = lambda t: K + t  # noqa: E731  (target index -> row in dist)

    prob = pulp.LpProblem("top", pulp.LpMaximize)
    y = {(i, k): pulp.LpVariable(f"y_{i}_{k}", cat="Binary") for i in targets for k in range(K)}
    # t[i,k]: distance flown by UAV k when it arrives at i (also removes subtours)
    t = {
        (i, k): pulp.LpVariable(f"t_{i}_{k}", d[k, node(i)], max(d[k, node(i)], B - d[node(i), k]))
        for i in targets for k in range(K) if np.isfinite(d[k, node(i)])
    }
    x = {}  # arc keys: ("d", i) depot->i, (i, "d") i->depot, (i, j) target->target
    for k in range(K):
        for i in targets:
            if 2 * d[k, node(i)] <= B:
                x[("d", i, k)] = pulp.LpVariable(f"xo_{i}_{k}", cat="Binary")
                x[(i, "d", k)] = pulp.LpVariable(f"xi_{i}_{k}", cat="Binary")
            else:
                prob += y[(i, k)] == 0
            for j in targets:
                if i != j and d[k, node(i)] + d[node(i), node(j)] + d[node(j), k] <= B:
                    x[(i, j, k)] = pulp.LpVariable(f"x_{i}_{j}_{k}", cat="Binary")

    def arc(a, b, k):
        return x.get((a, b, k), 0)

    prob += pulp.lpSum(int(inst.weights[i]) * y[(i, k)] for i in targets for k in range(K))

    for i in targets:
        prob += pulp.lpSum(y[(i, k)] for k in range(K)) <= 1
    for k in range(K):
        prob += pulp.lpSum(arc("d", i, k) for i in targets) <= 1
        prob += pulp.lpSum(arc("d", i, k) for i in targets) == pulp.lpSum(
            arc(i, "d", k) for i in targets
        )
        for i in targets:
            out_arcs = arc(i, "d", k) + pulp.lpSum(arc(i, j, k) for j in targets if j != i)
            in_arcs = arc("d", i, k) + pulp.lpSum(arc(j, i, k) for j in targets if j != i)
            prob += out_arcs == y[(i, k)]
            prob += in_arcs == y[(i, k)]
        for i in targets:
            for j in targets:
                if (i, j, k) in x:
                    big_m = t[(i, k)].upBound + d[node(i), node(j)] - t[(j, k)].lowBound
                    prob += t[(j, k)] >= t[(i, k)] + d[node(i), node(j)] - big_m * (1 - x[(i, j, k)])
        length = pulp.lpSum(
            d[k, node(i)] * x[("d", i, k)] + d[node(i), k] * x[(i, "d", k)]
            for i in targets if ("d", i, k) in x
        ) + pulp.lpSum(d[node(i), node(j)] * x[(i, j, k)] for i in targets for j in targets
                       if (i, j, k) in x)
        prob += length <= inst.budget - BUDGET_MARGIN

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)  # no threads=: it hangs CBC 2.10.3
    prob.solve(solver)

    proven = prob.sol_status == pulp.LpSolutionOptimal
    if prob.sol_status not in (pulp.LpSolutionOptimal, pulp.LpSolutionIntegerFeasible):
        status = "infeasible" if prob.status == pulp.LpStatusInfeasible else "no_solution"
        return Solution(routes=[[] for _ in range(K)], status=status)

    routes = []
    for k in range(K):
        successor = {}
        for (a, b, kk), var in x.items():
            if kk == k and a != "d" and var.value() is not None and var.value() > 0.5:
                successor[a] = b
        route, current = [], None
        for i in targets:
            if ("d", i, k) in x and x[("d", i, k)].value() > 0.5:
                current = i
        while current is not None and current != "d":
            route.append(current)
            current = successor.get(current)
        routes.append(route)
    return Solution(routes=routes, status="optimal" if proven else "time_limit",
                    extra={"objective": pulp.value(prob.objective)})
