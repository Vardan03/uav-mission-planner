"""Instance dataclass and JSON save/load.

Node indexing used everywhere: 0..K-1 are depots, K..K+N-1 are targets,
so target i has node index K + i in `dist`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class Instance:
    """One MD-TOP-NFZ problem instance with its NFZ-aware distance matrix."""

    seed: int
    topology: str
    targets: np.ndarray  # (N, 2) km
    weights: np.ndarray  # (N,) ints in 1..10
    depots: np.ndarray  # (K, 2) km
    nfz: list  # list of polygons, each a list of (x, y) vertices
    budget: float  # per-UAV flight budget, km
    dist: np.ndarray  # (N+K, N+K) km, np.inf if no path
    flags: dict = field(default_factory=dict)
    generator_version: int = 1

    @property
    def N(self) -> int:
        """Number of targets."""
        return len(self.targets)

    @property
    def K(self) -> int:
        """Number of depots (= number of UAVs)."""
        return len(self.depots)

    @property
    def points(self) -> np.ndarray:
        """Coordinates of all nodes, depots first, then targets."""
        return np.vstack([self.depots, self.targets])


def to_dict(inst: Instance) -> dict:
    """Convert an instance to a JSON-ready dict (inf distances become null)."""
    dist = [[None if np.isinf(v) else float(v) for v in row] for row in inst.dist]
    return {
        "generator_version": inst.generator_version,
        "seed": inst.seed,
        "topology": inst.topology,
        "targets": inst.targets.tolist(),
        "weights": inst.weights.tolist(),
        "depots": inst.depots.tolist(),
        "nfz": [[list(map(float, v)) for v in poly] for poly in inst.nfz],
        "budget": inst.budget,
        "dist": dist,
        "flags": inst.flags,
    }


def from_dict(d: dict) -> Instance:
    """Build an instance from the dict produced by `to_dict`."""
    dist = np.array(
        [[np.inf if v is None else v for v in row] for row in d["dist"]], dtype=float
    )
    return Instance(
        seed=d["seed"],
        topology=d["topology"],
        targets=np.array(d["targets"], dtype=float).reshape(-1, 2),
        weights=np.array(d["weights"], dtype=int),
        depots=np.array(d["depots"], dtype=float).reshape(-1, 2),
        nfz=d["nfz"],
        budget=d["budget"],
        dist=dist,
        flags=d["flags"],
        generator_version=d["generator_version"],
    )


def save_instance(inst: Instance, path: str | Path) -> None:
    """Write an instance to a JSON file (parent folders are created)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_dict(inst), sort_keys=True), encoding="utf-8")


def load_instance(path: str | Path) -> Instance:
    """Read an instance from a JSON file."""
    return from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
