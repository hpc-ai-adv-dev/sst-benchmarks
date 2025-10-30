"""PHOLD benchmark"""

import argparse
import sst


def log_init(my_rank: int, num_ranks: int, num_threads: int) -> None:
    """Log initial simulation context."""
    print(
        "initializing simulation on rank",
        my_rank,
        "of",
        num_ranks,
        "with",
        num_threads,
        "threads",
    )


def build_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="PHOLD",
        description="Run a simulation of the PHOLD benchmark.",
    )
    parser.add_argument(
        "--N",
        type=int,
        default=10,
        help="Height of grid (number of rows)",
    )
    parser.add_argument(
        "--M",
        type=int,
        default=10,
        help="Width of grid (number of columns)",
    )
    parser.add_argument(
        "--timeToRun",
        type=str,
        default="1000ns",
        help="Time to run the simulation",
    )
    parser.add_argument(
        "--linkDelay",
        type=str,
        default="1ns",
        help="Delay for each link",
    )
    parser.add_argument(
        "--numRings",
        type=int,
        default=1,
        help="Number of rings of neighbors to connect to each component",
    )
    parser.add_argument(
        "--eventDensity",
        type=float,
        default=0.1,
        help="How many events to transmit per component.",
    )
    parser.add_argument(
        "--exponentMultiplier",
        type=float,
        default=1.0,
        help="Multiplier for exponential distribution of event generation",
    )
    parser.add_argument(
        "--nodeType",
        type=str,
        default="phold.Node",
        help="Type of node to create (default: phold.Node)",
    )
    parser.add_argument(
        "--smallPayload",
        type=int,
        default=8,
        help="Size of small event payloads in bytes",
    )
    parser.add_argument(
        "--largePayload",
        type=int,
        default=1024,
        help="Size of large event payloads in bytes",
    )
    parser.add_argument(
        "--largeEventFraction",
        type=float,
        default=0.0,
        help="Fraction of events that are large (default: 0.1)",
    )
    parser.add_argument(
        "--imbalance-factor",
        type=float,
        default=0.0,
        help=(
            "Imbalance factor for thread-level distribution. Value in [0,1] "
            "(0: balanced, 1: single thread does all work)."
        ),
    )
    parser.add_argument(
        "--componentSize",
        type=int,
        default=0,
        help="Size of the additional data field of the component in bytes",
    )
    parser.add_argument(
        "--verbose",
        type=int,
        default=0,
        help="Whether or not to write the recvCount to file.",
    )
    return parser


def imbalance_thread_map(M: int, imbalance_factor: float, thread_count: int):
    """Return a function mapping column index to thread id.

    We allocate relative weights using an imbalance factor. A factor of 0
    distributes evenly; 1.0 assigns all work to thread 0.
    """
    first_weight = (1 + (thread_count - 1) * imbalance_factor) / thread_count
    other_weight = first_weight - imbalance_factor
    weights = [first_weight] + [other_weight] * (thread_count - 1)

    buckets = [0.0]
    for w in weights:
        buckets.append(buckets[-1] + w * M)

    def thread_for_index(idx: int) -> int:
        for t in range(thread_count):
            if buckets[t] <= idx < buckets[t + 1]:
                return t
        return thread_count - 1

    return thread_for_index


