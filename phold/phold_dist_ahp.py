import sys
import os
import argparse
import itertools

# Allow importing local ahp_graph if not installed
sys.path.append(os.environ.get('AHP_PATH', '.'))
from ahp_graph.Device import Device, PortInfo
from ahp_graph.DeviceGraph import DeviceGraph
from ahp_graph.SSTGraph import SSTGraph


try:
    import sst  # type: ignore[import]
    SST = True
except Exception:
    SST = False


parser = argparse.ArgumentParser(
    description='Run a simulation of the PHOLD benchmark using AHP.'
)
parser.add_argument(
    '--N', type=int, default=10,
    help='Height of grid (number of rows)'
)
parser.add_argument(
    '--M', type=int, default=10,
    help='Width of grid (number of columns)'
)
parser.add_argument(
    '--timeToRun', type=str, default='1000ns',
    help='Time to run the simulation'
)
parser.add_argument(
    '--linkDelay', type=str, default='1ns',
    help='Delay for each link'
)
parser.add_argument(
    '--numRings', type=int, default=1,
    help='Number of rings of neighbors to connect to each component'
)
parser.add_argument(
    '--eventDensity', type=float, default=0.1,
    help='How many events to transmit per component.'
)
parser.add_argument(
    '--exponentMultiplier', type=float, default=1.0,
    help='Multiplier for exponential distribution of event generation'
)
parser.add_argument(
    '--nodeType', type=str, default='phold.Node',
    help='Type of node to create (default: phold.Node)'
)
parser.add_argument(
    '--smallPayload', type=int, default=8,
    help='Size of small event payloads in bytes'
)
parser.add_argument(
    '--largePayload', type=int, default=1024,
    help='Size of large event payloads in bytes'
)
parser.add_argument(
    '--largeEventFraction', type=float, default=0.0,
    help='Fraction of events that are large (default: 0.1)'
)
parser.add_argument(
    '--imbalance-factor', type=float, default=0.0,
    help=(
        'Imbalance factor for the simulation\'s thread-level distribution.'
    )
)
parser.add_argument(
    '--componentSize', type=int, default=0,
    help='Size of the additional data field of the component in bytes'
)
parser.add_argument(
    '--verbose', type=int, default=0,
    help='Whether or not to write the recvCount to file.'
)
parser.add_argument(
    '--print-links', action='store_true', default=False,
    help='Print detailed link wiring information.'
)
parser.add_argument(
    '--partitioner', type=str, default='ahp_graph',
    help='Which partitioner to use: ahp_graph or sst?'
)
parser.add_argument(
    '--rank', type=int, default=0,
    help='which rank to generate the JSON file for'
)
parser.add_argument(
    '--numRanks', type=int, default=1,
    help='When running without SST, specify the number of ranks.'
)
args = parser.parse_args()


if SST:
    sst.setProgramOption("stop-at", args.timeToRun)
    my_rank = sst.getMyMPIRank()
    num_ranks = sst.getMPIRankCount()
else:
    my_rank = args.rank
    num_ranks = args.numRanks


def log_link(msg: str, level: int = 1) -> None:
    """Log link wiring if verbosity is sufficient or print-links is set."""
    if args.print_links or args.verbose >= level:
        print(msg)

NUM_RINGS = args.numRings
SIDE = NUM_RINGS * 2 + 1
MAX_SIZE = SIDE * SIDE


def port_num(src_i, src_j, dst_i, dst_j):
    side_length = NUM_RINGS * 2 + 1
    di = src_i - dst_i
    dj = src_j - dst_j
    ip = NUM_RINGS - di
    jp = NUM_RINGS - dj
    return ip * side_length + jp


def offset_index(di: int, dj: int) -> int:
    """Map an offset (di, dj) to a unique index in [0, SIDE*SIDE).

    Indexing order matches port_num's internal grid for consistency.
    """
    ip = NUM_RINGS - di
    jp = NUM_RINGS - dj
    return ip * SIDE + jp


def border_index(col_j: int, di: int, dj: int) -> int:
    """Compute global multi-port index for a border based on column and offset.

    We allocate M * (2R+1)^2 multi-ports per side. For column j we reserve a
    contiguous block of size (2R+1)^2 and index into it using (di, dj).
    """
    return col_j * MAX_SIZE + offset_index(di, dj)


def index_to_offset(idx: int) -> tuple[int, int]:
    """Inverse of offset_index: recover (di, dj) from 0..MAX_SIZE-1."""
    ip = idx // SIDE
    jp = idx % SIDE
    di = NUM_RINGS - ip
    dj = NUM_RINGS - jp
    return di, dj


