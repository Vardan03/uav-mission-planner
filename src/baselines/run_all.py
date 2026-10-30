"""CLI: run chosen baselines on a split and write results/raw/<split>/<method>.csv."""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import time
from pathlib import Path

import pandas as pd
import yaml
from tqdm import tqdm

from src.baselines import greedy, lawnmower, milp, ortools_top
from src.baselines.solution import timed
from src.data_gen.instance import load_instance
from src.eval import checker, metrics

ALL_METHODS = ["greedy", "lawnmower", "ortools_1s", "ortools_5s", "ortools_30s", "milp"]
REFERENCE = "ortools_30s"


def get_solver(method: str, cfg: dict):
    """Return (solve_function, time_limit) for a method name."""
    if method == "greedy":
        return greedy.solve, None
    if method == "lawnmower":
        return lawnmower.solve, None
    if method.startswith("ortools_"):
        return ortools_top.solve, float(method[len("ortools_"):-1])
    if method == "milp":
        return milp.solve, float(cfg["milp"]["time_limit"])
    raise ValueError(f"unknown method {method}")


def run_job(job: tuple) -> dict:
    """Solve one (instance file, method) pair, check it and return the result row."""
    path, method, cfg = job
    inst = load_instance(path)
    solve, limit = get_solver(method, cfg)
    sol = timed(solve, inst, time_limit=limit, seed=0)
    violations = checker.check(inst, sol.routes)
    if violations:
        print(f"BUG: {method} seed {inst.seed} infeasible: {violations[:3]}", flush=True)
    return metrics.instance_row(inst, method, sol, violations)


def main() -> None:
    """Parse arguments, run all jobs in parallel and write one CSV per method."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", required=True)
    parser.add_argument("--methods", default="all", help="'all' or comma-separated names")
    parser.add_argument("--procs", type=int, default=max(1, (mp.cpu_count() or 2) - 1))
    parser.add_argument("--instances", default="data/instances")
    parser.add_argument("--out", default="results")
    parser.add_argument("--config", default="configs/baselines.yaml")
    parser.add_argument("--limit", type=int, help="only the first LIMIT instances (debugging)")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())
    files = sorted(Path(args.instances, args.split).glob("*.json"))[: args.limit]
    n_targets = load_instance(files[0]).N
    methods = ALL_METHODS if args.methods == "all" else args.methods.split(",")
    if "milp" in methods and n_targets > cfg["milp"]["max_n"]:
        print(f"skipping milp: N={n_targets} > {cfg['milp']['max_n']}")
        methods = [m for m in methods if m != "milp"]

    jobs = [(str(f), m, cfg) for m in methods for f in files]
    jobs.sort(key=lambda j: -(get_solver(j[1], cfg)[1] or 0))  # slow jobs first
    start = time.perf_counter()
    with mp.Pool(args.procs) as pool:
        rows = list(tqdm(pool.imap_unordered(run_job, jobs), total=len(jobs)))
    elapsed = time.perf_counter() - start

    out_dir = Path(args.out, "raw", args.split)
    out_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows, columns=metrics.COLUMNS)
    ref_path = out_dir / f"{REFERENCE}.csv"
    for method in methods:
        part = frame[frame["method"] == method].sort_values("seed")
        part.to_csv(out_dir / f"{method}.csv", index=False)
    if ref_path.exists():  # fill gap_vs_ref for every method CSV now present
        ref = pd.read_csv(ref_path)
        for csv in out_dir.glob("*.csv"):
            data = pd.read_csv(csv)
            metrics.add_gap(data, ref).to_csv(csv, index=False)

    log_path = Path(args.out, "run_times.json")
    log = json.loads(log_path.read_text()) if log_path.exists() else {}
    log[args.split] = {"methods": methods, "procs": args.procs, "seconds": round(elapsed, 1)}
    log_path.write_text(json.dumps(log, indent=2))
    n_bad = int((~frame["feasible"]).sum())
    print(f"{args.split}: {len(jobs)} jobs in {elapsed:.1f}s, infeasible: {n_bad}")


if __name__ == "__main__":
    main()
