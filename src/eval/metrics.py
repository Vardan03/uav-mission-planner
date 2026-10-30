"""Per-instance metrics and aggregation over a split."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data_gen.instance import Instance
from src.eval.checker import route_length

COLUMNS = [
    "seed", "topology", "N", "K", "method", "CR", "CR_achievable",
    "gap_vs_ref", "L_total", "n_visited", "time_s", "feasible", "status",
]


def visited_weight(inst: Instance, routes: list) -> int:
    """Sum of the weights of all visited targets."""
    return int(sum(inst.weights[t] for route in routes for t in route))


def cr(inst: Instance, routes: list) -> float:
    """Collected reward in percent of the total weight of all targets."""
    return 100.0 * visited_weight(inst, routes) / float(inst.weights.sum())


def cr_achievable(inst: Instance, routes: list) -> float:
    """Collected reward in percent of the weight of the non-flagged targets."""
    skip = set(inst.flags.get("unreachable_targets", []))
    total = sum(w for i, w in enumerate(inst.weights) if i not in skip)
    return 100.0 * visited_weight(inst, routes) / float(total) if total else float("nan")


def total_length(inst: Instance, routes: list) -> float:
    """Sum of the lengths of all routes in km."""
    return float(sum(route_length(inst, k, r) for k, r in enumerate(routes)))


def gap(cr_ref: float, cr_value: float) -> float:
    """Gap in percent to a reference CR: 100 * (ref - value) / ref."""
    if not cr_ref:
        return float("nan")
    return 100.0 * (cr_ref - cr_value) / cr_ref


def instance_row(inst: Instance, method: str, sol, violations: list) -> dict:
    """One result row (without gap_vs_ref, which needs the reference method)."""
    return {
        "seed": inst.seed, "topology": inst.topology, "N": inst.N, "K": inst.K,
        "method": method,
        "CR": cr(inst, sol.routes),
        "CR_achievable": cr_achievable(inst, sol.routes),
        "gap_vs_ref": float("nan"),
        "L_total": total_length(inst, sol.routes),
        "n_visited": sum(len(r) for r in sol.routes),
        "time_s": sol.solve_time,
        "feasible": len(violations) == 0,
        "status": sol.status,
    }


def add_gap(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """Fill gap_vs_ref in df using the CR of `ref` (matched by seed)."""
    ref_cr = ref.set_index("seed")["CR"]
    out = df.copy()
    out["gap_vs_ref"] = [gap(ref_cr.get(s, np.nan), c) for s, c in zip(out["seed"], out["CR"])]
    return out


def summarize(df: pd.DataFrame) -> dict:
    """Mean and std of the metrics, feasibility rate and mean time for one method."""
    result = {"n_instances": len(df), "feasible_pct": 100.0 * df["feasible"].mean()}
    for col in ["CR", "CR_achievable", "gap_vs_ref", "L_total", "time_s"]:
        result[col + "_mean"] = df[col].mean()
        result[col + "_std"] = df[col].std(ddof=0)
    return result
