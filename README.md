# Weighted Vertex Cover — 2-Approximation via LP Rounding

Python implementation of the classic **2-approximation algorithm** for the
**Weighted Vertex Cover (WVC)** problem, based on LP relaxation and threshold
rounding.

---

## Background

Given an undirected graph G = (V, E) with non-negative vertex weights, a
**vertex cover** is a set S ⊆ V such that every edge has at least one endpoint
in S. WVC asks for the minimum-weight such set. WVC is NP-hard, so we compute
an approximate solution instead.

### The Algorithm (LP-Round-VC)

| Step | Action |
|------|--------|
| 1 | Formulate the LP relaxation: minimise Σ w(v)·x_v subject to x_u + x_v ≥ 1 for each edge and x_v ∈ [0,1]. |
| 2 | Solve the LP to get the fractional optimal solution x*. |
| 3 | Round up: include vertex v iff x*_v ≥ 0.5. |

**Guarantee:** the returned cover C satisfies w(C) ≤ 2 · OPT and is computed
in polynomial time.

---

## Repository Structure

```
.
├── weighted_vertex_cover.py   # Core algorithm + interactive input
├── setup.sh                   # Dependency installer
└── README.md                  # This file
```

---

## Requirements

- Python 3.8+
- [PuLP](https://coin-or.github.io/pulp/) — LP modelling library
  (wraps the open-source CBC solver; no external solver needed)

Install with:

```bash
bash setup.sh
```

or manually:

```bash
pip install pulp
```

---

## Usage

### Interactive mode

Run the script with no arguments and enter the graph step by step when prompted:

```bash
python weighted_vertex_cover.py
```

```
====================================================
  Weighted Vertex Cover -- LP Rounding (2-Approx)
====================================================

  Enter the graph below.
  Line 1 : <n> <m>               (vertices  edges)
  Line 2 : <w_0> ... <w_{n-1}>   (vertex weights)
  Lines 3 to m+2 : <u> <v>       (one edge per line, 0-indexed)

  n m > 4 4
  weights (4 values) > 1.0 2.0 1.5 3.0
  Enter 4 edge(s):
  edge 1/4 > 0 1
  edge 2/4 > 1 2
  edge 3/4 > 2 3
  edge 4/4 > 0 3

====================================================
  Vertices      : 4
  Edges         : 4
  Cover weight  : 5.5000
  Valid cover?  : YES
  Cover         : [0, 1, 2]
====================================================
```

### Optional flags

```bash
# Show the fractional LP solution values for each vertex
python weighted_vertex_cover.py --verbose

# Change the rounding threshold (default: 0.5)
python weighted_vertex_cover.py --threshold 0.6
```

### Use as a library

```python
from weighted_vertex_cover import Graph, lp_round_vertex_cover, cover_weight

G = Graph(num_vertices=6)
G.add_weights({0: 1.0, 1: 2.0, 2: 1.0, 3: 3.0, 4: 1.0, 5: 2.0})
G.add_edges([(0,1),(1,2),(2,3),(3,4),(4,5),(0,5),(1,4)])

cover = lp_round_vertex_cover(G)
print(f"Cover  : {cover}")
print(f"Weight : {cover_weight(G, cover):.2f}")
```

---

## Input Format

```
n m
w_0 w_1 ... w_{n-1}
u_1 v_1
u_2 v_2
...
u_m v_m
```

- `n` — number of vertices, labelled `0` to `n-1`
- `m` — number of edges
- All weights must be non-negative
- Edges are undirected; self-loops are not allowed

---

## Example Graphs

These can be entered directly in interactive mode to explore different
behaviours of the algorithm.

### 1 — 10×10 Grid (100 vertices, 180 edges)

Vertex at row i, column j has label `i*10 + j` and weight `1 + (i+j)%2`
(checkerboard pattern of 1s and 2s). The LP consistently picks the lighter
colour class.

```
100 180
<weights: 1 2 1 2 ... for all 100 vertices in row-major order>
0 1
0 10
1 2
1 11
... (all horizontal and vertical adjacencies)
```

### 2 — Circulant C(50; 1, 2, 5) (50 vertices, 150 edges)

50 vertices on a cycle with additional chords at distance 2 and 5.
Every edge `(v, (v+d) % 50)` for d ∈ {1, 2, 5}. Unit weights throughout.

```
50 150
1 1 1 ... (50 ones)
0 1
0 2
0 5
1 2
1 3
1 6
... (all circulant edges)
```

### 3 — Complete bipartite K₁₅,₁₅ (30 vertices, 225 edges)

Left vertices 0–14 have weight 1; right vertices 15–29 have weight 3.
Every left vertex connects to every right vertex. The LP selects only
the cheaper left side as the cover.

```
30 225
1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3
0 15
0 16
...
14 29
```

### 4 — Deterministic sparse graph (200 vertices, ~1200 edges)

Vertex v has weight `1 + (v % 5)`. Edge (u, v) with u < v exists iff
`(u*31 + v*17) % 200 < 12`. Produces an irregular graph with varied
weight distribution, useful for stress-testing the solver.

```
200 <m>
1 2 3 4 5 1 2 3 4 5 ... (repeating pattern for 200 vertices)
<edges determined by the rule above>
```

---

## Theoretical Notes

- The ratio of **2** is tight: on a single edge with equal weights, the LP
  assigns x* = 0.5 to both endpoints, both are rounded in, giving ratio 2.
- Assuming the **Unique Games Conjecture**, no polynomial-time algorithm can
  approximate WVC within 2 − ε for any ε > 0.
- The LP is **half-integral**: optimal solutions always satisfy
  x*_v ∈ {0, 0.5, 1}, so the threshold of 0.5 is canonical.

---

## License

MIT