def row_to_rank(i: int, N: int, rows_per_rank: int, num_ranks: int) -> int:
    """Map a global row index to MPI rank."""
    if i < 0 or i >= N:
        raise ValueError(f"Row index {i} out of bounds for N={N}")
    return min(i // rows_per_rank, num_ranks - 1)


def col_to_thread(j: int, M: int, thread_map) -> int:
    """Map a column index to thread id using provided map."""
    if j < 0 or j >= M:
        raise ValueError(f"Column index {j} out of bounds for M={M}")
    return thread_map(j)


def create_component(i: int, j: int, args, rows_per_rank: int, num_ranks: int,
                    thread_map):
    """Create and parameterize a PHOLD component, assign rank/thread."""
    comp = sst.Component(f"comp_{i}_{j}", args.nodeType)
    comp.addParams(
        {
            "numRings": args.numRings,
            "i": i,
            "j": j,
            "colCount": args.M,
            "rowCount": args.N,
            "timeToRun": args.timeToRun,
            "multiplier": args.exponentMultiplier,
            "eventDensity": args.eventDensity,
            "smallPayload": args.smallPayload,
            "largePayload": args.largePayload,
            "largeEventFraction": args.largeEventFraction,
            "verbose": args.verbose,
            "componentSize": args.componentSize,
        }
    )
    comp.setRank(
        row_to_rank(i, args.N, rows_per_rank, num_ranks),
        col_to_thread(j, args.M, thread_map),
    )
    return comp


def port_num(i: int, j: int, i2: int, j2: int, num_rings: int) -> int:
    """Compute port index for connection between (i,j) and (i2,j2)."""
    side = num_rings * 2 + 1
    di = i - i2
    dj = j - j2
    ip = num_rings - di
    jp = num_rings - dj
    return ip * side + jp


def connect_upwards(local_i: int, local_j: int, num_rings: int, comps,
                    low_ghost_start: int, args, my_rank: int, num_ranks: int,
                    rows_per_rank: int, link_counter: dict) -> None:
    """Wire links from a local stencil position upwards (including self)."""
    my_idx = ((num_rings * 2 + 1) ** 2 - 1) // 2  # self-connect center
    high_idx = (num_rings * 2 + 1) ** 2 - 1       # max index in stencil

    for nbr_idx in range(my_idx, high_idx + 1):
        side = num_rings * 2 + 1
        my_ring_i = my_idx // side
        my_ring_j = my_idx % side
        nbr_ring_i = nbr_idx // side
        nbr_ring_j = nbr_idx % side
        nbr_i = local_i + nbr_ring_i - my_ring_i
        nbr_j = local_j + nbr_ring_j - my_ring_j

        if nbr_i < 0 or nbr_i >= len(comps) or nbr_j < 0 or nbr_j >= args.M:
            continue

        port1 = port_num(local_i, local_j, nbr_i, nbr_j, num_rings)
        port2 = port_num(nbr_i, nbr_j, local_i, local_j, num_rings)

        global_i = low_ghost_start + local_i
        global_j = local_j
        nbr_global_i = low_ghost_start + nbr_i
        nbr_global_j = nbr_j

        # Require at least one endpoint on this rank
        local_rank = row_to_rank(global_i, args.N, rows_per_rank, num_ranks)
        nbr_rank = row_to_rank(nbr_global_i, args.N, rows_per_rank, num_ranks)
        if local_rank != my_rank and nbr_rank != my_rank:
            continue

        link_name = (
            f"link_{global_i}_{global_j}_to_{nbr_global_i}_{nbr_global_j}"
        )
        link = sst.Link(link_name)
        link.connect(
            (comps[local_i][local_j], f"port{port1}", args.linkDelay),
            (comps[nbr_i][nbr_j], f"port{port2}", args.linkDelay),
        )
        link_counter["count"] += 1 if port1 == port2 else 2


def main() -> None:
    my_rank = sst.getMyMPIRank()
    num_ranks = sst.getMPIRankCount()
    num_threads = sst.getThreadCount()
    log_init(my_rank, num_ranks, num_threads)

    parser = build_parser()
    args = parser.parse_args()

    rows_per_rank = max(1, args.N // num_ranks)
    thread_map = imbalance_thread_map(
        args.M, args.imbalance_factor, num_threads
    )

    # Build local + ghost rows
    my_row_start = my_rank * rows_per_rank
    my_row_end = my_row_start + rows_per_rank
    if my_rank == num_ranks - 1:
        my_row_end = args.N

    low_ghost_start = max(0, my_row_start - args.numRings)
    low_ghost_end = my_row_start
    high_ghost_start = my_row_end
    high_ghost_end = min(args.N, my_row_end + args.numRings)

    comps = []

    # Low ghost rows
    for i in range(low_ghost_start, low_ghost_end):
        row = [
            create_component(i, j, args, rows_per_rank, num_ranks, thread_map)
            for j in range(args.M)
        ]
        comps.append(row)

    # Local owned rows
    for i in range(my_row_start, my_row_end):
        row = [
            create_component(i, j, args, rows_per_rank, num_ranks, thread_map)
            for j in range(args.M)
        ]
        comps.append(row)

    # High ghost rows
    for i in range(high_ghost_start, high_ghost_end):
        row = [
            create_component(i, j, args, rows_per_rank, num_ranks, thread_map)
            for j in range(args.M)
        ]
        comps.append(row)

    link_counter = {"count": 0}
    for local_i in range(len(comps)):
        for local_j in range(args.M):
            connect_upwards(
                local_i,
                local_j,
                args.numRings,
                comps,
                low_ghost_start,
                args,
                my_rank,
                num_ranks,
                rows_per_rank,
                link_counter,
            )

    # Optional verbose summary
    if args.verbose:
        print(f"Total link endpoints registered: {link_counter['count']}")


if __name__ == "__main__":
    main()
