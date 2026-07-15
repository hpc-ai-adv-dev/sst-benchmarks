#!/usr/bin/env python3
"""
Dedicated visualization example for the PHOLD benchmark.

This script reuses the exact PHOLD graph-building code from
``phold_dist_ahp.py`` (the ``Node`` / ``SubGrid`` devices and the
``architecture`` builders) and renders the topology with the ahp_graph
NetworkX backend so you can exercise the visualization options:

  * saving the underlying NetworkX graph to a file (pickle / GraphML / GEXF)
  * coloring nodes by their partition (rank) for a global-partition image
  * highlighting links that cross a rank boundary (inter-rank links)
  * drawing self-links (default) with a toggle to remove them

It also supports the same drawing options as ``phold_dist_ahp.py``:
``--draw``, ``--draw-backend``, ``--dot-to-networkx`` and ``--combine``.

All output (images and saved graph objects) is written to the local
``output`` directory next to this file so the visualization artifacts stay
separate from the rest of the benchmark output.

Examples
--------
Render the global partition with per-rank colors and inter-rank highlighting::

    python3 visualize_phold.py --height 8 --width 8 --num-ranks 4

Also save the NetworkX graph object as a pickle::

    python3 visualize_phold.py --save-graph phold_grid.pickle

Remove self-links from the rendering::

    python3 visualize_phold.py --no-self-links

Render with the graphviz DOT backend instead of NetworkX::

    python3 visualize_phold.py --draw-backend dot

Read existing DOT files and render them as NetworkX images, then exit::

    python3 visualize_phold.py --dot-to-networkx output --combine
"""

import os
import sys
import argparse

# Allow importing a local ahp_graph checkout if it is not pip-installed.
# Prefer the AHP_PATH environment variable, then fall back to the sibling
# ahp_graph/src directory in this workspace.
sys.path.append(os.environ.get('AHP_PATH', '.'))
_repo_ahp_src = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..',
                 'ahp_graph', 'src')
)
if os.path.isdir(_repo_ahp_src):
    sys.path.append(_repo_ahp_src)

from ahp_graph.Device import Device, PortInfo
from ahp_graph.DeviceGraph import DeviceGraph


import re

# PHOLD-specific layout/label helpers.  These used to live inside ahp_graph's
# NetworkX backend, but that hard-coded the PHOLD 'comp_row_col' grid naming
# into the generic graph library.  They now live here in the PHOLD example and
# are passed to write_networkx / dot_to_networkx as callbacks, so the library
# stays domain-agnostic.
_GRID_RE = re.compile(r'comp_(\d+)_(\d+)')


def grid_label(node):
    """Return a compact 'row,col' label for a PHOLD grid node, else None.

    Returning None tells ahp_graph to fall back to the node's full label.
    """
    match = _GRID_RE.search(str(node))
    if match:
        return f"{match.group(1)},{match.group(2)}"
    return None


def grid_layout(graph):
    """Lay PHOLD 'comp_row_col' nodes out on a grid using (col, -row).

    Returns a dict of node -> (x, y) when every node encodes grid
    coordinates, otherwise None so ahp_graph falls back to its automatic
    (graphviz/spring) layout.
    """
    coords = dict()
    for node in graph.nodes():
        match = _GRID_RE.search(str(node))
        if not match:
            return None
        coords[node] = (int(match.group(2)), -int(match.group(1)))
    return coords


