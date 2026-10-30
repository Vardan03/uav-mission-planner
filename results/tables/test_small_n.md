# Results: test_small_n

30 instances per method.

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 87.3 ± 13.5 | 3.1 ± 5.3 | 34.0 ± 7.2 | 100 | 0.03 ± 0.00 |
| lawnmower | 58.6 ± 15.9 | 35.0 ± 16.7 | 35.1 ± 7.1 | 100 | 0.00 ± 0.00 |
| ortools_1s | 90.2 ± 13.4 | 0.0 ± 0.0 | 36.0 ± 6.9 | 100 | 1.01 ± 0.00 |
| ortools_5s | 90.2 ± 13.4 | 0.0 ± 0.0 | 36.0 ± 6.9 | 100 | 5.01 ± 0.00 |
| ortools_30s | 90.2 ± 13.4 | 0.0 ± 0.0 | 36.0 ± 6.9 | 100 | 30.02 ± 0.02 |
| milp | 81.7 ± 17.0 | 8.6 ± 16.3 | 41.3 ± 3.7 | 100 | 225.82 ± 112.87 |

## Topology: uniform (10 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 84.7 ± 9.2 | 4.5 ± 3.4 | 37.4 ± 3.6 | 100 | 0.03 ± 0.00 |
| lawnmower | 57.2 ± 11.3 | 34.6 ± 14.7 | 40.0 ± 2.8 | 100 | 0.00 ± 0.00 |
| ortools_1s | 88.6 ± 8.2 | 0.0 ± 0.0 | 41.0 ± 2.5 | 100 | 1.01 ± 0.00 |
| ortools_5s | 88.6 ± 8.2 | 0.0 ± 0.0 | 41.0 ± 2.5 | 100 | 5.01 ± 0.00 |
| ortools_30s | 88.6 ± 8.2 | 0.0 ± 0.0 | 41.0 ± 2.5 | 100 | 30.03 ± 0.02 |
| milp | 82.3 ± 11.6 | 6.5 ± 13.5 | 41.6 ± 3.5 | 100 | 290.38 ± 29.70 |

## Topology: clustered (10 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 82.0 ± 17.9 | 1.4 ± 5.7 | 31.1 ± 8.3 | 100 | 0.03 ± 0.00 |
| lawnmower | 54.7 ± 18.2 | 35.5 ± 17.7 | 32.6 ± 7.5 | 100 | 0.00 ± 0.00 |
| ortools_1s | 83.5 ± 18.7 | 0.0 ± 0.0 | 33.3 ± 7.7 | 100 | 1.01 ± 0.00 |
| ortools_5s | 83.5 ± 18.7 | 0.0 ± 0.0 | 33.2 ± 7.6 | 100 | 5.01 ± 0.00 |
| ortools_30s | 83.5 ± 18.7 | 0.0 ± 0.0 | 33.2 ± 7.6 | 100 | 30.02 ± 0.02 |
| milp | 78.2 ± 18.8 | 5.0 ± 14.7 | 40.4 ± 4.1 | 100 | 164.87 ± 128.46 |

## Topology: corridor (10 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 95.1 ± 6.9 | 3.5 ± 5.9 | 33.7 ± 7.3 | 100 | 0.03 ± 0.00 |
| lawnmower | 63.8 ± 16.0 | 34.9 ± 17.5 | 32.6 ± 7.2 | 100 | 0.00 ± 0.00 |
| ortools_1s | 98.5 ± 3.1 | 0.0 ± 0.0 | 33.8 ± 6.5 | 100 | 1.01 ± 0.00 |
| ortools_5s | 98.5 ± 3.1 | 0.0 ± 0.0 | 33.8 ± 6.5 | 100 | 5.01 ± 0.00 |
| ortools_30s | 98.5 ± 3.1 | 0.0 ± 0.0 | 33.8 ± 6.5 | 100 | 30.02 ± 0.02 |
| milp | 84.5 ± 19.0 | 14.2 ± 18.8 | 42.1 ± 3.1 | 100 | 222.20 ± 113.74 |

## Exact MILP optimum

MILP proved optimality on 11 of 30 instances; the true gap uses those instances only.

| Method | True gap to MILP optimum (%) mean ± std | Instances |
|---|---|---|
| greedy | 4.6 ± 7.0 | 11 |
| lawnmower | 38.2 ± 15.8 | 11 |
| ortools_1s | 0.4 ± 1.3 | 11 |
| ortools_5s | 0.4 ± 1.3 | 11 |
| ortools_30s | 0.4 ± 1.3 | 11 |
| milp | 0.0 ± 0.0 | 11 |
