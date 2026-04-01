"""
weighted_vertex_cover.py
========================
2-Approximation for the Weighted Vertex Cover (WVC) problem
via LP relaxation and threshold rounding.

Algorithm (LP-Round-VC)
-----------------------
  1. Formulate the LP relaxation of the WVC integer program.
  2. Solve the LP to get fractional optimal x* in [0, 1]^V.
  3. Round up: C = { v in V | x*_v >= 0.5 }.

Guarantee: C is a valid vertex cover with w(C) <= 2 * OPT.

Dependencies: PuLP  (pip install pulp)

Usage
-----
  # Interactive mode
  python weighted_vertex_cover.py

  # Use as a library
  >>> from weighted_vertex_cover import Graph, lp_round_vertex_cover
  >>> G = Graph(num_vertices=4)
  >>> G.add_weights({0: 1.0, 1: 2.0, 2: 1.5, 3: 3.0})
  >>> G.add_edges([(0, 1), (1, 2), (2, 3)])
  >>> cover = lp_round_vertex_cover(G)
  >>> print(cover)

Interactive Input Format
------------------------
  n m                        -- number of vertices and edges
  w_0 w_1 ... w_{n-1}       -- space-separated vertex weights
  u v  (repeated m times)   -- one edge per line (0-indexed)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import pulp


# -- Data model ----------------------------------------------------------------

@dataclass
class Graph:
    """Undirected weighted graph (0-indexed vertices)."""
    num_vertices: int
    weights: Dict[int, float] = field(default_factory=dict)
    edges: List[Tuple[int, int]] = field(default_factory=list)

    def add_weights(self, w: Dict[int, float]) -> None:
        """Set vertex weights from a dict {vertex_id: weight}."""
        self.weights.update(w)

    def add_edges(self, edges: List[Tuple[int, int]]) -> None:
        """Add a list of (u, v) edges."""
        for u, v in edges:
            if u == v:
                raise ValueError(f"Self-loop on vertex {u} is not allowed.")
            if not (0 <= u < self.num_vertices and 0 <= v < self.num_vertices):
                raise ValueError(
                    f"Edge ({u},{v}) references a vertex outside "
                    f"[0, {self.num_vertices - 1}]."
                )
            self.edges.append((u, v))

    def validate(self) -> None:
        """Raise ValueError if the graph is not properly initialised."""
        missing = [v for v in range(self.num_vertices) if v not in self.weights]
        if missing:
            raise ValueError(f"Missing weights for vertices: {missing}")


# -- Core algorithm ------------------------------------------------------------

def lp_round_vertex_cover(
    graph: Graph,
    threshold: float = 0.5,
    verbose: bool = False,
) -> List[int]:
    """
    Compute a 2-approximate Weighted Vertex Cover via LP rounding.

    Parameters
    ----------
    graph     : Graph instance with weights and edges initialised.
    threshold : Rounding threshold -- vertices with x* >= threshold are
                included in the cover.  Default 0.5 gives 2-approximation.
    verbose   : If True, print the fractional LP solution values.

    Returns
    -------
    cover : Sorted list of vertex indices forming the approximate cover.

    Raises
    ------
    RuntimeError : If the LP solver does not find an optimal solution.
    """
    graph.validate()
    n = graph.num_vertices

    # Formulate LP
    prob = pulp.LpProblem("WeightedVertexCover_LP", pulp.LpMinimize)

    # Decision variables: x[v] in [0, 1]
    x = [
        pulp.LpVariable(f"x_{v}", lowBound=0.0, upBound=1.0, cat="Continuous")
        for v in range(n)
    ]

    # Objective: minimise  sum_v  w(v) * x[v]
    prob += pulp.lpSum(graph.weights[v] * x[v] for v in range(n)), "TotalWeight"

    # Covering constraints: x[u] + x[v] >= 1  for every edge (u, v)
    for idx, (u, v) in enumerate(graph.edges):
        prob += x[u] + x[v] >= 1, f"Cover_{idx}_{u}_{v}"

    # Solve
    solver = pulp.PULP_CBC_CMD(msg=1 if verbose else 0)
    status = prob.solve(solver)

    if pulp.LpStatus[status] != "Optimal":
        raise RuntimeError(
            f"LP solver did not reach optimality. "
            f"Status: {pulp.LpStatus[status]}"
        )

    x_vals = [pulp.value(x[v]) for v in range(n)]

    if verbose:
        print("\nFractional LP solution:")
        for v in range(n):
            print(f"  x[{v}] = {x_vals[v]:.4f}  (weight = {graph.weights[v]})")

    # Round: include v if x*[v] >= threshold
    return sorted(
        v for v in range(n)
        if x_vals[v] is not None and x_vals[v] >= threshold
    )


# -- Verification helpers ------------------------------------------------------

def is_vertex_cover(graph: Graph, cover: List[int]) -> bool:
    """Return True iff `cover` is a valid vertex cover of `graph`."""
    cover_set = set(cover)
    return all(u in cover_set or v in cover_set for u, v in graph.edges)


def cover_weight(graph: Graph, cover: List[int]) -> float:
    """Return the total weight of `cover`."""
    return sum(graph.weights[v] for v in cover)


# -- Result display ------------------------------------------------------------

def print_result(graph: Graph, cover: List[int]) -> None:
    """Pretty-print a vertex cover result."""
    w     = cover_weight(graph, cover)
    valid = is_vertex_cover(graph, cover)
    sep   = "=" * 52

    print(sep)
    print(f"  Vertices      : {graph.num_vertices}")
    print(f"  Edges         : {len(graph.edges)}")
    print(f"  Cover weight  : {w:.4f}")
    print(f"  Valid cover?  : {'YES' if valid else 'NO  <-- BUG'}")
    if len(cover) <= 30:
        print(f"  Cover         : {cover}")
    else:
        print(f"  Cover         : {cover[:15]} ... {cover[-5:]}  ({len(cover)} vertices)")
    print(sep)


# -- Interactive input ---------------------------------------------------------

def read_graph_interactively() -> Graph:
    """Prompt the user to enter a graph at the terminal."""
    print()
    print("  Enter the graph below.")
    print("  Line 1 : <n> <m>               (vertices  edges)")
    print("  Line 2 : <w_0> ... <w_{n-1}>   (vertex weights)")
    print("  Lines 3 to m+2 : <u> <v>       (one edge per line, 0-indexed)")
    print()

    # n and m
    while True:
        try:
            n, m = map(int, input("  n m > ").split())
            if n < 1:
                print("  x  Number of vertices must be at least 1.")
            elif m < 0:
                print("  x  Number of edges cannot be negative.")
            else:
                break
        except ValueError:
            print("  x  Enter exactly two integers (e.g. 5 6).")

    # Weights
    while True:
        try:
            weights_raw = list(map(float, input(f"  weights ({n} values) > ").split()))
            if len(weights_raw) != n:
                print(f"  x  Expected {n} weights, got {len(weights_raw)}.")
            elif any(w < 0 for w in weights_raw):
                print("  x  Weights must be non-negative.")
            else:
                break
        except ValueError:
            print("  x  Enter space-separated numbers.")

    graph = Graph(num_vertices=n)
    graph.add_weights({v: weights_raw[v] for v in range(n)})

    # Edges
    edges: List[Tuple[int, int]] = []
    print(f"  Enter {m} edge(s):")
    while len(edges) < m:
        try:
            u, v = map(int, input(f"  edge {len(edges)+1}/{m} > ").split())
            if u == v:
                print("  x  Self-loops are not allowed.")
            elif not (0 <= u < n and 0 <= v < n):
                print(f"  x  Vertices must be in [0, {n-1}].")
            else:
                edges.append((u, v))
        except ValueError:
            print("  x  Enter exactly two integers (u v).")

    graph.add_edges(edges)
    return graph


# -- Entry point ---------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="2-Approximation for Weighted Vertex Cover via LP Rounding.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float, default=0.5, metavar="T",
        help="LP rounding threshold (default: 0.5).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print fractional LP solution values.",
    )
    args = parser.parse_args(argv)

    print("=" * 52)
    print("  Weighted Vertex Cover -- LP Rounding (2-Approx)")
    print("=" * 52)

    graph = read_graph_interactively()
    cover = lp_round_vertex_cover(graph, threshold=args.threshold, verbose=args.verbose)

    print()
    print_result(graph, cover)


if __name__ == "__main__":
    main()
