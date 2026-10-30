"""Every baseline must return feasible solutions on the smoke instances."""
from pathlib import Path

import numpy as np
import pytest
import yaml

from src.baselines import greedy, lawnmower, milp, ortools_top
from src.data_gen import geometry
from src.data_gen.generate import generate_instance
from src.data_gen.instance import Instance
from src.eval import checker, metrics

CFG = yaml.safe_load((Path(__file__).parents[1] / "configs" / "data.yaml").read_text())
SMOKE = CFG["splits"]["smoke"]
SMOKE_INSTANCES = [
    generate_instance(s, SMOKE["n"], SMOKE["k"], CFG)
    for s in range(SMOKE["seed_start"], SMOKE["seed_start"] + SMOKE["count"])
]
SOLVERS = {
    "greedy": greedy.solve,
    "lawnmower": lawnmower.solve,
    "ortools_1s": lambda inst: ortools_top.solve(inst, time_limit=1),
}


@pytest.mark.parametrize("name", list(SOLVERS))
def test_baseline_feasible_on_smoke(name):
    for inst in SMOKE_INSTANCES:
        sol = SOLVERS[name](inst)
        assert checker.check(inst, sol.routes) == [], (name, inst.seed)


def collected_weight(solver) -> int:
    """Total weight collected by a solver over all smoke instances."""
    total = 0
    for inst in SMOKE_INSTANCES:
        total += sum(inst.weights[t] for route in solver(inst).routes for t in route)
    return int(total)


def test_greedy_collects_at_least_as_much_as_lawnmower():
    greedy_total = collected_weight(greedy.solve)
    assert greedy_total > 0 and greedy_total >= collected_weight(lawnmower.solve)


def tiny_instance() -> Instance:
    """N=5 targets on a line, K=1, budget 8: optimum visits x=1..4 for weight 13."""
    depots = np.array([[0.0, 0.0]])
    targets = np.array([[float(x), 0.0] for x in range(1, 6)])
    dist = geometry.distance_matrix(np.vstack([depots, targets]), [])
    return Instance(seed=0, topology="uniform", targets=targets,
                    weights=np.array([1, 1, 1, 10, 1]), depots=depots, nfz=[],
                    budget=8.0, dist=dist, flags={"unreachable_targets": [4]})


def test_milp_and_ortools_find_obvious_optimum():
    inst = tiny_instance()
    for sol in (milp.solve(inst, time_limit=30), ortools_top.solve(inst, time_limit=5)):
        assert checker.check(inst, sol.routes) == []
        assert metrics.visited_weight(inst, sol.routes) == 13
    assert milp.solve(inst, time_limit=30).status == "optimal"
