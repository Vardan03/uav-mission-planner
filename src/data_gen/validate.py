"""Cleaning and validation checks for generated instances."""
from __future__ import annotations

import logging

import numpy as np
from shapely import make_valid
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

log = logging.getLogger("uav.generate")


class RepairFailed(Exception):
    """A repair did not succeed; the generator should retry with a new attempt."""


def _polygon_parts(geom) -> list:
    """Return the Polygon pieces of any shapely geometry."""
    if geom.geom_type == "Polygon":
        return [geom]
    if hasattr(geom, "geoms"):
        return [p for g in geom.geoms for p in _polygon_parts(g)]
    return []


def merge_nfz(polygons: list, seed: int) -> list:
    """Repair invalid polygons, merge overlapping ones, drop holes.

    Returns a list of polygons, each a list of (x, y) in counter-clockwise order
    without a repeated closing vertex. Raises RepairFailed if a polygon cannot be
    made valid.
    """
    repaired = []
    for poly in polygons:
        if not poly.is_valid:
            log.info("seed=%d repair: make_valid on NFZ polygon", seed)
            poly = make_valid(poly)
            if not poly.is_valid or not _polygon_parts(poly):
                raise RepairFailed("NFZ polygon still invalid after make_valid")
        repaired.append(poly)
    merged = unary_union(repaired)
    result = []
    for part in _polygon_parts(merged):
        if len(part.interiors) > 0:
            log.info("seed=%d repair: NFZ hole filled", seed)
        part = orient(Polygon(part.exterior), sign=1.0)  # exterior only, CCW
        result.append([tuple(map(float, c)) for c in part.exterior.coords[:-1]])
    return result


def nfz_union(nfz: list):
    """Return the union of the NFZ polygons as one shapely geometry, or None."""
    if not nfz:
        return None
    return unary_union([Polygon(p) for p in nfz])


def is_clear(point, union, clearance: float) -> bool:
    """True if the point is outside the NFZs and at least `clearance` km away."""
    if union is None:
        return True
    return union.distance(Point(point)) >= clearance


def check_hard_errors(targets, weights, depots, size: float, w_range) -> None:
    """Raise ValueError for NaN, out-of-bounds coordinates or bad weights.

    These can only come from a generator bug, so they are never repaired.
    """
    for name, arr in (("targets", targets), ("depots", depots)):
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"{name} contain NaN or inf")
        if arr.min() < 0 or arr.max() > size:
            raise ValueError(f"{name} outside the [0, {size}] map")
    if weights.min() < w_range[0] or weights.max() > w_range[1]:
        raise ValueError("weight outside the allowed range")


def unreachable_targets(dist: np.ndarray, n_depots: int, budget: float) -> list:
    """Target indices whose round trip exceeds the budget from every depot."""
    to_target = dist[:n_depots, n_depots:]
    return [int(i) for i in np.where(np.all(2 * to_target > budget, axis=0))[0]]


def validate_instance(inst, cfg: dict) -> list:
    """Check a finished instance; return a list of problems (empty = valid).

    Raises ValueError for generator-bug conditions (see `check_hard_errors`).
    """
    v = cfg["validation"]
    check_hard_errors(inst.targets, inst.weights, inst.depots, cfg["map_size"], cfg["weights"])
    problems = []
    union = nfz_union(inst.nfz)
    for k, p in enumerate(inst.depots):
        if not is_clear(p, union, v["depot_nfz_clearance"]):
            problems.append(f"depot {k} too close to an NFZ")
    for i, p in enumerate(inst.targets):
        if not is_clear(p, union, v["target_nfz_clearance"]):
            problems.append(f"target {i} too close to an NFZ")
    gaps = np.linalg.norm(inst.targets[:, None] - inst.targets[None, :], axis=2)
    np.fill_diagonal(gaps, np.inf)
    if gaps.min() < v["min_target_sep"]:
        problems.append("two targets closer than the minimum separation")
    reachable = np.isfinite(inst.dist[: inst.K, inst.K :]).any(axis=0)
    for i in np.where(~reachable)[0]:
        problems.append(f"target {i} has no path to any depot")
    expected = unreachable_targets(inst.dist, inst.K, inst.budget)
    if inst.flags.get("unreachable_targets") != expected:
        problems.append("flags.unreachable_targets does not match dist")
    return problems
