"""NFZ-aware shortest-path distances via a visibility graph."""
from __future__ import annotations

import numpy as np
import shapely
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from shapely.geometry import Polygon
from shapely.ops import unary_union

PUSH = 1e-6  # km, polygon vertices are moved outward by this much


def _push_outward(vertices: np.ndarray, eps: float) -> np.ndarray:
    """Move each vertex of a polygon eps outward along its corner bisector."""
    poly = Polygon(vertices)
    if not poly.exterior.is_ccw:
        vertices = vertices[::-1]
    prev_v = np.roll(vertices, 1, axis=0)
    next_v = np.roll(vertices, -1, axis=0)
    e_in = vertices - prev_v
    e_out = next_v - vertices
    # For a counter-clockwise polygon the outward normal of edge (dx, dy) is (dy, -dx).
    n_in = np.stack([e_in[:, 1], -e_in[:, 0]], axis=1)
    n_out = np.stack([e_out[:, 1], -e_out[:, 0]], axis=1)
    n_in /= np.linalg.norm(n_in, axis=1, keepdims=True)
    n_out /= np.linalg.norm(n_out, axis=1, keepdims=True)
    bisector = n_in + n_out
    length = np.linalg.norm(bisector, axis=1, keepdims=True)
    bisector = np.where(length > 1e-12, bisector / np.maximum(length, 1e-12), n_in)
    return vertices + eps * bisector


class NFZGraph:
    """Visibility graph over points and NFZ vertices with all-pairs shortest paths.

    Args:
        points: (P, 2) array of depots and targets (the nodes we need distances for).
        nfz: list of polygons, each a list of (x, y) vertices.

    Attributes:
        dist: (P, P) shortest-path distances, np.inf where no path exists.
    """

    def __init__(self, points: np.ndarray, nfz: list):
        self.points = np.asarray(points, dtype=float).reshape(-1, 2)
        n_points = len(self.points)
        corner_blocks = [_push_outward(np.asarray(p, dtype=float), PUSH) for p in nfz]
        corners = np.vstack(corner_blocks) if corner_blocks else np.empty((0, 2))
        self.nodes = np.vstack([self.points, corners])

        n_nodes = len(self.nodes)
        rows, cols = np.triu_indices(n_nodes, k=1)
        segments = np.stack([self.nodes[rows], self.nodes[cols]], axis=1)
        if nfz:
            union = unary_union([Polygon(p) for p in nfz])
            shapely.prepare(union)
            blocked = shapely.intersects(union, shapely.linestrings(segments))
        else:
            blocked = np.zeros(len(rows), dtype=bool)
        keep = ~blocked
        lengths = np.linalg.norm(segments[keep, 1] - segments[keep, 0], axis=1)
        graph = csr_matrix((lengths, (rows[keep], cols[keep])), shape=(n_nodes, n_nodes))
        full, self._pred = shortest_path(
            graph, method="D", directed=False, return_predecessors=True
        )
        self.dist = full[:n_points, :n_points]

    def path(self, i: int, j: int) -> np.ndarray:
        """Return the (M, 2) polyline of the shortest path from point i to point j.

        The result is empty if j cannot be reached from i.
        """
        if not np.isfinite(self.dist[i, j]):
            return np.empty((0, 2))
        order = [j]
        while order[-1] != i:
            order.append(int(self._pred[i, order[-1]]))
        return self.nodes[order[::-1]]


def distance_matrix(points: np.ndarray, nfz: list) -> np.ndarray:
    """Return the NFZ-aware shortest-path distance matrix between points."""
    return NFZGraph(points, nfz).dist
