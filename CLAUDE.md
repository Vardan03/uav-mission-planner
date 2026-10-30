# CLAUDE.md — UAV Mission Planning: baselines

## Project in one paragraph

We plan routes for a small UAV fleet. The problem is the **multi-depot Team Orienteering Problem with no-fly zones (MD-TOP-NFZ)**: N targets with priority weights, K depots with one UAV each, polygonal no-fly zones (NFZs), and a flight-distance budget B per UAV. Each UAV flies a closed route from its depot back to the same depot. The fleet maximises the total weight of visited targets. Every target is visited at most once. No route may exceed B. No flight leg may cross an NFZ.

The neural solver comes later. **This task is only the instance generator, the classical baselines, and the evaluation.** The goal is real numbers for the proposal's baseline table (Part 3 "small test" and Part 4 "baseline results").

## Your task, in order

1. Create the repository skeleton and environment (see Layout).
2. Write the instance generator with cleaning and validation (`src/data_gen/`).
3. Write the NFZ-aware distance computation (`src/data_gen/geometry.py`).
4. Write the feasibility checker and metrics (`src/eval/`). **Do this before any baseline.**
5. Write the baselines, in this order: greedy → lawnmower → OR-Tools → exact MILP (small N only) → GA (optional, only if time remains).
6. Write unit tests (`tests/`) and make them pass.
7. Run the benchmark on the evaluation sets and produce the results table and route plots.
8. Write `README.md` with the exact commands, hardware, run times and results.

Work in small steps. After each step, run its tests before moving on. If something in this file is ambiguous, choose the simplest reasonable option, write the decision in `docs/decisions.md`, and continue.

## Environment

- Python 3.10.
- Pin every version in `requirements.txt` (`pip freeze` subset after things work).
- Required: `numpy`, `scipy`, `shapely>=2.0`, `networkx`, `ortools==9.9.3963`, `pulp`, `pandas`, `matplotlib`, `pyyaml`, `pytest`, `tqdm`.
- Optional: `deap` (GA).
- Do **not** install PyTorch or PyG for this task.
- Everything must run on a laptop CPU.

## Layout

```text
README.md
CLAUDE.md
requirements.txt
Makefile
configs/
  data.yaml           generator parameters and split seed ranges
  baselines.yaml      time limits and baseline settings
src/
  data_gen/
    generate.py       instance generator (CLI)
    geometry.py       NFZ polygons, visibility graph, NFZ-aware distance matrix
    validate.py       cleaning and validation checks
    instance.py       Instance dataclass + save/load (JSON)
  baselines/
    greedy.py
    lawnmower.py
    ortools_top.py
    milp.py
    ga.py             optional
    run_all.py        CLI: run chosen baselines on a split, write results
  eval/
    checker.py        feasibility checker
    metrics.py        CR, gap, L_total, timing aggregation
    benchmark.py      CLI: build tables from results
    plots.py          route plots
data/
  instances/<split>/<seed>.json
results/
  raw/<split>/<method>.csv        one row per instance
  tables/<split>.md               summary tables
  plots/<split>/<seed>.png
docs/
  decisions.md
tests/
```

## Instance specification

Units: kilometres. Map: square `[0, 10] x [0, 10]`.

| Field | Type | Meaning |
| --- | --- | --- |
| `seed` | int | Generator seed; the instance is fully determined by it plus the config |
| `topology` | str | `uniform`, `clustered` or `corridor` |
| `targets` | float[N, 2] | Target coordinates |
| `weights` | int[N] | Integer weights in 1..10 |
| `depots` | float[K, 2] | Depot coordinates |
| `nfz` | list of polygons | Each polygon is a list of (x, y) vertices |
| `budget` | float | Per-UAV budget B in km |
| `dist` | float[N+K, N+K] | NFZ-aware shortest-path distance matrix; index 0..K-1 = depots, K..K+N-1 = targets |
| `flags` | dict | e.g. `unreachable_targets`: target indices no depot can serve within budget |

Store instances as JSON. Store `dist` in the JSON too, so every baseline uses exactly the same distances.

### Generation

- **Topology** is chosen by `seed % 3` → 0 uniform, 1 clustered, 2 corridor (balanced splits).
- **Uniform:** targets uniform in the map with a 0.3 km margin.
- **Clustered:** 3–6 cluster centres uniform in the map; each target from a Gaussian around a random centre, σ uniform in [0.4, 1.0] km; clip to the map.
- **Corridor:** 1–3 random polylines (3–5 vertices each); each target sampled at a random position along a random polyline plus perpendicular Gaussian noise, σ = 0.25 km.
- **Weights:** integers uniform in 1..10.
- **Depots:** K points near the map edges (within 1 km of the boundary), at least 3 km apart from each other.
- **NFZs:** 0–3 polygons. Each is a random convex hull of 5–8 points around a random centre, radius 0.8–2.0 km, so that total NFZ area is 5–20% of the map. Polygons may overlap; merge overlapping ones with `unary_union`.
- **Budget:** B = 15 km by default (configurable).

