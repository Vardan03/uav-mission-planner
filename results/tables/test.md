# Results: test

100 instances per method.

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 80.6 ± 13.1 | 5.8 ± 7.2 | 41.0 ± 4.0 | 100 | 0.26 ± 0.04 |
| lawnmower | 44.0 ± 14.0 | 48.6 ± 13.7 | 38.3 ± 6.2 | 100 | 0.00 ± 0.00 |
| ortools_1s | 85.0 ± 12.2 | 0.6 ± 1.7 | 41.4 ± 4.8 | 100 | 1.01 ± 0.00 |
| ortools_5s | 85.5 ± 11.9 | 0.0 ± 0.0 | 41.5 ± 4.8 | 100 | 5.00 ± 0.00 |
| ortools_30s | 85.5 ± 11.9 | 0.0 ± 0.0 | 41.5 ± 4.8 | 100 | 30.01 ± 0.00 |

## Topology: uniform (33 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 70.3 ± 8.0 | 5.2 ± 7.0 | 42.7 ± 1.4 | 100 | 0.23 ± 0.03 |
| lawnmower | 37.0 ± 7.6 | 50.0 ± 10.0 | 43.3 ± 1.2 | 100 | 0.00 ± 0.00 |
| ortools_1s | 73.6 ± 7.2 | 0.9 ± 2.0 | 43.8 ± 1.1 | 100 | 1.01 ± 0.00 |
| ortools_5s | 74.2 ± 7.1 | 0.0 ± 0.0 | 43.9 ± 0.7 | 100 | 5.00 ± 0.00 |
| ortools_30s | 74.2 ± 7.1 | 0.0 ± 0.0 | 43.9 ± 0.7 | 100 | 30.01 ± 0.00 |

## Topology: clustered (34 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 84.0 ± 12.2 | 6.1 ± 7.1 | 39.6 ± 4.6 | 100 | 0.27 ± 0.04 |
| lawnmower | 47.5 ± 15.8 | 47.2 ± 15.0 | 34.8 ± 6.2 | 100 | 0.00 ± 0.00 |
| ortools_1s | 89.3 ± 10.8 | 0.1 ± 0.5 | 40.0 ± 5.1 | 100 | 1.01 ± 0.00 |
| ortools_5s | 89.5 ± 10.8 | 0.0 ± 0.0 | 40.1 ± 5.2 | 100 | 5.00 ± 0.00 |
| ortools_30s | 89.5 ± 10.8 | 0.0 ± 0.0 | 40.1 ± 5.2 | 100 | 30.01 ± 0.00 |

## Topology: corridor (33 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 87.3 ± 11.6 | 6.0 ± 7.5 | 40.8 ± 4.5 | 100 | 0.28 ± 0.03 |
| lawnmower | 47.5 ± 14.4 | 48.6 ± 15.2 | 37.0 ± 6.1 | 100 | 0.00 ± 0.00 |
| ortools_1s | 92.1 ± 8.7 | 0.7 ± 2.0 | 40.4 ± 5.7 | 100 | 1.01 ± 0.00 |
| ortools_5s | 92.7 ± 8.2 | 0.0 ± 0.1 | 40.6 ± 5.7 | 100 | 5.00 ± 0.00 |
| ortools_30s | 92.7 ± 8.1 | 0.0 ± 0.0 | 40.6 ± 5.7 | 100 | 30.01 ± 0.00 |
