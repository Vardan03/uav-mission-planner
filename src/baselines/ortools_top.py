"""OR-Tools routing solver with Guided Local Search and optional targets."""
from __future__ import annotations

import math

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from src.baselines.solution import Solution
from src.data_gen.instance import Instance

SCALE = 1000  # km -> m
DEFAULT_TIME_LIMIT = 5.0  # s, used when no limit is given


def solve(inst: Instance, time_limit: float | None = None, seed: int = 0) -> Solution:
    """Maximise collected weight with per-vehicle distance budgets.

    Arc costs are NFZ-aware distances in metres, rounded UP so that a route within
    the integer capacity is also within B in real kilometres. Every target is
    optional with a penalty of weight * M, M larger than any route cost, so weight
    is maximised first and distance second. GLS is deterministic for fixed inputs
    (OR-Tools exposes no seed here), so `seed` is unused.
    """
    time_limit = DEFAULT_TIME_LIMIT if time_limit is None else time_limit
    capacity = int(math.floor(inst.budget * SCALE))
    n_nodes = inst.K + inst.N
    # Legs longer than the budget can never be flown; cap them so the matrix stays finite.
    capped = inst.dist.clip(max=inst.budget + 1.0)
    matrix = [[int(math.ceil(v * SCALE - 1e-9)) for v in row] for row in capped]

    depots = list(range(inst.K))
    manager = pywrapcp.RoutingIndexManager(n_nodes, inst.K, depots, depots)
    routing = pywrapcp.RoutingModel(manager)

    def arc_cost(from_index: int, to_index: int) -> int:
        return matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    transit = routing.RegisterTransitCallback(arc_cost)
    routing.SetArcCostEvaluatorOfAllVehicles(transit)
    routing.AddDimension(transit, 0, capacity, True, "Distance")

    big_m = 10 * capacity * inst.K
    for t in range(inst.N):
        routing.AddDisjunction([manager.NodeToIndex(inst.K + t)], int(inst.weights[t]) * big_m)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromMilliseconds(int(time_limit * 1000))
    params.log_search = False

    assignment = routing.SolveWithParameters(params)
    if assignment is None:
        return Solution(routes=[[] for _ in range(inst.K)], status="no_solution")

    routes = []
    for vehicle in range(inst.K):
        route, index = [], routing.Start(vehicle)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node >= inst.K:
                route.append(node - inst.K)
            index = assignment.Value(routing.NextVar(index))
        routes.append(route)
    return Solution(routes=routes, status="solved")
