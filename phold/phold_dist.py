import sst
import argparse

my_rank     = sst.getMyMPIRank()
num_ranks   = sst.getMPIRankCount()
num_threads = sst.getThreadCount()
print('initializing simulation on rank', my_rank, 'of', num_ranks, 'with', num_threads, 'threads')

parser = argparse.ArgumentParser(
  prog='PHOLD',
  description='Run a simulation of the PHOLD benchmark.')

parser.add_argument('--N', type=int, default=10, help='Height of grid (number of rows)')
parser.add_argument('--M', type=int, default=10, help='Width of grid (number of columns)')
parser.add_argument('--timeToRun', type=str, default='1000ns', help='Time to run the simulation')
parser.add_argument("--linkDelay", type=str, default="1ns", help="Delay for each link")
parser.add_argument('--numRings', type=int, default=1, help='Number of rings of neighbors to connect to each component')
parser.add_argument('--eventDensity', type=float, default=0.1, help="How many events to transmit per component. Negative values indicate that each component should start with as many events as links.")
parser.add_argument('--exponentMultiplier', type=float, default=1.0, help="Multiplier for exponential distribution of event generation")
parser.add_argument('--uniformMin', type=float, default=0.0, help="Minimum value for uniform distribution, in ns, in addition to link delay")
parser.add_argument('--uniformMax', type=float, default=1.0, help="Maximum value for uniform distribution, in ns, in addition to link delay")
parser.add_argument('--nodeType', type=str, default='phold.Node', help='Type of node to create (default: phold.Node)')
parser.add_argument('--smallPayload', type=int, default=8, help='Size of small event payloads in bytes')
parser.add_argument('--largePayload', type=int, default=1024, help='Size of large event payloads in bytes')
parser.add_argument('--largeEventFraction', type=float, default=0.0, help='Fraction of events that are large (default: 0.1)')
parser.add_argument('--imbalance-factor', type=float, default=0.0, help="Imbalance factor for the simulation's thread-level distribution." \
                    " This value should be between 0 (representing perfectly load balanced), and 1.0 (representing a single thread doing all the work).")
parser.add_argument('--componentSize', type=int, default=0, help='Size of the additional data field of the component in bytes')
parser.add_argument('--movementFunction', type=str, default='random', help='Movement function to use: random or cyclic')
parser.add_argument('--verbose', type=int, default=0, help='Whether or not to write the recvCount to file.')


args = parser.parse_args()


def imbalance_thread_map(M, imbalance_factor, thread_count):
  """
  Create the boundaries for what column indices each thread gets
  """
  import math
  # firstThread + (otherThreads * (thread_count - 1)) == 1
  # firstThread - otherThreads == imbalance_factor
  # otherThreads = firstThread - imbalance_factor

  # 1 ==  firstThread + (thread_count - 1) * otherThreads
  # 1 == firstThread + (thread_count - 1) * (firstThread - imbalance_factor)
  # 1 == firstThread + (thread_count - 1) * firstThread - (thread_count - 1) * imbalance_factor
  # 1 + (thread_count - 1) * imbalance_factor == firstThread * thread_count
  # firstThread == (1 + (thread_count - 1) * imbalance_factor) / thread_count
  first_thread_weight = (1 + (thread_count - 1) * imbalance_factor) / thread_count
  other_thread_weight = first_thread_weight - imbalance_factor
  weights = [first_thread_weight] + [other_thread_weight] * (thread_count - 1)

  buckets = [0]
  for w in weights:
    buckets.append(buckets[-1] + w * M)

  def thread_for_index(i: int):
    for t in range(thread_count):
      if buckets[t] <= i < buckets[t + 1]:
        return t
    return thread_count - 1

  return thread_for_index


