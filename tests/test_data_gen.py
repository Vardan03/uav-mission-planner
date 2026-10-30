"""Tests for the NFZ-aware distances and the instance generator."""
from pathlib import Path

import numpy as np
import yaml

from src.data_gen import geometry
from src.data_gen.generate import generate_instance
from src.data_gen.instance import load_instance, save_instance, to_dict
from src.data_gen.validate import validate_instance

CFG = yaml.safe_load((Path(__file__).parents[1] / "configs" / "data.yaml").read_text())


def test_no_nfz_distance_is_euclidean():
    pts = np.random.default_rng(0).uniform(0, 10, size=(15, 2))
    expected = np.linalg.norm(pts[:, None] - pts[None, :], axis=2)
    assert np.abs(geometry.distance_matrix(pts, []) - expected).max() < 1e-9


def test_square_nfz_detour_matches_hand_computation():
    square = [(4, 4), (6, 4), (6, 6), (4, 6)]
    pts = np.array([[0.0, 5.0], [10.0, 5.0]])
    graph = geometry.NFZGraph(pts, [square])
    detour = 2 * np.sqrt(4**2 + 1**2) + 2.0  # via corners (4,4) and (6,4)
    assert graph.dist[0, 1] > 10.0 + 1e-3
    assert abs(graph.dist[0, 1] - detour) < 1e-5
    path = graph.path(0, 1)
    assert len(path) == 4 and np.allclose(path[0], pts[0]) and np.allclose(path[-1], pts[1])


def test_generator_is_deterministic(tmp_path):
    a = generate_instance(1001, 20, 2, CFG)
    b = generate_instance(1001, 20, 2, CFG)
    save_instance(a, tmp_path / "a.json")
    save_instance(b, tmp_path / "b.json")
    assert (tmp_path / "a.json").read_text() == (tmp_path / "b.json").read_text()
    assert to_dict(load_instance(tmp_path / "a.json")) == to_dict(a)


def test_generated_instances_are_valid():
    for seed in range(9000, 9012):  # covers all three topologies several times
        inst = generate_instance(seed, 20, 2, CFG)
        assert validate_instance(inst, CFG) == []
        assert inst.topology == ["uniform", "clustered", "corridor"][seed % 3]