### Cleaning and validation (`validate.py`)

Apply these checks in order. Log every repair with the seed. Regenerate the instance (same seed + attempt counter) if a repair fails 20 times.

1. Polygon invalid or self-intersecting → `shapely.make_valid`; reject if still invalid.
2. Depot inside or within 0.2 km of an NFZ → resample the depot.
3. Target inside or within 0.05 km of an NFZ → resample the target.
4. Two targets closer than 0.001 km → resample one.
5. NaN, out-of-bounds coordinates, weight outside 1..10 → raise an error (generator bug, not data noise).
6. Target whose round trip from every depot exceeds B, i.e. `2 * dist[d, t] > B` for all depots d → keep it, but list it in `flags.unreachable_targets`.
7. A target with no finite-distance path to any depot → resample it.

### NFZ-aware distances (`geometry.py`)

- Build a visibility graph whose nodes are all depots, all targets, and all NFZ polygon vertices. Push each polygon vertex outward by 1e-6 km so that grazing segments are not falsely blocked.
- Two nodes are connected if the straight segment between them does not intersect the interior of any NFZ. Use `shapely` prepared geometries for speed.
- Edge weight = Euclidean length.
- `dist[i, j]` = Dijkstra shortest path in this graph (`scipy.sparse.csgraph.shortest_path` is fine).
- Also return the actual path vertices for each pair (or a way to reconstruct them) so that plots draw real detours, not straight lines.
- Sanity test: with no NFZs, `dist` must equal the Euclidean distance matrix (tolerance 1e-9).

## Splits (`configs/data.yaml`)

| Split | Instances | N | K | Seeds | Purpose |
| --- | --- | --- | --- | --- | --- |
| `smoke` | 5 | 20 | 2 | 9000–9004 | Fast end-to-end check |
| `small_test` | 20 | 50 | 3 | 1000–1019 | Proposal Part 3 "small test" |
| `test` | 100 | 50 | 3 | 1000–1099 | Main baseline table |
| `test_small_n` | 30 | 20 | 3 | 4000–4029 | Exact MILP optimum, true optimality gap |
| `test_large` | 50 | 100 | 3 | 2000–2049 | Scaling check (optional) |

Validation and training splits are not needed for this task.

## Baselines

Every baseline has the same interface:

```python
def solve(inst: Instance, time_limit: float | None = None, seed: int = 0) -> Solution
# Solution: routes: list[list[int]], one per depot, each a list of target indices (0..N-1),
#           depot start/end implicit; plus solve_time (s) and any solver status string.
```

Every route a baseline returns must pass `checker.py`. A baseline that returns an infeasible route is a bug: fix it, do not report it.

### 1. Greedy (weight per detour, budget-aware)

Build all K routes at the same time. At each step, over all UAVs and all unvisited targets, compute the cheapest insertion position into that UAV's route and its added distance Δ. Skip insertions that would make the route exceed B. Choose the (UAV, target, position) with the highest `w / (Δ + ε)`, with ε = 1e-6. Stop when no feasible insertion exists. Then apply 2-opt to each route to shorten it and, if 2-opt freed budget, try more insertions. Repeat until nothing changes.

### 2. Lawnmower sweep

This baseline imitates a priority-blind coverage sweep.

- Split the map into K vertical strips of equal width. Assign each strip to the nearest depot. If two strips get the same depot, use a minimum-cost assignment (`scipy.optimize.linear_sum_assignment`) on strip-centre-to-depot distances.
- Inside each strip, sort targets in boustrophedon order: divide the strip into horizontal lanes of height 1 km; traverse lanes bottom to top, left-to-right on even lanes and right-to-left on odd lanes.
- The UAV visits targets in that order, ignoring weights, and skips a target only if visiting it and returning to the depot would exceed B. It stops when no remaining target in its strip can be visited.
- Distances use the NFZ-aware matrix.

### 3. OR-Tools (routing solver + Guided Local Search)

- Use `pywrapcp.RoutingIndexManager(n_nodes, K, starts, ends)` with `starts = ends = [0..K-1]` (each vehicle returns to its own depot).
- Arc cost = NFZ-aware distance scaled to integers: `round(dist * 1000)` (metres).
- Distance dimension with capacity `round(B * 1000)` per vehicle, slack 0, `fix_start_cumul_to_zero=True`.
- Make every target optional: `AddDisjunction([index], penalty)` with `penalty = weight * M`, where M is larger than any route cost (for example `M = 10 * round(B * 1000) * K`). This makes the solver prefer visiting targets over saving distance, so it maximises collected weight first and shortens routes second.
- First solution strategy: `PATH_CHEAPEST_ARC`. Metaheuristic: `GUIDED_LOCAL_SEARCH`.
- Run with time limits **1 s, 5 s and 30 s** on every instance and report each as a separate method (`ortools_1s`, `ortools_5s`, `ortools_30s`). `ortools_30s` is the reference for the gap.
- Set `log_search=False`. Fix the random seed if the API allows; otherwise note in `docs/decisions.md` that GLS is deterministic for fixed inputs.

