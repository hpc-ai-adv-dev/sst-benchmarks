import argparse, itertools
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
    '--partitioner', type=str, default='ahp_graph',
    help='Which partitioner to use: ahp_graph or sst?')
args = parser.parse_args()


if SST:
    sst.setProgramOption("stop-at", args.timeToRun)
    my_rank = sst.getMyMPIRank()
    num_ranks = sst.getMPIRankCount()
else:
    my_rank = 0
    num_ranks = 1

def port_num(src_i, src_j, dst_i, dst_j, num_rings):
    side_length = num_rings * 2 + 1
    di = src_i - dst_i
    dj = src_j - dst_j
    ip = num_rings - di
    jp = num_rings - dj
    return ip * side_length + jp

class Node(Device):
    """PHOLD node device"""
    library = args.nodeType

    """ 
    Below is an examble of a 5x5 grid. There are 3 types of nodes in this grid. 
    The Z nodes have the least amount of connections; the Y nodes have the 
    second least amount of connections; the X nodes have the maximum number of 
    connections. This is true for when the number of rings is greater than or
    equal to 1.
    
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
        for di in range(-args.numRings, args.numRings + 1):
            for dj in range(-args.numRings, args.numRings + 1):
                # Ensures that the ring offsets are never more than the size
                # of the ring or at least greater than or equal to one. Also
                # ensures that nodes are connected to themselves.
                if (1 <= max(abs(di), abs(dj)) <= args.numRings or
                        (di == 0 and dj == 0)):
                    # Calculate the indices of the neighbors of the node 
                    # centered at (i,j).
                    dst_i = i + di 
                    dst_j = j + dj
                    
                    # Only add port if neighbor is within the global grid
                    if 0 <= dst_i < args.N and 0 <= dst_j < args.M:
                        pnum = port_num(i, j, dst_i, dst_j, args.numRings)
                        pname = f"port{pnum}"
                        self.portinfo.add(pname, "String")
        
        self.attr = {
            "i": i,
            "j": j,
            "numRings": args.numRings,
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
    """Assembly of vertices as a SubGrid for a partition"""
    
    def __init__(self, name, row_start, row_end, max_size):
        super().__init__(name)
        self.portinfo = PortInfo()
        self.row_start = row_start
        self.row_end = row_end
        self.max_size = max_size
        self.nodes = {}

        # Create indexed border ports as instance attributes
        for j in range(args.M*self.max_size):
            print(j)
            if row_start > 0:
                self.portinfo.add(f'northBorder{j}', 'String')
            
            if row_end < args.N - 1:
                self.portinfo.add(f'southBorder{j}', 'String')
    
    def expand(self, graph: DeviceGraph) -> None:
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        # print(self.name)
        
        self.nodes = {}
        for i in range(self.row_start, self.row_end):
            self.nodes[i] = {}
            for j in range(args.M):
                n = Node(f"node_{i}_{j}", i, j)
                self.nodes[i][j] = n
                # print(n)

        M, numRings = args.M, args.numRings
        ring_range = range(-numRings, numRings + 1)
        index_range = itertools.product(
            range(self.row_start, self.row_end), range(M)
        )
        offset_range = list(itertools.product(ring_range, ring_range))

        # Track which ports have been linked for each node
        linked_ports = {
            (i, j): set() for i in range(self.row_start, self.row_end)
            for j in range(M)
        }

        for i, j in index_range:
            for di, dj in offset_range:
                if (
                    1 <= max(abs(di), abs(dj)) <= numRings or
                    (di == 0 and dj == 0)
                ):
                    ni = i + di
                    nj = j + dj
                    src_idx = port_num(i, j, ni, nj, numRings)
                    src_port = f"port{src_idx}"
                    if src_port not in self.nodes[i][j].portinfo:
                        continue  # Skip if port doesn't exist
                    if src_port in linked_ports[(i, j)]:
                        continue  # Already linked this port

                    # Internal neighbor within this subgrid
                    if (
                        self.row_start <= ni < self.row_end and
                        0 <= nj < M
                    ):
                        tgt_idx = port_num(ni, nj, i, j, numRings)
                        tgt_port = f"port{tgt_idx}"
                        if tgt_port in self.nodes[ni][nj].portinfo:
                            print(
                                f"Linking {self.nodes[i][j].name}" 
                                f" ({src_port}) -> "
                                f"{self.nodes[ni][nj].name} ({tgt_port})"
                            )
                            graph.link(
                                getattr(self.nodes[i][j], src_port),
                                getattr(self.nodes[ni][nj], tgt_port),
                                args.linkDelay
                            )
                            linked_ports[(i, j)].add(src_port)
                            linked_ports[(ni, nj)].add(tgt_port)
                    # Neighbor is outside this subgrid but inside the global grid
                    elif 0 <= ni < args.N and 0 <= nj < M:
                        if ni < self.row_start:
                            border_port = getattr(self, f"northBorder{ni}")
                            print(
                                f"Linking {self.nodes[i][j].name} ({src_port}) -> "
                                f"{border_port}"
                            )
                            graph.link(
                                getattr(self.nodes[i][j], src_port),
                                border_port,
                                args.linkDelay
                            )
                            linked_ports[(i, j)].add(src_port)
                        elif ni >= self.row_end:
                            border_port = getattr(self, f"southBorder{nj}")
                            print(
                                f"Linking {self.nodes[i][j].name} ({src_port}) -> "
                                f"{border_port}"
                            )
                            graph.link(
                                getattr(self.nodes[i][j], src_port),
                                border_port,
                                args.linkDelay
                            )
                            linked_ports[(i, j)].add(src_port)
                    # If neighbor is outside the global grid, do nothing
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        # print()

# Calculates the rank based on the row index
def row_to_rank(i, rows_per_rank, num_ranks):
    if i < 0 or i >= args.N:
        raise ValueError(f"Row index {i} is out of bounds for N={args.N}")
    return min(i // rows_per_rank, num_ranks - 1)

def assemble_grid(num_ranks) -> DeviceGraph:
    # Get max size of nodes covered by rings
    count = 0
    for i in range(-args.numRings, args.numRings + 1):
        count += 1
    max_size = count**2

    grid = DeviceGraph()
    subgrids = dict()
    rows_per_rank = args.N // num_ranks
    for i in range(num_ranks):
        row_start = i * rows_per_rank
        row_end = row_start + rows_per_rank if i != num_ranks - 1 else args.N
        subgrids[i] = SubGrid(f"SubGrid{i}", row_start, row_end, max_size)
        subgrids[i].set_partition(i)
        grid.add(subgrids[i])

    # Connect border ports between adjacent SubGrids for all columns
    for i in range(num_ranks - 1):
        upper = subgrids[i]
        lower = subgrids[i + 1]
        for j in range(args.M):
            # Connect all border ports for all columns
            uport = f"southBorder{j}"
            lport = f"northBorder{j}"
            grid.link(
                getattr(upper, uport),
                getattr(lower, lport),
                args.linkDelay
            )

    return grid

ahp_graph = assemble_grid(num_ranks)
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
        sst_graph.write_json('phold', nranks=num_ranks, rank=my_rank)