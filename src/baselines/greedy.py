"""Greedy baseline: best weight per added detour, then 2-opt, repeated."""
from __future__ import annotations

import numpy as np

from src.baselines.solution import Solution
from src.data_gen.instance import Instance

EPS = 1e-6  # added to the detour in the ratio w / (delta + EPS)
TOL = 1e-9  # numerical slack for budget and 2-opt comparisons


def _nodes(inst: Instance, k: int, route: list) -> list:
    """Node sequence of route k including the depot at both ends."""
    return [k] + [inst.K + t for t in route] + [k]


def _length(inst: Instance, nodes: list) -> float:
    """Length of a node sequence."""
    return float(sum(inst.dist[a, b] for a, b in zip(nodes[:-1], nodes[1:])))


def _best_insertion(inst: Instance, routes: list, lengths: list, unvisited: set):
    """Return (ratio, k, target, position) of the best feasible insertion, or None."""
    best = None
    for k, route in enumerate(routes):
        nodes = _nodes(inst, k, route)
        for t in unvisited:
            node = inst.K + t
            for pos in range(len(nodes) - 1):
                a, b = nodes[pos], nodes[pos + 1]
                delta = inst.dist[a, node] + inst.dist[node, b] - inst.dist[a, b]
                if not np.isfinite(delta) or lengths[k] + delta > inst.budget + TOL:
                    continue
                ratio = inst.weights[t] / (delta + EPS)
                if best is None or ratio > best[0]:
                    best = (ratio, k, t, pos)
    return best


def _two_opt(inst: Instance, k: int, route: list) -> list:
    """Shorten one route by reversing segments until no reversal helps."""
    nodes = _nodes(inst, k, route)
    d = inst.dist
    improved = True
    while improved:
        improved = False
        for i in range(1, len(nodes) - 2):
            for j in range(i + 1, len(nodes) - 1):
                before = d[nodes[i - 1], nodes[i]] + d[nodes[j], nodes[j + 1]]
                after = d[nodes[i - 1], nodes[j]] + d[nodes[i], nodes[j + 1]]
                if after < before - TOL:
                    nodes[i : j + 1] = nodes[i : j + 1][::-1]
                    improved = True
    return [n - inst.K for n in nodes[1:-1]]


def solve(inst: Instance, time_limit: float | None = None, seed: int = 0) -> Solution:
    """Build all routes at once by weight-per-detour insertion, improved with 2-opt.

    time_limit and seed are unused: the method is deterministic and fast.
    """
    routes = [[] for _ in range(inst.K)]
    lengths = [0.0] * inst.K
    unvisited = set(range(inst.N))
    while True:
        inserted = False
        while unvisited:
            best = _best_insertion(inst, routes, lengths, unvisited)
            if best is None:
                break
            _, k, t, pos = best
            routes[k].insert(pos, t)  # nodes[pos] is route[pos - 1], so pos is the list index
            lengths[k] = _length(inst, _nodes(inst, k, routes[k]))
            unvisited.discard(t)
            inserted = True
        shortened = False
        for k in range(inst.K):
            new_route = _two_opt(inst, k, routes[k])
            new_length = _length(inst, _nodes(inst, k, new_route))
            if new_length < lengths[k] - TOL:
                shortened = True
            routes[k], lengths[k] = new_route, min(new_length, lengths[k])
        if not shortened:
            break
    return Solution(routes=routes, status="ok")
