# Results: small_test

20 instances per method.

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 84.2 ± 15.0 | 3.1 ± 5.2 | 41.8 ± 2.6 | 100 | 0.26 ± 0.04 |
| lawnmower | 45.7 ± 17.0 | 48.0 ± 14.6 | 38.5 ± 6.3 | 100 | 0.00 ± 0.00 |
| ortools_1s | 86.3 ± 15.3 | 0.7 ± 2.0 | 41.3 ± 5.0 | 100 | 1.01 ± 0.00 |
| ortools_5s | 86.5 ± 15.3 | 0.6 ± 1.7 | 41.7 ± 4.8 | 100 | 5.01 ± 0.00 |
| ortools_30s | 87.0 ± 15.2 | 0.0 ± 0.0 | 41.7 ± 4.9 | 100 | 30.02 ± 0.00 |

## Topology: uniform (6 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 72.1 ± 11.0 | 0.7 ± 4.7 | 43.8 ± 0.7 | 100 | 0.23 ± 0.03 |
| lawnmower | 33.6 ± 7.4 | 52.6 ± 12.5 | 43.8 ± 0.7 | 100 | 0.00 ± 0.00 |
| ortools_1s | 72.6 ± 10.6 | 0.0 ± 0.0 | 44.2 ± 0.5 | 100 | 1.01 ± 0.00 |
| ortools_5s | 72.6 ± 10.6 | 0.0 ± 0.0 | 44.2 ± 0.5 | 100 | 5.01 ± 0.00 |
| ortools_30s | 72.6 ± 10.6 | 0.0 ± 0.0 | 44.2 ± 0.5 | 100 | 30.01 ± 0.00 |

## Topology: clustered (7 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 88.4 ± 14.6 | 2.3 ± 2.2 | 40.1 ± 2.8 | 100 | 0.27 ± 0.04 |
| lawnmower | 50.1 ± 19.2 | 45.9 ± 15.6 | 35.8 ± 7.0 | 100 | 0.00 ± 0.00 |
| ortools_1s | 90.4 ± 15.4 | 0.2 ± 0.3 | 40.4 ± 4.4 | 100 | 1.01 ± 0.00 |
| ortools_5s | 90.6 ± 15.4 | 0.0 ± 0.0 | 40.5 ± 4.6 | 100 | 5.01 ± 0.00 |
| ortools_30s | 90.6 ± 15.4 | 0.0 ± 0.0 | 40.4 ± 4.6 | 100 | 30.02 ± 0.00 |

## Topology: corridor (7 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 90.3 ± 12.1 | 6.0 ± 6.2 | 41.7 ± 2.4 | 100 | 0.27 ± 0.03 |
| lawnmower | 51.5 ± 15.0 | 46.2 ± 14.3 | 36.6 ± 5.2 | 100 | 0.00 ± 0.00 |
| ortools_1s | 94.0 ± 10.0 | 1.9 ± 3.1 | 39.8 ± 6.4 | 100 | 1.01 ± 0.00 |
| ortools_5s | 94.2 ± 9.5 | 1.6 ± 2.6 | 40.7 ± 6.1 | 100 | 5.01 ± 0.00 |
| ortools_30s | 95.6 ± 7.7 | 0.0 ± 0.0 | 41.0 ± 6.2 | 100 | 30.02 ± 0.00 |
