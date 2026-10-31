# UAV mission planning: classical baselines for MD-TOP-NFZ

Instance generator, NFZ-aware distances, feasibility checker and classical baselines
(greedy, lawnmower, OR-Tools, exact MILP) for the multi-depot Team Orienteering Problem
with no-fly zones. The neural solver comes later. See `CLAUDE.md` for the full spec and
`docs/decisions.md` for every non-obvious choice.

## Setup

Python 3.10 is required.

```
py -3.10 -m venv .venv
.venv\Scriptsctivate
pip install -r requirements.txt
```

## Commands

`make` is not installed on the Windows machine used here, so each target below was run
as the plain command. The Makefile targets wrap exactly these commands.

| Step | Command (`make` target) |
|---|---|
| Generate all splits | `python -m src.data_gen.generate --all` (`make data`) |
| Tests | `python -m pytest -q` (`make test`) |
| Smoke run | `python -m src.baselines.run_all --split smoke --methods greedy,lawnmower,ortools_1s,ortools_5s,ortools_30s` (`make smoke`) |
| Baselines | `python -m src.baselines.run_all --split <small_test\|test\|test_small_n> --methods all` (`make baselines`) |
| Tables and plots | `python -m src.eval.benchmark --all` then `python -m src.eval.plots --split <split>` (`make tables`) |
| Pilot demo | open `notebooks/pilot_demo.ipynb` (loads one instance, runs lawnmower, greedy and OR-Tools 5 s, shows metrics and routes) |

`run_all` skips the MILP when N > 20. Instances run in parallel, one process per core minus one.

## Hardware and run times

- CPU: 12th Gen Intel Core i5-12450H (12 logical cores), 16 GB RAM, Windows 11. 11 worker processes.
- Python 3.10.11. Package versions are in `requirements.txt` and `results/summary.json`.

| Step | Wall time |
|---|---|
| Generate all 205 instances | about 3 s |
| `pytest` (18 tests) | about 11 s |
| smoke (5 instances, no MILP) | 31.5 s |
| small_test (20 instances, 5 methods) | 67.9 s |
| test (100 instances, 5 methods) | 332.7 s |
| test_small_n (30 instances, 6 methods incl. MILP, 300 s limit) | 746.2 s |

Per-instance times in the tables were measured while 11 instances ran in parallel, so
they are indicative. greedy and lawnmower are most affected; OR-Tools runs to its limit.

## Results

All numbers come from `results/raw/`. Every reported solution passed the checker (feasibility 100% for every method).
Per-topology tables are in `results/tables/<split>.md`. Route plots are in `results/plots/` (regenerate with the plots command).

### test (100 instances, N=50, K=3, B=15 km)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 80.6 ± 13.1 | 5.8 ± 7.2 | 41.0 ± 4.0 | 100 | 0.26 ± 0.04 |
| lawnmower | 44.0 ± 14.0 | 48.6 ± 13.7 | 38.3 ± 6.2 | 100 | 0.00 ± 0.00 |
| ortools_1s | 85.0 ± 12.2 | 0.6 ± 1.7 | 41.4 ± 4.8 | 100 | 1.01 ± 0.00 |
| ortools_5s | 85.5 ± 11.9 | 0.0 ± 0.0 | 41.5 ± 4.8 | 100 | 5.00 ± 0.00 |
| ortools_30s | 85.5 ± 11.9 | 0.0 ± 0.0 | 41.5 ± 4.8 | 100 | 30.01 ± 0.00 |

### small_test (20 instances, N=50, K=3)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 84.2 ± 15.0 | 3.1 ± 5.2 | 41.8 ± 2.6 | 100 | 0.26 ± 0.04 |
| lawnmower | 45.7 ± 17.0 | 48.0 ± 14.6 | 38.5 ± 6.3 | 100 | 0.00 ± 0.00 |
| ortools_1s | 86.3 ± 15.3 | 0.7 ± 2.0 | 41.3 ± 5.0 | 100 | 1.01 ± 0.00 |
| ortools_5s | 86.5 ± 15.3 | 0.6 ± 1.7 | 41.7 ± 4.8 | 100 | 5.01 ± 0.00 |
| ortools_30s | 87.0 ± 15.2 | 0.0 ± 0.0 | 41.7 ± 4.9 | 100 | 30.02 ± 0.00 |

### test_small_n (30 instances, N=20, K=3)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 87.3 ± 13.5 | 3.1 ± 5.3 | 34.0 ± 7.2 | 100 | 0.03 ± 0.00 |
| lawnmower | 58.6 ± 15.9 | 35.0 ± 16.7 | 35.1 ± 7.1 | 100 | 0.00 ± 0.00 |
| ortools_1s | 90.2 ± 13.4 | 0.0 ± 0.0 | 36.0 ± 6.9 | 100 | 1.01 ± 0.00 |
| ortools_5s | 90.2 ± 13.4 | 0.0 ± 0.0 | 36.0 ± 6.9 | 100 | 5.01 ± 0.00 |
| ortools_30s | 90.2 ± 13.4 | 0.0 ± 0.0 | 36.0 ± 6.9 | 100 | 30.02 ± 0.02 |
| milp | 81.7 ± 17.0 | 8.6 ± 16.3 | 41.3 ± 3.7 | 100 | 225.82 ± 112.87 |

Exact MILP optimum (300 s limit per instance):

MILP proved optimality on 11 of 30 instances; the true gap uses those instances only.

| Method | True gap to MILP optimum (%) mean ± std | Instances |
|---|---|---|
| greedy | 4.6 ± 7.0 | 11 |
| lawnmower | 38.2 ± 15.8 | 11 |
| ortools_1s | 0.4 ± 1.3 | 11 |
| ortools_5s | 0.4 ± 1.3 | 11 |
| ortools_30s | 0.4 ± 1.3 | 11 |
| milp | 0.0 ± 0.0 | 11 |

## Known limitations

- `small_test` (seeds 1000-1019) is the first 20 instances of `test` (1000-1099), as specified. They are not independent.
- `ortools_30s` is the reference for the gap, but it is a heuristic, not an optimum. The true gap exists only on `test_small_n`, and only on the instances where CBC proved optimality (see the count above). On unproven instances the MILP result is only a feasible solution and is often worse than OR-Tools.
- The MILP formulation was improved on `test_small_n` (arrival-distance variables instead of MTZ). The `test` split was not used for tuning any baseline.
- `test_large` (N=100) was generated but not run. The GA baseline was not implemented (optional in the spec).
- Timing was taken under parallel load (see above).
- Differences from the spec (OR-Tools costs rounded up, CBC without `threads`, MILP not in smoke, NFZs kept inside the map, holes filled) are listed in `docs/decisions.md`.
- `make all` was not run from a clean clone because `make` is unavailable here; the equivalent commands were run one by one.
- Instances are synthetic (generator version 1). Lawnmower is a deliberately priority-blind reference.