parser = argparse.ArgumentParser(
    description='Visualize the PHOLD benchmark topology with ahp_graph.'
)
# --- PHOLD grid options (mirrors phold_dist_ahp.py) ---
parser.add_argument(
    '--height', type=int, dest='height', default=8,
    help='Height of grid (number of rows)'
)
parser.add_argument(
    '--width', type=int, dest='width', default=8,
    help='Width of grid (number of columns)'
)
parser.add_argument(
    '--linkDelay', '--link-delay', type=str, default='1ns',
    help='Delay for each link'
)
parser.add_argument(
    '--numRings', '--num-rings', '--ring-size', type=int, default=1,
    help='Number of rings of neighbors to connect to each component'
)
parser.add_argument(
    '--nodeType', '--node-type', type=str, default='phold.Node',
    help='Type of node to create (default: phold.Node)'
)
parser.add_argument(
    '--no-self-links', action='store_true', default=False,
    help='Disable self-links; by default self-links are enabled.'
)
parser.add_argument(
    '--verbose', type=int, default=0,
    help='Verbosity level for link wiring messages.'
)
parser.add_argument(
    '--print-links', action='store_true', default=False,
    help='Print detailed link wiring information.'
)
parser.add_argument(
    '--num-ranks', '--numRanks', type=int, default=4,
    help='Number of ranks/boards to partition rows across (default: 4)'
)
parser.add_argument(
    '--rank', type=int, default=0,
    help='Which rank to view when using the spmd architecture.'
)
parser.add_argument(
    '--per-rank', action='store_true', default=False,
    help='Render one image per rank (each rank writes its own '
         '"phold_global_partition<rank>" slice), mirroring per-rank JSON '
         'generation. Automatically enabled when launched under srun (i.e. '
         'when $SLURM_PROCID is set); the rank then comes from $SLURM_PROCID.'
)
parser.add_argument(
    '--architecture', type=str, default='global',
    help='Which architecture to use: global or spmd (default: global). '
         'global builds every partition and is best for a colored, '
         'whole-topology image.'
)
# --- drawing options (mirrors phold_dist_ahp.py) ---
parser.add_argument(
    '--draw', action='store_true', default=False,
    help='Display the figure interactively as well as writing it.'
)
parser.add_argument(
    '--draw-backend', type=str, default='networkx',
    help='Which backend to draw with: networkx or dot (default: networkx)'
)
parser.add_argument(
    '--dot-to-networkx', type=str, default=None,
    help='Directory (or .dot file) of DOT files to read and render as '
         'NetworkX images, then exit.'
)
parser.add_argument(
    '--combine', action='store_true', default=False,
    help='When using --dot-to-networkx, merge all DOT files into one image.'
)
# --- new NetworkX visualization options ---
parser.add_argument(
    '--output', type=str, default='output',
    help='Output directory (default: output)'
)
parser.add_argument(
    '--save-graph', type=str, default=None,
    help='Also save the NetworkX graph object to this file. Format is chosen '
         'by extension: .pickle/.pkl/.gpickle, .graphml, or .gexf'
)
parser.add_argument(
    '--no-color-by-partition', action='store_true', default=False,
    help='Disable coloring nodes by their partition (rank).'
)
parser.add_argument(
    '--no-highlight-inter-rank', action='store_true', default=False,
    help='Disable highlighting of inter-rank links.'
)
args = parser.parse_args()


# Resolve the output directory next to this file when a relative path is used.
if os.path.isabs(args.output):
    output_dir = args.output
else:
    output_dir = os.path.join(os.path.dirname(__file__), args.output)


# Handle the DOT -> NetworkX conversion path and exit, like phold_dist_ahp.py.
if args.dot_to_networkx is not None:
    DeviceGraph.dot_to_networkx(args.dot_to_networkx, output=output_dir,
                                combine=args.combine,
                                layout=grid_layout, node_label=grid_label)
    raise SystemExit(0)


def log_link(msg: str, level: int = 1) -> None:
    """Log link wiring if verbosity is sufficient or print-links is set."""
    if args.print_links or args.verbose >= level:
        print(msg)


NUM_RINGS = args.numRings
SIDE = NUM_RINGS * 2 + 1
MAX_SIZE = SIDE * SIDE


def port_num(src_i, src_j, dst_i, dst_j):
    """Return port index for link from (src_i,src_j) to (dst_i,dst_j)."""
    side_length = NUM_RINGS * 2 + 1
    di = src_i - dst_i
    dj = src_j - dst_j
    ip = NUM_RINGS - di
    jp = NUM_RINGS - dj
    return ip * side_length + jp


def offset_index(di: int, dj: int) -> int:
    """Map an offset (di, dj) to a unique index in [0, SIDE*SIDE)."""
    ip = NUM_RINGS - di
    jp = NUM_RINGS - dj
    return ip * SIDE + jp


def border_index(col_j: int, dj: int, src_row_offset: int,
                 tgt_row_offset: int) -> int:
    """Compute global multi-port index for a border based on column/offsets."""
    base = col_j * NUM_RINGS * NUM_RINGS * SIDE
    dj_idx = dj + NUM_RINGS  # Convert dj from [-R, R] to [0, 2R]
    return (base + src_row_offset * NUM_RINGS * SIDE
            + tgt_row_offset * SIDE + dj_idx)