rows_per_rank = args.N // num_ranks
def row_to_rank(i):
  if i < 0 or i >= args.N:
    raise ValueError(f"Row index {i} is out of bounds for N={args.N}")
  # Calculate the rank based on the row index
  return min(i // rows_per_rank, num_ranks - 1)

thread_map = imbalance_thread_map(args.M, args.imbalance_factor, num_threads)
def col_to_thread(i):
  if i < 0 or i >= args.M:
    raise ValueError(f"Column index {i} is out of bounds for M={args.M}")
  # Calculate the thread based on the column index
  return thread_map(i)
  



comps = []


# Create grid of components for my rank
my_row_start = my_rank * rows_per_rank
my_row_end = my_row_start + rows_per_rank #exclusive
if my_rank == num_ranks - 1:  # Last rank gets the rest
  my_row_end = args.N


def create_component(i,j):
  comp = sst.Component(f"comp_{i}_{j}", args.nodeType)
  comp.addParams({
    "numRings": args.numRings,
    "i": i,
    "j": j,
    'colCount': args.M,
    "rowCount": args.N,
    "timeToRun": args.timeToRun,
    "multiplier": args.exponentMultiplier,
    "eventDensity": args.eventDensity,
    "smallPayload": args.smallPayload,
    "largePayload": args.largePayload,
    "largeEventFraction": args.largeEventFraction,
    "verbose": args.verbose,
    "componentSize": args.componentSize,
    "movementFunction": args.movementFunction
  })
  comp.setRank(row_to_rank(i), col_to_thread(j))
  return comp

for i in range(my_row_start, my_row_end):
  row = []
  for j in range(0,args.M):
    comp = create_component(i, j)
    row.append(comp)
  comps.append(row)

low_rows = []

# Create low ghost components
low_ghost_start = max(0,my_row_start - args.numRings)
low_ghost_end = my_row_start
for i in range(low_ghost_start, low_ghost_end):
  row = []
  for j in range(args.M):
    comp = create_component(i, j)
    row.append(comp)
  low_rows.append(row)
comps = low_rows + comps

# Create high ghost components
high_ghost_start = my_row_end
high_ghost_end = min(args.N, my_row_end + args.numRings)
for i in range(high_ghost_start, high_ghost_end):
  row = []
  for j in range(args.M):
    comp = create_component(i,j)
    row.append(comp)
  comps.append(row)




def port_num(i,j,i2,j2, num_rings):
  side_length = (num_rings * 2 + 1)
  di = i-i2
  dj = j-j2
  ip = num_rings - di
  jp = num_rings - dj
  return ip * side_length + jp
 
linkCount = 0

def connect_upwards(local_i, local_j, num_rings):
  global linkCount
  my_idx = ((num_rings * 2 + 1) ** 2 - 1) // 2 # port number for self connect
  high_idx = (num_rings * 2 + 1) ** 2 - 1 # port number for highest connect

  for neighbor_ring_idx in range(my_idx, high_idx + 1):
    # My indices within the stencil
    my_ring_i = my_idx // (num_rings * 2 + 1)
    my_ring_j = my_idx % (num_rings * 2 + 1)

    # The indices of the neighbor component within the stencil
    neighbor_ring_i = neighbor_ring_idx // (num_rings * 2 + 1)
    neighbor_ring_j = neighbor_ring_idx % (num_rings * 2 + 1)

    # The local indices of the neighbor component
    neighbor_i = local_i + neighbor_ring_i - my_ring_i
    neighbor_j = local_j + neighbor_ring_j - my_ring_j

    if neighbor_i < 0 or neighbor_i >= len(comps) or neighbor_j < 0 or neighbor_j >= args.M:
      continue
    
    port1 = port_num(local_i, local_j, neighbor_i, neighbor_j, num_rings)
    port2 = port_num(neighbor_i, neighbor_j, local_i, local_j, num_rings)

    my_global_i = low_ghost_start + local_i
    my_global_j = local_j

    neighbor_global_i = low_ghost_start + neighbor_i
    neighbor_global_j = neighbor_j

    # Only need the links that connect to a component that lives on this rank
    if row_to_rank(my_global_i) != my_rank and row_to_rank(neighbor_global_i) != my_rank:
      continue
  
    link_name = f"link_{my_global_i}_{my_global_j}_to_{neighbor_global_i}_{neighbor_global_j}"
    link = sst.Link(link_name)
    link.connect((comps[local_i][local_j], f"port{port1}", args.linkDelay), 
                 (comps[neighbor_i][neighbor_j], f"port{port2}", args.linkDelay))
    if port1 == port2:
      linkCount += 1
    else:
      linkCount += 2

    


                                           

for local_i in range(len(comps)):
  for local_j in range(args.M):
    connect_upwards(local_i, local_j, args.numRings)