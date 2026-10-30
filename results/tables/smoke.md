# Results: smoke

5 instances per method.

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 76.8 ± 16.2 | 5.9 ± 11.9 | 26.7 ± 2.4 | 100 | 0.02 ± 0.01 |
| lawnmower | 41.0 ± 13.1 | 50.0 ± 12.4 | 26.8 ± 2.4 | 100 | 0.00 ± 0.00 |
| ortools_1s | 81.2 ± 11.0 | 0.0 ± 0.0 | 26.3 ± 2.4 | 100 | 1.01 ± 0.00 |
| ortools_5s | 81.2 ± 11.0 | 0.0 ± 0.0 | 26.3 ± 2.4 | 100 | 5.01 ± 0.00 |
| ortools_30s | 81.2 ± 11.0 | 0.0 ± 0.0 | 26.3 ± 2.4 | 100 | 30.01 ± 0.00 |

## Topology: uniform (2 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 67.6 ± 15.8 | 14.8 ± 14.8 | 28.8 ± 0.5 | 100 | 0.02 ± 0.00 |
| lawnmower | 37.2 ± 14.5 | 53.5 ± 15.6 | 25.0 ± 0.5 | 100 | 0.00 ± 0.00 |
| ortools_1s | 78.5 ± 4.8 | 0.0 ± 0.0 | 28.2 ± 1.1 | 100 | 1.01 ± 0.00 |
| ortools_5s | 78.5 ± 4.8 | 0.0 ± 0.0 | 28.2 ± 1.1 | 100 | 5.01 ± 0.00 |
| ortools_30s | 78.5 ± 4.8 | 0.0 ± 0.0 | 28.2 ± 1.1 | 100 | 30.01 ± 0.00 |

## Topology: clustered (2 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 74.4 ± 6.9 | 0.0 ± 0.0 | 23.7 ± 0.2 | 100 | 0.02 ± 0.00 |
| lawnmower | 35.8 ± 3.6 | 51.1 ± 9.3 | 27.2 ± 2.5 | 100 | 0.00 ± 0.00 |
| ortools_1s | 74.4 ± 6.9 | 0.0 ± 0.0 | 23.6 ± 0.4 | 100 | 1.00 ± 0.00 |
| ortools_5s | 74.4 ± 6.9 | 0.0 ± 0.0 | 23.6 ± 0.4 | 100 | 5.02 ± 0.00 |
| ortools_30s | 74.4 ± 6.9 | 0.0 ± 0.0 | 23.6 ± 0.4 | 100 | 30.01 ± 0.00 |

## Topology: corridor (1 instances)

| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) | Feasible (%) | Time per instance (s) |
|---|---|---|---|---|---|
| greedy | 100.0 ± 0.0 | 0.0 ± 0.0 | 28.1 ± 0.0 | 100 | 0.03 ± 0.00 |
| lawnmower | 59.2 ± 0.0 | 40.8 ± 0.0 | 29.7 ± 0.0 | 100 | 0.00 ± 0.00 |
| ortools_1s | 100.0 ± 0.0 | 0.0 ± 0.0 | 28.0 ± 0.0 | 100 | 1.01 ± 0.00 |
| ortools_5s | 100.0 ± 0.0 | 0.0 ± 0.0 | 28.0 ± 0.0 | 100 | 5.01 ± 0.00 |
| ortools_30s | 100.0 ± 0.0 | 0.0 ± 0.0 | 28.0 ± 0.0 | 100 | 30.01 ± 0.00 |