def index_to_offset(idx: int):
    """Inverse of offset_index: recover (di, dj) from 0..MAX_SIZE-1."""
    ip = idx // SIDE
    jp = idx % SIDE
    di = NUM_RINGS - ip
    dj = NUM_RINGS - jp
    return di, dj


class Node(Device):
    """PHOLD node device: exposes ports to neighbors within R rings."""
    library = args.nodeType

    def __init__(self, name, i, j):
        """Create node at (i,j) and add ports for in-bounds neighbors."""
        super().__init__(name)
        self.type = None
        self.portinfo = PortInfo()

        # Iterate neighbor offsets within ring radius; include self (0,0).
        for di in range(-NUM_RINGS, NUM_RINGS + 1):
            for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                # Enforce ring boundary and allow self.
                if (1 <= max(abs(di), abs(dj)) <= NUM_RINGS or
                        (di == 0 and dj == 0)):
                    dst_i = i + di
                    dst_j = j + dj
                    # Add port if neighbor is within the global grid.
                    if 0 <= dst_i < args.height and 0 <= dst_j < args.width:
                        pnum = port_num(i, j, dst_i, dst_j)
                        self.portinfo.add(f"port{pnum}", "String",
                                          required=False)

        self.attr = {"i": i, "j": j, "numRings": NUM_RINGS}


class SubGrid(Device):
    """Row-partitioned assembly; wires internal links and border anchors."""

    portinfo = PortInfo()
    portinfo.add('northBorder', 'String',
                 limit=args.width * NUM_RINGS * NUM_RINGS * SIDE,
                 required=False)
    portinfo.add('southBorder', 'String',
                 limit=args.width * NUM_RINGS * NUM_RINGS * SIDE,
                 required=False)

    def __init__(self, name, row_start, row_end):
        """Initialize subgrid covering rows [row_start, row_end)."""
        super().__init__(name)
        self.row_start = row_start
        self.row_end = row_end
        self.nodes = {}

    def expand(self, graph: DeviceGraph) -> None:
        """Construct child nodes and wire internal and border links."""
        self.nodes = {}
        for i in range(self.row_start, self.row_end):
            self.nodes[i] = {}
            for j in range(args.width):
                n = Node(f"comp_{i}_{j}", i, j)
                # Ensure child nodes inherit the SubGrid's partition.
                if getattr(self, 'partition', None) is not None:
                    n.set_partition(self.partition[0], self.partition[1])
                self.nodes[i][j] = n

        M = args.width

        # Defer border wiring to sweeps to avoid multi-link collisions.
        for i in range(self.row_start, self.row_end):
            for j in range(M):
                for di in range(-NUM_RINGS, NUM_RINGS + 1):
                    for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                        if max(abs(di), abs(dj)) > NUM_RINGS:
                            continue

                        ni = i + di
                        nj = j + dj

                        if not (0 <= ni < args.height and 0 <= nj < M):
                            continue

                        src_idx = port_num(i, j, ni, nj)
                        tgt_idx = port_num(ni, nj, i, j)
                        src_port = f"port{src_idx}"
                        tgt_port = f"port{tgt_idx}"

                        # Internal neighbor within this subgrid
                        if self.row_start <= ni < self.row_end:
                            # Self-link handling: include unless disabled
                            if di == 0 and dj == 0:
                                if args.no_self_links:
                                    continue
                            else:
                                # Duplicate-avoid rule for non-self wiring
                                if not (di < 0 or (di == 0 and dj < 0)):
                                    continue

                            if args.verbose >= 2:
                                msg = (
                                    f"Internal link: {self.name}.comp_{i}_{j}."
                                    f"{src_port} <-> {self.name}."
                                    f"comp_{ni}_{nj}.{tgt_port} "
                                    f"(delay {args.linkDelay})"
                                )
                                log_link(msg, level=2)

                            src_node = self.nodes[i][j]
                            tgt_node = self.nodes[ni][nj]
                            graph.link(
                                getattr(src_node, src_port),
                                getattr(tgt_node, tgt_port),
                                args.linkDelay,
                            )
                        # Neighbor outside this subgrid: handled by sweeps.
                        elif 0 <= ni < args.height:
                            continue

        # Single-link border sweeps: one anchor per border index.
        tops = list(range(self.row_start,
                          min(self.row_start + NUM_RINGS, self.row_end)))
        bots = list(range(max(self.row_start, self.row_end - NUM_RINGS),
                          self.row_end))

        # North border sweep: connect to neighbors above this subgrid.
        for top in tops:
            i = top
            for j in range(args.width):
                for di in range(-NUM_RINGS, 0):  # Only negative di (going up)
                    for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                        if max(abs(di), abs(dj)) > NUM_RINGS:
                            continue
                        ni = i + di
                        nj = j + dj
                        if ni < self.row_start and 0 <= nj < args.width \
                                and 0 <= ni:
                            upper_row_end = self.row_start
                            src_row_offset = (upper_row_end - 1) - ni
                            tgt_row_offset = i - upper_row_end
                            bidx = border_index(nj, -dj, src_row_offset,
                                                tgt_row_offset)
                            nb = self.northBorder(bidx)
                            src_idx = port_num(i, j, ni, nj)
                            node = self.nodes[i][j]
                            if args.verbose >= 2:
                                msg = (
                                    f"Border link (north): {self.name}."
                                    f"comp_{i}_{j}.port{src_idx} -> "
                                    f"{self.name}.northBorder[{bidx}] "
                                    f"(delay {args.linkDelay})"
                                )
                                log_link(msg, level=2)
                            graph.link(getattr(node, f"port{src_idx}"), nb,
                                       args.linkDelay)

        # South border sweep: connect to neighbors below this subgrid.
        for bot in bots:
            i = bot
            for j in range(args.width):
                for di in range(1, NUM_RINGS + 1):  # Only positive di (down)
                    for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                        if max(di, abs(dj)) > NUM_RINGS:
                            continue
                        ni = i + di
                        nj = j + dj
                        if ni >= self.row_end and 0 <= nj < args.width \
                                and ni < args.height:
                            src_row_offset = (self.row_end - 1) - i
                            tgt_row_offset = ni - self.row_end
                            bidx = border_index(j, dj, src_row_offset,
                                                tgt_row_offset)
                            sb = self.southBorder(bidx)
                            src_idx = port_num(i, j, ni, nj)
                            node = self.nodes[i][j]
                            if args.verbose >= 2:
                                msg = (
                                    f"Border link (south): {self.name}."
                                    f"comp_{i}_{j}.port{src_idx} -> "
                                    f"{self.name}.southBorder[{bidx}] "
                                    f"(delay {args.linkDelay})"
                                )
                                log_link(msg, level=2)
                            graph.link(getattr(node, f"port{src_idx}"), sb,
                                       args.linkDelay)


