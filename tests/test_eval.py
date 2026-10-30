"""Tests for the feasibility checker and the metrics on a hand-made instance."""
import numpy as np
import pandas as pd

from src.baselines.solution import Solution
from src.data_gen import geometry
from src.data_gen.instance import Instance
from src.eval import checker, metrics


def make_instance(nfz=None, budget=10.0) -> Instance:
    """Two depots on the bottom edge, three targets in a row; weights 1, 2, 7."""
    depots = np.array([[0.0, 0.0], [10.0, 0.0]])
    targets = np.array([[1.0, 0.0], [2.0, 0.0], [9.0, 0.0]])
    nfz = nfz or []
    dist = geometry.distance_matrix(np.vstack([depots, targets]), nfz)
    return Instance(
        seed=0, topology="uniform", targets=targets, weights=np.array([1, 2, 7]),
        depots=depots, nfz=nfz, budget=budget, dist=dist,
        flags={"unreachable_targets": []},
    )


def test_feasible_solution_passes():
    inst = make_instance()
    assert checker.check(inst, [[0, 1], [2]]) == []


def test_checker_catches_over_budget():
    inst = make_instance(budget=3.0)
    assert any("exceeds budget" in v for v in checker.check(inst, [[0, 1, 2], []]))


def test_checker_catches_duplicate_target():
    inst = make_instance()
    assert any("more than once" in v for v in checker.check(inst, [[0], [0]]))
    assert any("more than once" in v for v in checker.check(inst, [[0, 0], []]))


def test_checker_catches_wrong_end_depot():
    inst = make_instance()
    assert checker.check_node_sequences(inst, [[0, 2, 3, 0], [1, 4, 1]]) == []
    bad = checker.check_node_sequences(inst, [[0, 2, 3, 1], [1, 4, 1]])
    assert any("start and end at depot 0" in v for v in bad)


def test_checker_catches_wrong_route_count_and_bad_index():
    inst = make_instance()
    assert checker.check(inst, [[0]])
    assert checker.check(inst, [[5], []])


def test_checker_accepts_detour_path_around_nfz():
    square = [(4.0, -1.0), (6.0, -1.0), (6.0, 1.0), (4.0, 1.0)]
    inst = make_instance(nfz=[square], budget=40.0)
    assert checker.check(inst, [[0, 1], [2]]) == []
    assert inst.dist[0, 1] > 10.0 + 1e-3  # depot 0 -> depot 1 must go around the square


def test_checker_catches_leg_through_nfz():
    square = [(4.0, -1.0), (6.0, -1.0), (6.0, 1.0), (4.0, 1.0)]
    inst = make_instance(nfz=[square], budget=40.0)
    inst.dist = np.linalg.norm(inst.points[:, None] - inst.points[None, :], axis=2)
    assert checker.check(inst, [[0, 1, 2], []]) != []


def test_metrics_hand_computed():
    inst = make_instance()
    routes = [[0, 1], [2]]  # weights 1+2+7 = 10 of 10
    assert metrics.cr(inst, routes) == 100.0
    assert metrics.cr(inst, [[0, 1], []]) == 30.0
    assert metrics.total_length(inst, [[0, 1], []]) == 4.0  # 0->1->2->0 on a line
    assert metrics.total_length(inst, [[0, 1], [2]]) == 6.0
    inst.flags["unreachable_targets"] = [2]
    assert metrics.cr_achievable(inst, [[0, 1], []]) == 100.0
    assert metrics.gap(80.0, 60.0) == 25.0


def test_instance_row_and_summary():
    inst = make_instance()
    sol = Solution(routes=[[0, 1], []], solve_time=0.5, status="ok")
    row = metrics.instance_row(inst, "m", sol, [])
    assert row["CR"] == 30.0 and row["n_visited"] == 2 and row["feasible"]
    df = pd.DataFrame([row, {**row, "CR": 50.0, "time_s": 1.5}])
    summary = metrics.summarize(df)
    assert summary["CR_mean"] == 40.0 and summary["CR_std"] == 10.0
    assert summary["time_s_mean"] == 1.0 and summary["feasible_pct"] == 100.0
