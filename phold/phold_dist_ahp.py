import argparse
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


class Node(Device):
    """PHOLD node device"""
    library = args.nodeType

    def __init__(self, name, i, j):
        super().__init__(name)
        self.portinfo = PortInfo()
        count = 0
        for di in range(-args.numRings, args.numRings + 1):
            for dj in range(-args.numRings, args.numRings + 1):
                if 0 <= i + di < args.N and 0 <= j + dj < args.M:
                    if (1 <= max(abs(di), abs(dj)) <= args.numRings or
                            (di == 0 and dj == 0)):
                        pname = f"port{count}"
                        self.portinfo.add(pname, "String")
                        count += 1
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
    """Assembly of Nodes as a SubGrid for a partition"""
    portinfo = PortInfo()

    # TODO: SubGrids will eventually need to have ports to connect to SubGrids
    # that live on other ranks. For now, we are assuming this will be executed
    # on only one rank.

    def port_index(self, i, j, di, dj):
        count = 0
        for ddi in range(-args.numRings, args.numRings + 1):
            for ddj in range(-args.numRings, args.numRings + 1):
                if 0 <= i + ddi < args.N and 0 <= j + ddj < args.M:
                    if (1 <= max(abs(ddi), abs(ddj)) <= args.numRings or
                            (ddi == 0 and ddj == 0)):
                        if ddi == di and ddj == dj:
                            return count
                        count += 1
        return None
    
    def expand(self, graph: DeviceGraph) -> None:
        nodes = {}
        for i in range(args.N):
            nodes[i] = {}
            for j in range(args.M):
                n = Node(f"node_{i}_{j}", i, j)
                nodes[i][j] = n

        for i in range(args.N):
            for j in range(args.M):
                for di in range(-args.numRings, args.numRings + 1):
                    for dj in range(-args.numRings, args.numRings + 1):
                        if (1 <= max(abs(di), abs(dj)) <= args.numRings or
                                (di == 0 and dj == 0)):
                            if (di < 0 or (di == 0 and dj < 0)) and not (
                                    di == 0 and dj == 0):
                                continue
                            ni = i + di
                            nj = j + dj
                            if (0 <= ni < args.N and 0 <= nj < args.M and
                                    0 <= i < args.N and 0 <= j < args.M):
                                src_idx = self.port_index(i, j, di, dj)
                                old_i, old_j = i, j
                                i, j = ni, nj
                                tgt_idx = self.port_index(i, j, -di, -dj)
                                i, j = old_i, old_j
                                if src_idx is not None and tgt_idx is not None:
                                    src_port = f"port{src_idx}"
                                    tgt_port = f"port{tgt_idx}"
                                    print(
                                        f"Linking {nodes[i][j].name}" 
                                        f" ({src_port}) -> "
                                        f"{nodes[ni][nj].name} ({tgt_port})"
                                    )
                                    graph.link(
                                        getattr(nodes[i][j], src_port),
                                        getattr(nodes[ni][nj], tgt_port),
                                        args.linkDelay
                                    )


def assemble_grid(numSubGrids) -> DeviceGraph:
    grid = DeviceGraph()
    subgrids = dict()
    for i in range(numSubGrids):
        subgrids[i] = SubGrid(f"SubGrid{i}")
        subgrids[i].set_partition(i)
        grid.add(subgrids[i])
    
    # TODO: Currently this only creates one SubGrid per rank and does not allow
    # for connections between SubGrids on two different ranks. This has to be
    # modified to allow for links between SubGrids on different ranks.
    
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