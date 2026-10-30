"""CLI: build results/tables/<split>.md and results/summary.json from results/raw."""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd

METHOD_ORDER = ["greedy", "lawnmower", "ortools_1s", "ortools_5s", "ortools_30s", "milp"]
DASH = "—"
HEADER = (
    "| Method | CR (%) mean ± std | Gap vs OR-Tools 30 s (%) | L_total (km) "
    "| Feasible (%) | Time per instance (s) |\n|---|---|---|---|---|---|\n"
)


def mean_std(values: pd.Series, digits: int = 1) -> str:
    """Format 'mean ± std', or a dash if there are no values."""
    values = values.dropna()
    if values.empty:
        return DASH
    return f"{values.mean():.{digits}f} ± {values.std(ddof=0):.{digits}f}"


def load_split(raw_dir: Path) -> dict:
    """Read every method CSV of a split into {method: DataFrame}, in table order."""
    frames = {p.stem: pd.read_csv(p) for p in raw_dir.glob("*.csv")}
    return {m: frames[m] for m in METHOD_ORDER if m in frames}


def method_table(frames: dict) -> str:
    """Markdown table with one row per method."""
    out = HEADER
    for method, df in frames.items():
        out += (
            f"| {method} | {mean_std(df['CR'])} | {mean_std(df['gap_vs_ref'])} "
            f"| {mean_std(df['L_total'])} | {100 * df['feasible'].mean():.0f} "
            f"| {mean_std(df['time_s'], 2)} |\n"
        )
    return out


def milp_table(frames: dict) -> str:
    """True gap to the proven MILP optimum, using only instances CBC solved to optimality."""
    milp = frames["milp"]
    proven = milp[milp["status"] == "optimal"].set_index("seed")["CR"]
    out = (
        f"MILP proved optimality on {len(proven)} of {len(milp)} instances; "
        "the true gap uses those instances only.\n\n"
        "| Method | True gap to MILP optimum (%) mean ± std | Instances |\n|---|---|---|\n"
    )
    for method, df in frames.items():
        sub = df[df["seed"].isin(proven.index)]
        gaps = 100 * (proven.loc[sub["seed"]].to_numpy() - sub["CR"].to_numpy()) / proven.loc[
            sub["seed"]
        ].to_numpy()
        text = DASH if len(gaps) == 0 else mean_std(pd.Series(gaps))
        out += f"| {method} | {text} | {len(gaps)} |\n"
    return out


def build_table(split: str, raw_dir: Path) -> str:
    """Full markdown for one split: overall table, per-topology tables, MILP table."""
    frames = load_split(raw_dir)
    n_inst = len(next(iter(frames.values())))
    text = f"# Results: {split}\n\n{n_inst} instances per method.\n\n" + method_table(frames)
    for topology in ["uniform", "clustered", "corridor"]:
        part = {m: df[df["topology"] == topology] for m, df in frames.items()}
        text += f"\n## Topology: {topology} ({len(next(iter(part.values())))} instances)\n\n"
        text += method_table(part)
    if "milp" in frames:
        text += "\n## Exact MILP optimum\n\n" + milp_table(frames)
    return text


def hardware() -> dict:
    """CPU model and core count of this machine."""
    cpu = platform.processor() or platform.machine()
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    return {"cpu": cpu, "logical_cores": __import__("os").cpu_count(), "os": platform.platform()}


def write_summary(out_dir: Path) -> None:
    """Write results/summary.json with hardware, versions, git commit and run times."""
    packages = ["numpy", "scipy", "shapely", "networkx", "ortools", "pulp", "pandas", "matplotlib"]
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = None
    times_path = out_dir / "run_times.json"
    times = json.loads(times_path.read_text()) if times_path.exists() else {}
    summary = {
        "hardware": hardware(),
        "python": sys.version.split()[0],
        "packages": {p: metadata.version(p) for p in packages},
        "git_commit": commit,
        "run_times_s": times,
        "total_run_time_s": round(sum(v["seconds"] for v in times.values()), 1),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))


def main() -> None:
    """Build the tables for the chosen splits (or all splits found in results/raw)."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="results")
    parser.add_argument("--split")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    out_dir = Path(args.results)
    splits = [p.name for p in sorted((out_dir / "raw").iterdir()) if p.is_dir()]
    if args.split and not args.all:
        splits = [args.split]
    (out_dir / "tables").mkdir(exist_ok=True)
    for split in splits:
        if not list((out_dir / "raw" / split).glob("*.csv")):
            continue
        (out_dir / "tables" / f"{split}.md").write_text(
            build_table(split, out_dir / "raw" / split), encoding="utf-8"
        )
        print(f"wrote tables/{split}.md")
    write_summary(out_dir)


if __name__ == "__main__":
    main()
