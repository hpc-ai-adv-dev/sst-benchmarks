import sys
import os
import argparse

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
    '--height', type=int, dest='height', default=10,
    help='Height of grid (number of rows)'
)
parser.add_argument(
    '--width', type=int, dest='width', default=10,
    help='Width of grid (number of columns)'
)
parser.add_argument(
    '--timeToRun', '--time-to-run', type=str, default='1000ns',
    help='Time to run the simulation'
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
    '--eventDensity', '--event-density', type=float, default=0.1,
    help='How many events to transmit per component.'
)
parser.add_argument(
    '--exponentMultiplier', '--exponent-multiplier', type=float, default=1.0,
    help='Multiplier for exponential distribution of event generation'
)
parser.add_argument(
    '--nodeType', '--node-type', type=str, default='phold.Node',
    help='Type of node to create (default: phold.Node)'
)
parser.add_argument(
    '--smallPayload', '--small-payload', type=int, default=8,
    help='Size of small event payloads in bytes'
)
parser.add_argument(
    '--largePayload', '--large-payload', type=int, default=1024,
    help='Size of large event payloads in bytes'
)
parser.add_argument(
    '--largeEventFraction', '--large-event-fraction', type=float, default=0.0,
    help='Fraction of events that are large (default: 0.1)'
)
parser.add_argument(
    '--imbalance-factor', type=float, default=0.0,
    help=(
        'Imbalance factor for the simulation\'s thread-level distribution.'
    )
)
parser.add_argument(
    '--componentSize', '--component-size', type=int, default=0,
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
    '--no-self-links', action='store_true', default=False,
    help='Disable self-links; by default self-links are enabled.'
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
parser.add_argument(
    '--build', action='store_true', default=False,
    help='Build the topology with SST.'
)
parser.add_argument(
    '--write', action='store_true', default=False,
    help='Write the topology to JSON.'
)
parser.add_argument(
    '--draw', action='store_true', default=False,
    help='Write the topology to DOT.'
)
args = parser.parse_args()


if SST:
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
    """Return port index for link from (src_i,src_j) to (dst_i,dst_j).

    Uses a (2R+1)x(2R+1) grid centered at the source; offset (di,dj)
    maps to a unique index consistent with `offset_index()`.
    """
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
    """PHOLD node device: exposes ports to neighbors within R rings."""
    library = args.nodeType

    def __init__(self, name, i, j):
        """Create node at (i,j) and add ports for in-bounds neighbors.

        Ports follow the ring neighborhood up to `NUM_RINGS`, including self.
        """
        super().__init__(name)
        self.type = None
        self.portinfo = PortInfo()
        
        # Iterate neighbor offsets within ring radius; include self (0,0).
        for di in range(-NUM_RINGS, NUM_RINGS + 1):
            for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                # Enforce ring boundary and allow self.
                if (1 <= max(abs(di), abs(dj)) <= NUM_RINGS or
                        (di == 0 and dj == 0)):
                    # Neighbor coordinates.
                    dst_i = i + di 
                    dst_j = j + dj
                    
                    # Add port if neighbor is within the global grid.
                    if 0 <= dst_i < args.height and 0 <= dst_j < args.width:
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
            "rowCount": args.height,
            "colCount": args.width
        }