def architecture_spmd(num_boards: int) -> DeviceGraph:
    """Build a row-partitioned device graph, only near args.rank."""
    graph = DeviceGraph()
    subgrids = {}
    my_rank = args.rank

    rows_per = args.height // num_boards if num_boards > 0 else args.height

    start_idx = max(0, my_rank - 1)
    end_idx = min(num_boards, my_rank + 2)

    for i in range(start_idx, end_idx):
        row_start = i * rows_per
        row_end = (i + 1) * rows_per if i != num_boards - 1 else args.height
        sub = SubGrid(f"SubGrid{i}", row_start, row_end)
        sub.set_partition(i)
        graph.add(sub)
        subgrids[i] = sub

    border_start = max(1, my_rank)
    border_end = min(num_boards, my_rank + 2)

    for i in range(border_start, border_end):
        if (i - 1) not in subgrids or i not in subgrids:
            continue
        upper = subgrids[i - 1]
        lower = subgrids[i]
        for src_row_offset in range(NUM_RINGS):
            for tgt_row_offset in range(NUM_RINGS):
                total_di = src_row_offset + 1 + tgt_row_offset
                if total_di > NUM_RINGS:
                    continue
                for j in range(args.width):
                    for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                        if max(total_di, abs(dj)) > NUM_RINGS:
                            continue
                        jj = j + dj
                        if not (0 <= jj < args.width):
                            continue
                        bidx = border_index(j, dj, src_row_offset,
                                            tgt_row_offset)
                        graph.link(upper.southBorder(bidx),
                                   lower.northBorder(bidx), args.linkDelay)

    return graph


