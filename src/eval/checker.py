"""Feasibility checker: returns a list of violations (empty list = feasible)."""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString

from src.data_gen import geometry, validate
from src.data_gen.instance import Instance

BUDGET_TOL = 1e-6  # km
PATH_TOL = 1e-6  # km, allowed mismatch between path length and dist
INSIDE_TOL = 1e-9  # km, length of a leg allowed inside an NFZ (numerical noise)


def route_length(inst: Instance, k: int, route: list) -> float:
    """Length of the closed route depot k -> targets -> depot k, using inst.dist."""
    nodes = [k] + [inst.K + t for t in route] + [k]
    return float(sum(inst.dist[a, b] for a, b in zip(nodes[:-1], nodes[1:])))


def check(inst: Instance, routes: list, check_paths: bool = True) -> list:
    """Return all constraint violations of `routes` (empty list = feasible).

    Args:
        routes: one list of target indices (0..N-1) per depot.
        check_paths: also rebuild the real leg paths and test them against the NFZs.
    """
    problems = []
    if len(routes) != inst.K:
        return [f"expected {inst.K} routes, got {len(routes)}"]

    seen = set()
    for k, route in enumerate(routes):
        for t in route:
            if not isinstance(t, (int, np.integer)) or not 0 <= t < inst.N:
                problems.append(f"route {k}: invalid target index {t!r}")
            elif t in seen:
                problems.append(f"route {k}: target {t} visited more than once")
            seen.add(t)
    if problems:
        return problems

    for k, route in enumerate(routes):
        length = route_length(inst, k, route)
        if not length <= inst.budget + BUDGET_TOL:
            problems.append(f"route {k}: length {length:.6f} exceeds budget {inst.budget}")

    if check_paths:
        problems += _check_leg_paths(inst, routes)
    return problems


def check_node_sequences(inst: Instance, node_routes: list) -> list:
    """Check routes given as node sequences (depots included, indices as in dist).

    Verifies that route k starts and ends at depot k and only visits targets in
    between, then runs the normal `check`.
    """
    if len(node_routes) != inst.K:
        return [f"expected {inst.K} routes, got {len(node_routes)}"]
    problems, routes = [], []
    for k, nodes in enumerate(node_routes):
        if len(nodes) < 2 or nodes[0] != k or nodes[-1] != k:
            problems.append(f"route {k}: must start and end at depot {k}")
            routes.append([])
            continue
        inner = list(nodes[1:-1])
        if any(n < inst.K for n in inner):
            problems.append(f"route {k}: depot used as an intermediate stop")
        routes.append([n - inst.K for n in inner if n >= inst.K])
    return problems + check(inst, routes)


def _check_leg_paths(inst: Instance, routes: list) -> list:
    """Verify every leg's real path avoids NFZ interiors and matches dist."""
    if not inst.nfz:
        return []
    graph = geometry.NFZGraph(inst.points, inst.nfz)
    union = validate.nfz_union(inst.nfz)
    shapely.prepare(union)
    problems = []
    for k, route in enumerate(routes):
        nodes = [k] + [inst.K + t for t in route] + [k]
        for a, b in zip(nodes[:-1], nodes[1:]):
            path = graph.path(a, b)
            if len(path) < 2:
                continue
            line = LineString(path)
            if abs(line.length - inst.dist[a, b]) > PATH_TOL:
                problems.append(f"route {k}: path {a}->{b} length differs from dist")
            if line.intersection(union).length > INSIDE_TOL:
                problems.append(f"route {k}: leg {a}->{b} enters an NFZ")
    return problems