class SubGrid(Device):
    """Row-partitioned assembly; wires internal links and border anchors."""

    # Expose indexed north/south border multi-ports sized for all columns and
    # all offsets within the ring neighborhood.
    portinfo = PortInfo()
    portinfo.add('northBorder', 'String', limit=args.width*MAX_SIZE, required=False)
    portinfo.add('southBorder', 'String', limit=args.width*MAX_SIZE, required=False)

    def __init__(self, name, row_start, row_end):
        """Initialize subgrid covering rows [row_start, row_end)."""
        super().__init__(name)
        self.row_start = row_start
        self.row_end = row_end
        self.nodes = {}
    
    def expand(self, graph: DeviceGraph) -> None:
        """Construct child nodes and wire internal and border links.

        Internal links use a duplicate-avoid rule; border links are anchored
        via single representative connections per multi-port index.
        """
        self.nodes = {}
        for i in range(self.row_start, self.row_end):
            self.nodes[i] = {}
            for j in range(args.width):
                n = Node(f"comp_{i}_{j}", i, j)
                # Ensure child nodes inherit the SubGrid's partition (rank, thread)
                if getattr(self, 'partition', None) is not None:
                    n.set_partition(self.partition[0], self.partition[1])
                self.nodes[i][j] = n

        M = args.width
    
        # Defer border wiring to sweeps to avoid multi-link collisions.
        for i in range(self.row_start, self.row_end):
            for j in range(M):
                for di in range(-NUM_RINGS, NUM_RINGS + 1):
                    for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                        # Enforce ring boundary.
                        if max(abs(di), abs(dj)) > NUM_RINGS:
                            continue

                        ni = i + di
                        nj = j + dj

                        # Only consider in-bounds neighbors in global grid
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
                                # Duplicate-avoid rule for non-self internal wiring
                                if not (di < 0 or (di == 0 and dj < 0)):
                                    continue

                            if args.verbose >= 2:
                                msg = (
                                    f"Internal link: {self.name}.comp_{i}_{j}."
                                    f"{src_port} <-> {self.name}.comp_{ni}_{nj}."
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
                        # Neighbor outside this subgrid: handled by border sweeps.
                        elif 0 <= ni < args.height:
                            continue

        # Single-link border sweeps: one anchor per border index.
        top = self.row_start
        bot = self.row_end - 1
        
        # North border sweep
        for bidx in range(args.width * MAX_SIZE):
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
            if 0 <= nj < args.width and ni < self.row_start:
                src_idx = port_num(i, j, ni, nj)
                node = self.nodes[i][j]
                if args.verbose >= 2:
                    msg = (
                        f"Border link (north): {self.name}.comp_{i}_{j}.port{src_idx} "
                        f"-> {self.name}.northBorder[{bidx}] (delay {args.linkDelay})"
                    )
                    log_link(msg, level=2)
                graph.link(getattr(node, f"port{src_idx}"), nb, args.linkDelay)
        
        # South border sweep
        for bidx in range(args.width * MAX_SIZE):
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
            if 0 <= nj < args.width and ni >= self.row_end:
                src_idx = port_num(i, j, ni, nj)
                node = self.nodes[i][j]
                if args.verbose >= 2:
                    msg = (
                        f"Border link (south): {self.name}.comp_{i}_{j}.port{src_idx} "
                        f"-> {self.name}.southBorder[{bidx}] (delay {args.linkDelay})"
                    )
                    log_link(msg, level=2)
                graph.link(getattr(node, f"port{src_idx}"), sb, args.linkDelay)


def architecture(num_boards: int) -> DeviceGraph:
    """Build a row-partitioned device graph and connect adjacent borders."""
    graph = DeviceGraph()
    subgrids = {}

    # Divide rows evenly among boards; last gets remainder.
    rows_per = args.height // num_boards if num_boards > 0 else args.height
    for i in range(num_boards):
        row_start = i * rows_per
        row_end = (i + 1) * rows_per if i != num_boards - 1 else args.height
        sub = SubGrid(f"SubGrid{i}", row_start, row_end)
        sub.set_partition(i)
        graph.add(sub)
        subgrids[i] = sub

    # Connect borders between adjacent SubGrids.
    for i in range(1, num_boards):
        upper = subgrids[i - 1]
        lower = subgrids[i]
        for j in range(args.width):
            for di in range(1, NUM_RINGS + 1):  # south from upper
                for dj in range(-NUM_RINGS, NUM_RINGS + 1):
                    jj = j + dj
                    if not (0 <= jj < args.width):
                        continue
                    u_idx = border_index(j, di, dj)
                    l_idx = jj * MAX_SIZE + offset_index(-di, -dj)
                    if args.verbose >= 2:
                        msg = (
                            f"Inter-subgrid link: {upper.name}.southBorder[{u_idx}] "
                            f"<-> {lower.name}.northBorder[{l_idx}] (delay {args.linkDelay})"
                        )
                        log_link(msg, level=2)
                    graph.link(
                        upper.southBorder(u_idx),
                        lower.northBorder(l_idx), 
                        args.linkDelay
                    )

    return graph

if sum([args.write, args.build, args.draw]) > 1:
    raise SystemExit("Error: Only one of --write, --build, or --draw can be specified.") 

if args.draw:
    raise SystemExit("Error: --draw is not implemented.")

ahp_graph = architecture(num_ranks)
sst_graph = SSTGraph(ahp_graph)


if SST:
    if args.partitioner.lower() == 'sst' and args.build:
        sst_graph.build()
    elif args.partitioner.lower() == 'sst' and args.write:
        sst_graph.write_json('ahp_phold_sst_part_mpi.json', nranks=num_ranks, rank=my_rank)
    elif args.partitioner.lower() == 'ahp_graph' and args.build:
        sst_graph.build(num_ranks)
    elif args.partitioner.lower() == 'ahp_graph' and args.write:
        sst_graph.write_json('ahp_phold_ahp_part_mpi.json', nranks=num_ranks, rank=my_rank)
    else:
        raise SystemExit("Error: Invalid partitioner or missing action (--build or --write).")
else:
    if args.partitioner.lower() == 'sst' and args.write:
        sst_graph.write_json('ahp_phold_sst_part_python.json', nranks=num_ranks, rank=my_rank)
    elif args.partitioner.lower() == 'ahp_graph' and args.write:
        sst_graph.write_json('ahp_phold_ahp_part_python.json', nranks=num_ranks, rank=my_rank)
    else:
        raise SystemExit("Error: Invalid partitioner or missing action (--write).")