def architecture_global(num_boards: int) -> DeviceGraph:
    """Build a row-partitioned device graph with every partition present."""
    graph = DeviceGraph()
    subgrids = {}

    rows_per = args.height // num_boards if num_boards > 0 else args.height
    for i in range(num_boards):
        row_start = i * rows_per
        row_end = (i + 1) * rows_per if i != num_boards - 1 else args.height
        sub = SubGrid(f"SubGrid{i}", row_start, row_end)
        sub.set_partition(i)
        graph.add(sub)
        subgrids[i] = sub

    for i in range(1, num_boards):
        upper = subgrids[i - 1]
        lower = subgrids[i]
        for src_row_offset in range(NUM_RINGS):
            for tgt_row_offset in range(NUM_RINGS):
                total_di = src_row_offset + 1 + tgt_row_offset
                if total_di > NUM_RINGS:
                    continue
                for j in range(args.width):
                    for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                        if max(total_di, abs(dj)) > NUM_RINGS:
                            continue
                        jj = j + dj
                        if not (0 <= jj < args.width):
                            continue
                        bidx = border_index(j, dj, src_row_offset,
                                            tgt_row_offset)
                        graph.link(upper.southBorder(bidx),
                                   lower.northBorder(bidx), args.linkDelay)

    return graph


def architecture(num_boards: int) -> DeviceGraph:
    """Dispatch to the selected architecture function."""
    if args.architecture.lower() == 'spmd':
        return architecture_spmd(num_boards)
    else:
        return architecture_global(num_boards)


def main() -> None:
    """Build the PHOLD grid and render it with the requested options."""
    # Per-rank (parallel) rendering mirrors the per-rank JSON generation: when
    # launched under srun, each task reads its rank from $SLURM_PROCID, prunes
    # the graph to its own slice, and writes its own image.  It can also be
    # forced with --per-rank (rank taken from --rank).
    slurm_rank = os.environ.get('SLURM_PROCID')
    per_rank = (args.per_rank or slurm_rank is not None) and args.num_ranks > 1
    rank = int(slurm_rank) if slurm_rank is not None else args.rank

    if per_rank:
        # Build every partition, then flatten/prune to this rank's slice --
        # exactly the slice a single rank would own (mirrors make_rank_graph
        # and SSTGraph._flatten for nranks > 1).
        graph = architecture_global(args.num_ranks)
        graph.check_partition()
        graph.flatten(rank=rank)
        graph.follow_links(rank, prune=True)
        name = f'phold_global_partition{rank}'
        print(f"Built PHOLD grid slice for rank {rank}/{args.num_ranks}: "
              f"{args.height}x{args.width}, {len(graph.devices)} devices, "
              f"{len(graph.links)} links")
    else:
        graph = architecture(args.num_ranks)
        # Fully expand assemblies so the individual comp nodes (each carrying
        # its partition) are visible in the rendering.
        graph.flatten()
        name = 'phold_global_partition'
        print(f"Built PHOLD grid: {args.height}x{args.width}, "
              f"{args.num_ranks} ranks, {len(graph.devices)} devices, "
              f"{len(graph.links)} links")

    if args.draw_backend.lower() == 'dot':
        # The DOT backend does not support the NetworkX-only toggles.
        graph.write_dot(name, output=output_dir,
                        draw=args.draw, hierarchy=False)
        image = os.path.join(output_dir, f'{name}.svg')
        print(f"Wrote DOT visualization to {image}")
        return

    graph.write_networkx(
        name,
        output=output_dir,
        draw=args.draw,
        hierarchy=False,
        save_graph=args.save_graph,
        color_by_partition=not args.no_color_by_partition,
        highlight_inter_rank=not args.no_highlight_inter_rank,
        self_links=not args.no_self_links,
        layout=grid_layout,
        node_label=grid_label,
    )

    image = os.path.join(output_dir, f'{name}.png')
    print(f"Wrote visualization image to {image}")
    if args.save_graph:
        saved = args.save_graph
        if not os.path.dirname(saved):
            saved = os.path.join(output_dir, saved)
        print(f"Saved NetworkX graph object to {saved}")


if __name__ == '__main__':
    main()