class Node(Device):
    """PHOLD node device"""
    library = args.nodeType

    """ 
    Below is an examble of a 5x5 grid. There are 3 types of nodes in this grid. 
    The Z nodes have the least amount of connections; the Y nodes have the 
    second least amount of connections; the X nodes have the maximum number of 
    connections. This is true for when the number of rings is equal to 1.
    
    Z Y Y Y Z
    Y X X X Y
    Y X X X Y
    Y X X X Y
    Y X X X Y
    Z Y Y Y Z
    """

    def __init__(self, name, i, j):
        super().__init__(name)
        self.portinfo = PortInfo()
        
        # Double for loop to iterate over the ring space where by default it 
        # will iterate over the full ring space for all the nodes regardless if
        # they are X, Y, or Z nodes. The variables di and dj are the ring
        # offsets.
        for di in range(-NUM_RINGS, NUM_RINGS + 1):
            for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                # Ensures that the ring offsets are never more than the size
                # of the ring or at least greater than or equal to one. Also
                # ensures that nodes are connected to themselves.
                if (1 <= max(abs(di), abs(dj)) <= NUM_RINGS or
                        (di == 0 and dj == 0)):
                    # Calculate the indices of the neighbors of the node 
                    # centered at (i,j).
                    dst_i = i + di 
                    dst_j = j + dj
                    
                    # Only add port if neighbor is within the global grid
                    if 0 <= dst_i < args.N and 0 <= dst_j < args.M:
                        pnum = port_num(i, j, dst_i, dst_j)
                        pname = f"port{pnum}"
                        self.portinfo.add(pname, "String", required=False)
        
        self.attr = {
            "i": i,
            "j": j,
            "numRings": NUM_RINGS,
            "eventDensity": args.eventDensity,
            "multiplier": args.exponentMultiplier,
            "smallPayload": args.smallPayload,
            "largePayload": args.largePayload,
            "largeEventFraction": args.largeEventFraction,
            "componentSize": args.componentSize,
            "timeToRun": args.timeToRun,
            "verbose": args.verbose,
            "rowCount": args.N,
            "colCount": args.M
        }


class SubGrid(Device):
    """Assembly of vertices as a SubGrid for a partition (general ring R>1)."""

    # Expose indexed north/south border multi-ports sized for all columns and
    # all offsets within the ring neighborhood.
    portinfo = PortInfo()
    portinfo.add('northBorder', 'String', limit=args.M*MAX_SIZE, required=False)
    portinfo.add('southBorder', 'String', limit=args.M*MAX_SIZE, required=False)

    def __init__(self, name, row_start, row_end):
        super().__init__(name)
        self.row_start = row_start
        self.row_end = row_end
        self.nodes = {}
    
    def expand(self, graph: DeviceGraph) -> None:
        self.nodes = {}
        for i in range(self.row_start, self.row_end):
            self.nodes[i] = {}
            for j in range(args.M):
                n = Node(f"node_{i}_{j}", i, j)
                self.nodes[i][j] = n

        M = args.M
        ring_range = range(-NUM_RINGS, NUM_RINGS + 1)
        index_range = itertools.product(
            range(self.row_start, self.row_end), range(M)
        )
        offset_range = list(itertools.product(ring_range, ring_range))
    
    # Note: We do NOT directly wire child->border ports here; doing so for
    # each child would attempt to attach many children to the same assembly
    # multi-port index and lead to "already linked" errors in DOT and
    # expansion. Instead, we add exactly ONE representative link per border
    # index in a dedicated sweep after the inner loops (see below). That
    # preserves DOT visuals (green boxes) and provides a clean rewiring
    # anchor for runtime flatten/follow.
        for i, j in index_range:
            for di, dj in offset_range:
                # Enforce ring boundary. 
                if max(abs(di), abs(dj)) > NUM_RINGS:
                    continue

                ni = i + di
                nj = j + dj

                # Only consider in-bounds neighbors in global grid
                if not (0 <= ni < args.N and 0 <= nj < M):
                    continue

                src_idx = port_num(i, j, ni, nj)
                tgt_idx = port_num(ni, nj, i, j)
                src_port = f"port{src_idx}"
                tgt_port = f"port{tgt_idx}"

                # Internal neighbor within this subgrid
                if self.row_start <= ni < self.row_end:
                    # Duplicate-avoid rule only for internal wiring
                    if not (di < 0 or (di == 0 and dj < 0)):
                        continue
                    
                    if args.verbose >= 2:
                        msg = (
                            f"Internal link: {self.name}:node_{i}_{j}."
                            f"{src_port} <-> {self.name}:node_{ni}_{nj}."
                            f"{tgt_port} (delay {args.linkDelay})"
                        )
                        log_link(msg, level=2)
                    
                    src_node = self.nodes[i][j]
                    tgt_node = self.nodes[ni][nj]
                    graph.link(
                        getattr(src_node, src_port),
                        getattr(tgt_node, tgt_port),
                        args.linkDelay,
                    )
                # Neighbor is outside this subgrid but inside the global grid:
                # defer child->border wiring to the single-link border sweeps
                # below to avoid multi-port collisions.
                elif 0 <= ni < args.N:
                    continue

        # Single-link border sweeps (run for both DOT and runtime): ensure all
        # externally linked border ports are anchored to exactly one boundary
        # child to trigger rewiring at runtime and to render green port nodes
        # in hierarchical DOT without multi-link collisions.
        top = self.row_start
        bot = self.row_end - 1
        
        # North border sweep
        for bidx in range(args.M * MAX_SIZE):
            nb = self.northBorder(bidx)
            if nb.link is None:
                continue
            col = bidx // MAX_SIZE
            off = bidx % MAX_SIZE
            di, dj = index_to_offset(off)
            
            # Boundary node on top row
            j = col
            i = top
            ni = i + di
            nj = j + dj
            if 0 <= nj < args.M and ni < self.row_start:
                src_idx = port_num(i, j, ni, nj)
                node = self.nodes[i][j]
                graph.link(getattr(node, f"port{src_idx}"), nb, args.linkDelay)
        
        # South border sweep
        for bidx in range(args.M * MAX_SIZE):
            sb = self.southBorder(bidx)
            if sb.link is None:
                continue
            
            col = bidx // MAX_SIZE
            off = bidx % MAX_SIZE
            di, dj = index_to_offset(off)
            
            # Boundary node on bottom row
            j = col
            i = bot
            ni = i + di
            nj = j + dj
            if 0 <= nj < args.M and ni >= self.row_end:
                src_idx = port_num(i, j, ni, nj)
                node = self.nodes[i][j]
                graph.link(getattr(node, f"port{src_idx}"), sb, args.linkDelay)