### 4. Exact MILP (only N ≤ 20)

- Formulate the TOP with PuLP + CBC: binary `x[i, j, k]` for arcs, binary `y[i, k]` for visits, per-vehicle budget constraint, flow conservation, each target visited at most once across vehicles, MTZ subtour elimination with continuous `u[i, k]`.
- Objective: maximise Σ w_i y[i, k].
- Time limit 300 s per instance. Record whether CBC proved optimality. Report only instances solved to proven optimality in the "true gap" table; count the others.

### 5. Genetic algorithm (optional)

Only if everything above is done and tested. A giant-tour chromosome (a permutation of targets) decoded greedily into K budget-feasible routes. DEAP, population 100, 200 generations, ordered crossover, swap mutation. Report with the same columns.

## Feasibility checker (`checker.py`)

For a solution, verify and return a list of violations (empty list = feasible):

- Exactly K routes; route k starts and ends at depot k.
- Every target index appears in at most one route, at most once.
- Route length (sum of `dist` over consecutive nodes, including depot→first and last→depot) ≤ B + 1e-6.
- Every leg's real path (from the visibility-graph path) does not enter any NFZ interior. This is guaranteed if `dist` is built correctly, but check it anyway in tests.

## Metrics (`metrics.py`)

Per instance and method:

- `CR = 100 * sum(weights of visited targets) / sum(all weights)`
- `CR_achievable = 100 * sum(visited weights) / sum(weights of targets not in flags.unreachable_targets)`
- `L_total` = sum of route lengths (km)
- `time_s` = wall-clock solve time, measured with `time.perf_counter()` around `solve()` only
- `feasible` = checker returned no violations

Per method over a split: mean ± std of each metric, feasibility rate, and `gap = 100 * (CR_ref - CR) / CR_ref` per instance against `ortools_30s` (and against the MILP optimum on `test_small_n`).

## Outputs

- `results/raw/<split>/<method>.csv` with columns: `seed, topology, N, K, method, CR, CR_achievable, gap_vs_ref, L_total, n_visited, time_s, feasible, status`.
- `results/tables/<split>.md`: one markdown table with rows = methods and columns = `CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s)`. Add one more table per topology below it.
- `results/plots/<split>/<seed>.png` for 3 instances (one per topology): the map, NFZs shaded, depots as squares, targets as circles sized by weight, one colour per UAV, routes drawn along the real NFZ-avoiding paths. One subplot per method side by side.
- `results/summary.json` with the hardware (CPU model from `platform`/`/proc/cpuinfo`), Python version, package versions, git commit if available, and total run time.

## Makefile targets

```make
make env          # pip install -r requirements.txt
make data         # generate all splits into data/instances/
make test         # pytest -q
make smoke        # all baselines on the smoke split (should take < 1 min)
make baselines    # all baselines on small_test, test, test_small_n
make tables       # build results/tables/*.md and plots
make all          # data test baselines tables
```

`make baselines` runs instances in parallel with `multiprocessing` (one process per CPU core minus one). OR-Tools 30 s on 100 instances is about 50 minutes sequentially, so parallelism matters.

## Tests (`tests/`)

- Generator is deterministic: same seed → identical JSON.
- Every generated instance passes validation; no target or depot inside an NFZ.
- With no NFZs, the distance matrix equals Euclidean distances.
- With one square NFZ between two points, `dist` is strictly larger than the Euclidean distance and equals the hand-computed detour length.
- Checker catches: a route over budget, a duplicated target, a route ending at the wrong depot.
- Every baseline returns a feasible solution on all `smoke` instances.
- On a tiny hand-made instance (N = 5, K = 1) with an obvious optimum, MILP finds it and OR-Tools 5 s matches it.
- Metric functions on a hand-computed example.

## Rules

- **Never invent or estimate numbers.** If a run fails or is not done, leave the cell as `—` and say why in the README.
- Never change the evaluation instances after results are produced. If the generator changes, bump a `generator_version` field and regenerate everything.
- Do not tune any baseline on the `test` split. Use `smoke` or `small_test` for debugging.
- Keep each file short and readable; second-year students will continue this code in January. Docstrings on every public function. No clever one-liners.
- Record every non-obvious choice in `docs/decisions.md` (one line each, dated).

## Definition of done

- `make all` runs from a clean clone without errors.
- `pytest` passes.
- `results/tables/small_test.md` and `results/tables/test.md` exist with real numbers for greedy, lawnmower, OR-Tools 1/5/30 s; `results/tables/test_small_n.md` includes the MILP optimum.
- Every reported solution is feasible (100% feasibility for every method).
- Route plots exist for at least three instances.
- `README.md` contains: setup, commands, hardware, run time per step, the results tables, and known limitations.
- At the end, print a short summary: what was built, the main results table for `test`, and anything that did not work.
