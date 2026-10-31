"""CLI: route plots, one figure per topology with one subplot per method."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon as MplPolygon

from src.baselines import greedy, lawnmower, ortools_top
from src.data_gen import geometry
from src.data_gen.instance import Instance, load_instance
from src.eval import metrics

COLOURS = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
# Routes are not stored in the CSVs, so the plotted methods are solved again here.
PLOT_METHODS = {
    "greedy": lambda inst: greedy.solve(inst),
    "lawnmower": lambda inst: lawnmower.solve(inst),
    "ortools_5s": lambda inst: ortools_top.solve(inst, time_limit=5),
}


def draw_solution(ax, inst: Instance, graph, routes: list, title: str) -> None:
    """Draw map, NFZs, depots, targets and routes along the real NFZ-avoiding paths."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    for poly in inst.nfz:
        ax.add_patch(MplPolygon(poly, closed=True, color="grey", alpha=0.5, zorder=1))
    for k, route in enumerate(routes):
        nodes = [k] + [inst.K + t for t in route] + [k]
        for a, b in zip(nodes[:-1], nodes[1:]):
            path = graph.path(a, b)
            if len(path):
                ax.plot(path[:, 0], path[:, 1], color=COLOURS[k % 5], lw=1.5, zorder=2)
    visited = {t for r in routes for t in r}
    sizes = 15 + 12 * inst.weights
    ax.scatter(*inst.targets[list(visited)].T, s=sizes[list(visited)], c="black", zorder=3)
    missed = [t for t in range(inst.N) if t not in visited]
    ax.scatter(*inst.targets[missed].T, s=sizes[missed], facecolors="none",
               edgecolors="grey", zorder=3)
    for k, depot in enumerate(inst.depots):
        ax.scatter(*depot, marker="s", s=110, c=COLOURS[k % 5], edgecolors="black", zorder=4)
    ax.set_title(title, fontsize=9)


def plot_instance(inst: Instance, out_path: Path) -> None:
    """Save one figure with a subplot per method for this instance."""
    graph = geometry.NFZGraph(inst.points, inst.nfz)
    fig, axes = plt.subplots(1, len(PLOT_METHODS), figsize=(5 * len(PLOT_METHODS), 5))
    for ax, (name, solve) in zip(axes, PLOT_METHODS.items()):
        routes = solve(inst).routes
        title = f"{name}: CR {metrics.cr(inst, routes):.1f}%, L {metrics.total_length(inst, routes):.1f} km"
        draw_solution(ax, inst, graph, routes, title)
    fig.suptitle(f"seed {inst.seed} ({inst.topology}), N={inst.N}, K={inst.K}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Plot the first instance of each topology of a split."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", required=True)
    parser.add_argument("--instances", default="data/instances")
    parser.add_argument("--out", default="results/plots")
    args = parser.parse_args()
    matplotlib.use("Agg")  # the CLI only writes files; notebooks keep their own backend
    seen = set()
    for path in sorted(Path(args.instances, args.split).glob("*.json")):
        inst = load_instance(path)
        if inst.topology in seen:
            continue
        seen.add(inst.topology)
        plot_instance(inst, Path(args.out, args.split, f"{inst.seed}.png"))
        print(f"plotted {args.split}/{inst.seed} ({inst.topology})")
        if len(seen) == 3:
            break


if __name__ == "__main__":
    main()
