"""Instance generator (CLI): `python -m src.data_gen.generate --all`."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import yaml
from shapely.geometry import MultiPoint, Polygon

from src.data_gen import geometry, validate
from src.data_gen.instance import Instance, save_instance
from src.data_gen.validate import RepairFailed

log = logging.getLogger("uav.generate")
TOPOLOGIES = ["uniform", "clustered", "corridor"]


def _random_hull(rng, cfg: dict) -> Polygon:
    """One convex NFZ polygon: hull of 5-8 random points around a centre."""
    size = cfg["map_size"]
    r_lo, r_hi = cfg["nfz"]["radius"]
    v_lo, v_hi = cfg["nfz"]["vertices"]
    radius = rng.uniform(r_lo, r_hi)
    centre = rng.uniform(radius, size - radius, size=2)  # polygon stays inside the map
    m = int(rng.integers(v_lo, v_hi + 1))
    angles = rng.uniform(0, 2 * np.pi, size=m)
    radii = rng.uniform(0.6 * radius, radius, size=m)
    pts = centre + radii[:, None] * np.stack([np.cos(angles), np.sin(angles)], axis=1)
    return MultiPoint(pts).convex_hull


def sample_nfz(rng, cfg: dict, seed: int) -> list:
    """Draw 0-3 convex NFZs, merge overlaps, keep total area in the allowed share.

    Instances with zero NFZs are exempt from the area rule.
    """
    count = int(rng.integers(0, cfg["nfz"]["max_count"] + 1))
    if count == 0:
        return []
    lo, hi = cfg["nfz"]["area_fraction"]
    for _ in range(200):
        hulls = [_random_hull(rng, cfg) for _ in range(count)]
        if any(h.geom_type != "Polygon" for h in hulls):
            continue
        merged = validate.merge_nfz(hulls, seed)
        area = validate.nfz_union(merged).area / cfg["map_size"] ** 2
        if lo <= area <= hi:
            return merged
    raise RepairFailed("could not draw NFZs with the required area share")


def sample_depot(rng, cfg: dict) -> np.ndarray:
    """One point within `depot_edge_dist` km of a random map edge."""
    size, d = cfg["map_size"], rng.uniform(0, cfg["depot_edge_dist"])
    t = rng.uniform(0, size)
    side = int(rng.integers(4))
    return np.array([[t, d], [t, size - d], [d, t], [size - d, t]][side])


def sample_depots(rng, k: int, cfg: dict, union, seed: int) -> np.ndarray:
    """K depots near the edges, far from each other and from the NFZs."""
    depots: list = []
    for _ in range(k):
        for _ in range(cfg["validation"]["max_repairs"]):
            p = sample_depot(rng, cfg)
            apart = all(np.linalg.norm(p - q) >= cfg["depot_min_sep"] for q in depots)
            if apart and validate.is_clear(p, union, cfg["validation"]["depot_nfz_clearance"]):
                depots.append(p)
                break
            log.info("seed=%d repair: depot resampled", seed)
        else:
            raise RepairFailed("could not place a depot")
    return np.array(depots)


def make_target_sampler(rng, topology: str, cfg: dict):
    """Return a function that draws one raw target position for the topology."""
    size = cfg["map_size"]
    if topology == "uniform":
        m = cfg["margin"]
        return lambda: rng.uniform(m, size - m, size=2)
    if topology == "clustered":
        c_lo, c_hi = cfg["clustered"]["centres"]
        centres = rng.uniform(0, size, size=(int(rng.integers(c_lo, c_hi + 1)), 2))
        s_lo, s_hi = cfg["clustered"]["sigma"]
        sigmas = rng.uniform(s_lo, s_hi, size=len(centres))

        def draw_clustered():
            c = int(rng.integers(len(centres)))
            return np.clip(rng.normal(centres[c], sigmas[c]), 0, size)

        return draw_clustered
    p_lo, p_hi = cfg["corridor"]["polylines"]
    v_lo, v_hi = cfg["corridor"]["vertices"]
    lines = [
        rng.uniform(0, size, size=(int(rng.integers(v_lo, v_hi + 1)), 2))
        for _ in range(int(rng.integers(p_lo, p_hi + 1)))
    ]

    def draw_corridor():
        line = lines[int(rng.integers(len(lines)))]
        seg_len = np.linalg.norm(np.diff(line, axis=0), axis=1)
        ends = np.cumsum(seg_len)
        s = rng.uniform(0, ends[-1])  # position along the polyline
        idx = min(int(np.searchsorted(ends, s)), len(seg_len) - 1)
        offset = s - (ends[idx] - seg_len[idx])
        direction = (line[idx + 1] - line[idx]) / seg_len[idx]
        normal = np.array([-direction[1], direction[0]])
        noise = rng.normal(0, cfg["corridor"]["sigma"])
        return np.clip(line[idx] + offset * direction + noise * normal, 0, size)

    return draw_corridor


def draw_valid_target(sampler, others: np.ndarray, union, cfg: dict, seed: int) -> np.ndarray:
    """Sample until the target is clear of NFZs and not on top of another target."""
    v = cfg["validation"]
    for _ in range(v["max_repairs"]):
        p = sampler()
        far_enough = len(others) == 0 or (
            np.linalg.norm(others - p, axis=1).min() >= v["min_target_sep"]
        )
        if far_enough and validate.is_clear(p, union, v["target_nfz_clearance"]):
            return p
        log.info("seed=%d repair: target resampled", seed)
    raise RepairFailed("could not place a target")


def _generate_once(seed: int, attempt: int, n: int, k: int, cfg: dict) -> Instance:
    """One generation attempt; raises RepairFailed if a repair runs out of tries."""
    rng = np.random.default_rng([seed, attempt])
    topology = TOPOLOGIES[seed % 3]
    nfz = sample_nfz(rng, cfg, seed)
    union = validate.nfz_union(nfz)
    depots = sample_depots(rng, k, cfg, union, seed)
    sampler = make_target_sampler(rng, topology, cfg)

    targets = np.empty((0, 2))
    for _ in range(n):
        p = draw_valid_target(sampler, targets, union, cfg, seed)
        targets = np.vstack([targets, p])
    w_lo, w_hi = cfg["weights"]
    weights = rng.integers(w_lo, w_hi + 1, size=n)
    validate.check_hard_errors(targets, weights, depots, cfg["map_size"], cfg["weights"])

    # Check 7: targets that no depot can reach at all are resampled.
    for _ in range(cfg["validation"]["max_repairs"]):
        dist = geometry.distance_matrix(np.vstack([depots, targets]), nfz)
        cut_off = np.where(~np.isfinite(dist[:k, k:]).any(axis=0))[0]
        if len(cut_off) == 0:
            break
        for i in cut_off:
            others = np.delete(targets, i, axis=0)
            targets[i] = draw_valid_target(sampler, others, union, cfg, seed)
    else:
        raise RepairFailed("targets stay cut off from all depots")

    flags = {"unreachable_targets": validate.unreachable_targets(dist, k, cfg["budget"])}
    return Instance(
        seed=seed, topology=topology, targets=targets, weights=weights, depots=depots,
        nfz=nfz, budget=cfg["budget"], dist=dist, flags=flags,
        generator_version=cfg["generator_version"],
    )


def generate_instance(seed: int, n: int, k: int, cfg: dict, max_attempts: int = 20) -> Instance:
    """Generate the instance fully determined by (seed, n, k, cfg).

    If a repair fails, retry with the next attempt counter (same seed).
    """
    for attempt in range(max_attempts):
        try:
            return _generate_once(seed, attempt, n, k, cfg)
        except RepairFailed as err:
            log.info("seed=%d attempt %d failed (%s), regenerating", seed, attempt, err)
    raise RuntimeError(f"seed {seed}: generation failed after {max_attempts} attempts")


def main() -> None:
    """CLI entry point: write the chosen splits to data/instances/<split>/<seed>.json."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/data.yaml")
    parser.add_argument("--out", default="data/instances")
    parser.add_argument("--split", help="split name; default is --all")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text())
    names = list(cfg["splits"]) if args.all or not args.split else [args.split]
    Path("data").mkdir(exist_ok=True)
    logging.basicConfig(filename="data/generation.log", level=logging.INFO, filemode="w")
    for name in names:
        s = cfg["splits"][name]
        for seed in range(s["seed_start"], s["seed_start"] + s["count"]):
            inst = generate_instance(seed, s["n"], s["k"], cfg)
            problems = validate.validate_instance(inst, cfg)
            if problems:
                raise RuntimeError(f"{name}/{seed}: {problems}")
            save_instance(inst, Path(args.out) / name / f"{seed}.json")
        print(f"{name}: {s['count']} instances written")


if __name__ == "__main__":
    main()
