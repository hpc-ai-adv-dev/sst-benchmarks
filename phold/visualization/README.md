# PHOLD Visualization

Dedicated place for visualizing the PHOLD benchmark topology with the
`ahp_graph` NetworkX / DOT backends, separate from the rest of the benchmark
output.

## Contents

- `visualize_phold.py` — standalone example that builds a small PHOLD grid,
  partitions its rows across ranks, and renders it (a whole-topology global
  view or one image per rank) while exercising the NetworkX visualization
  options.
- `visualize_phold_demo.ipynb` — a notebook with one demo cell per feature
  (global/per-rank views, saving/reloading graphs, DOT rendering, DOT →
  NetworkX conversion, the hierarchy view, and AHP's simple HPC example).
- `output/` — generated images and saved graph objects from the examples.

## Environment

Every command below needs the SST environment sourced so `graphviz` is on
`LD_LIBRARY_PATH` and `python3` resolves:

```bash
source /lus/bnchlu1/alvarado/sst_workspace/setSSTEnvironment.sh source
```

Use `python3` (there is no `python` on this system). For **standalone `srun`
runs**, the login-shell environment is *not* carried onto the compute node, so
you must source the environment **inside** the `srun` step, otherwise every
task dies with `execve(): python: No such file or directory`:

```bash
srun -N 1 --ntasks-per-node=4 bash -c \
    'source /lus/bnchlu1/alvarado/sst_workspace/setSSTEnvironment.sh source; \
     python3 visualize_phold.py --height 16 --width 16 --num-ranks 4'
```

## Usage

Render the global partition (per-rank node colors, inter-rank links
highlighted, self-links drawn):

```bash
python3 visualize_phold.py --height 8 --width 8 --num-ranks 4
```

Also save the underlying NetworkX graph object:

```bash
python3 visualize_phold.py --save-graph phold_grid.pickle   # or .graphml / .gexf
```

Remove self-links from the rendering:

```bash
python3 visualize_phold.py --no-self-links
```

Render with the graphviz DOT backend, or convert existing DOT files:

```bash
python3 visualize_phold.py --draw-backend dot
python3 visualize_phold.py --dot-to-networkx output --combine
```

### Per-rank (parallel) rendering

Mirroring the per-rank JSON generation (where each MPI rank writes its own JSON
file), the example can render **one image per rank**. Each task builds every
partition, flattens/prunes to its own rank's slice, and writes its own
`phold_global_partition<rank>` image. Launch it under `srun` so each task gets
its rank from `$SLURM_PROCID`. Source the environment **inside** the `srun`
step so every task can find `python3` and graphviz (see
[Environment](#environment)):

```bash
srun -N 1 --ntasks-per-node=4 bash -c \
    'source /lus/bnchlu1/alvarado/sst_workspace/setSSTEnvironment.sh source; \
     python3 visualize_phold.py --height 16 --width 16 --num-ranks 4'
# writes phold_global_partition0.png ... phold_global_partition3.png
```

`--per-rank` forces the same behavior without srun (rank taken from `--rank`),
and it also works with `--draw-backend dot`. This is the DOT/GraphViz/NetworkX
analog of each rank writing its own JSON slice.

## Visualization options

These map to the `DeviceGraph.write_networkx` parameters:

| Flag | Parameter | Effect |
| --- | --- | --- |
| `--save-graph PATH` | `save_graph` | Save the NetworkX graph to a file (pickle/GraphML/GEXF by extension). A bare filename lands in `output/`. |
| `--no-color-by-partition` | `color_by_partition` | Color nodes by their partition (rank). On by default here. |
| `--no-highlight-inter-rank` | `highlight_inter_rank` | Highlight links crossing a rank boundary in red. On by default here. |
| `--no-self-links` | `self_links` | Self-links are drawn by default; this removes them. |

The following mirror `phold_dist_ahp.py` drawing options:

| Flag | Effect |
| --- | --- |
| `--draw` | Also display the figure interactively. |
| `--draw-backend {networkx,dot}` | Choose the rendering backend (default `networkx`). |
| `--dot-to-networkx PATH` | Read existing DOT files and render them as NetworkX images, then exit. |
| `--combine` | With `--dot-to-networkx`, merge all DOT files into one image. |
| `--architecture {global,spmd}` | `global` builds every partition (best for a colored whole-topology image). |

## Grid layout via callbacks (generalized API)

The `ahp_graph` NetworkX backend used to detect PHOLD `comp_row_col` node names
with a hard-coded regex and lay them out on a grid. That PHOLD-specific logic
has been **removed from the library** so `ahp_graph` stays domain-agnostic.
Instead, `write_networkx`, `render_networkx_graph`, and `dot_to_networkx` accept
two optional callbacks:

| Parameter | Signature | Effect |
| --- | --- | --- |
| `layout` | `layout(graph) -> {node: (x, y)}` | Custom node placement. Return `None` to fall back to the automatic graphviz/spring layout. Nodes may alternatively carry a `pos` attribute. |
| `node_label` | `node_label(node) -> str` | Compact display label used when `full_labels=False`. Return `None` to fall back to the full node name. |

`visualize_phold.py` defines `grid_layout` / `grid_label` and passes them so the
PHOLD grid renders exactly as before. Graphs that are **not** grids (such as the
HPC example) simply omit these callbacks and get the automatic layout. The
graph-building code (`Node`, `SubGrid`, `architecture_*`) is copied from
`phold_dist_ahp.py` so the visualized topology matches the benchmark exactly.

If `AHP_PATH` is not set, the script falls back to the sibling
`ahp_graph/src` checkout in this workspace.

## Notebook demos

`visualize_phold_demo.ipynb` documents each feature as its own cell:

1. Global partition, colored by rank
2. Per-rank views
3. No coloring / no inter-rank highlight
4. Save the graph as a pickle
5. Save the graph as GraphML
6. Reload the saved graphs and render from them
7. Render with the DOT (graphviz) backend
8. DOT files → NetworkX images (combined)
9. DOT files → NetworkX images (per-rank, separate)
10. Hierarchy view showing only the links between SubGrids
11. **AHP's simple HPC example** — a non-grid graph (`ahp_graph/examples/HPC`)
    rendered with the same API and *no* grid callbacks

The notebook's "Grid layout & label callbacks" section defines the
`grid_layout` / `grid_label` helpers described above and passes them to the
PHOLD demos.

> The kernel must be started from a shell that has sourced the SST environment
> so graphviz is on `LD_LIBRARY_PATH`:
>
> ```bash
> source setSSTEnvironment.sh source
> ```
>
> then launch Jupyter / VS Code and select that interpreter as the kernel.