def architecture(num_boards: int) -> DeviceGraph:
    graph = DeviceGraph()
    subgrids = {}

    # Divide rows evenly among boards; last gets remainder
    rows_per = args.N // num_boards if num_boards > 0 else args.N
    for i in range(num_boards):
        row_start = i * rows_per
        row_end = (i + 1) * rows_per if i != num_boards - 1 else args.N
        sub = SubGrid(f"SubGrid{i}", row_start, row_end)
        sub.set_partition(i)
        sub.model = f"rank{i}"
        graph.add(sub)
        subgrids[i] = sub

    # Connect borders between adjacent SubGrids
    for i in range(1, num_boards):
        upper = subgrids[i - 1]
        lower = subgrids[i]
        for j in range(args.M):
            for di in range(1, NUM_RINGS + 1):  # south from upper
                for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                    jj = j + dj
                    if not (0 <= jj < args.M):
                        continue
                    u_idx = border_index(j, di, dj)
                    l_idx = jj * MAX_SIZE + offset_index(-di, -dj)
                    graph.link(
                        upper.southBorder(u_idx),
                        lower.northBorder(l_idx), 
                        args.linkDelay
                    )

    return graph

ahp_graph = architecture(num_ranks)
sst_graph = SSTGraph(ahp_graph)


if SST:
    # If running within SST, generate the SST graph
    # There are multiple ways to run, below are two examples

    # SST partitioner
    # This will work in serial or running SST with MPI in parallel
    if args.partitioner.lower() == 'sst':
        sst_graph.build()

    # MPI mode with ahp_graph graph partitioning. Specifying nranks tells
    # ahp_graph that it is doing the partitioning, not SST
    # For this to work you need to pass --parallel-load=SINGLE to sst
    elif args.partitioner.lower() == 'ahp_graph':
        # Fully flatten assemblies ahead of SST build to avoid expansion
        # and ensure no SubGrid assemblies remain in the graph.
        # ahp_graph.flatten()
        sst_graph.build(num_ranks)
else:
    # SST partitioner
    # This will generate a flat dot graph and a single JSON file
    if args.partitioner.lower() == 'sst':
        ahp_graph.flatten()
        ahp_graph.write_dot('pholdFlat', draw=True, ports=True, hierarchy=False)
        sst_graph.write_json('pholdFlat')

    # If ahp_graph is partitioning, we generate a hierarchical DOT graph
    # and a JSON file for the rank that is specified from the command line
    elif args.partitioner.lower() == 'ahp_graph':
        if args.rank == 0:
            ahp_graph.write_dot('phold', draw=True, ports=True)
        sst_graph.write_json('phold', nranks=num_ranks, rank=args.rank)
