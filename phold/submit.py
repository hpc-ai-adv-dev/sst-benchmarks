import math
import argparse
import itertools
import subprocess
import os
import random

working_dir = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))

def int_list(value):
  try:
    return [int(x) for x in value.split()]
  except ValueError:
    raise argparse.ArgumentTypeError(f"Invalid list of integers: '{value}'")
  
def float_list(value):
  try:
    return [float(x) for x in value.split()]
  except ValueError:
    raise argparse.ArgumentTypeError(f"Invalid list of floats: '{value}'")

def parse_arguments():
  parser = argparse.ArgumentParser(description="Submit PHOLD benchmark jobs.")

  parser.add_argument('--node_counts', '--node-counts', type=int_list, help="List of node counts to use for the benchmark, e.g., '4 8 16'", required=True)
  parser.add_argument('--thread_counts', '--thread-counts', '--thread-count', type=int_list, help="List of thread counts to use for the benchmark, e.g., '1 2 4'. Default is [1].", default=[1])
  parser.add_argument('--rank_counts', '--rank-counts', '--rank-count', '--ranks_per_node', '--ranks-per-node', type=int_list, default=[1], help="Number of MPI ranks to run per node. Default is 1.")
  parser.add_argument('--widths', '--width', type=int_list, help="List of widths to use for the benchmark, e.g., '100 200 250'", default=None)
  parser.add_argument('--components_per_node', '--components-per-node',  type=int_list, default=None, help="List of components-per-node values to use for the simulation. This is used to calculate widths.")
  parser.add_argument('--heights', '--height', type=int_list, help="List of heights to use for the benchmark, e.g., '100 200 250'. The grid is distributed over this dimension.", required=True)
  parser.add_argument('--event_densities', '--event-densities', '--event-density', type=float_list, help="List of event densities to use for the benchmark, e.g., '0.1 0.5 10'", required=True)
  parser.add_argument('--times_to_run', '--times-to-run', '--time-to-run',type=int_list, help="List of times to run the benchmark, in nanoseconds, e.g., '1 1000 2500'", required=True)
  parser.add_argument('--ring_sizes', '--ring-sizes', '--ring-size', type=int_list, default=[1], help="How many rings of neighboring components each component should connect to, e.g., '1 2 4'. Default is [1].")
  parser.add_argument('--small_payloads', '--small-payloads', '--small-payload', type=int_list, default=[8], help="List of small payload sizes in bytes, e.g., '8 16 32'. Default is [8].")
  parser.add_argument('--large_payloads', '--large-payloads', '--large-payload', type=int_list, default=[1024], help="List of large payload sizes in bytes, e.g., '1024 2048 4096'. Default is [1024].")
  parser.add_argument('--large_event_fractions', '--large-event-fractions', '--large-event-fraction', type=float_list, default=[0.0], help="List of fractions of large events, e.g., '0.1 0.2 0.5'. Default is [0.1].")
  parser.add_argument('--dry_run', '--dry-run', action='store_true', help="If set, only print the commands that would be run without executing them.")
  parser.add_argument('--name', type=str, default="phold", help="(Optional) Name of the benchmark job prepended to output files.")
  parser.add_argument('--imbalance_factors', '--imbalance-factors', '--imbalance-factor', type=float_list, default=[0.0], help="List of imbalance fractions to use, e.g., '0.1 0.2 0.5'. Default is [0.0].")

  # Weak scaling is used to indicate that the combinations of height and width are the "per-node" shape.
  # With a weak scaling run, if we vary the height, we are varying the per-node component count.
  # Sometimes, we want to run weak scaling where the per-node component count is fixed, the height varies, but the width varies.
  # In such a circumstance, we would want to have the per-node component count be used to dynamically calculate the necessary widths.
  # Or maybe, we want to say "the first width is the value that calculates the per-node component count. Vary widths as the height changes to maintain the per-node component count."

  parser.add_argument('--weak_scaling', '--weak', '--weak-scaling', action='store_true', help="If set, the height parameters are treated as \
                      per-node heights rather. If not, then the height parameters are treated as the total grid height.")
  parser.add_argument('--stochastic', type=int, help="If set, treat the arguments to this script as integer constants or range bounds, \
                      rather than lists of values. The value of this variable is the number of points in the resulting space to sample.")
  args = parser.parse_args()
  assert(args.widths is not None or args.components_per_node is not None), "Either --width or --components-per-node must be specified."
  return args




def convert_to_ranges(args):
  if args.stochastic is not None:
    # Turn the single values into ranges with a single element
    if len(args.node_counts) == 1:
      args.node_counts = [args.node_counts[0]] * 2
    if len(args.thread_counts) == 1:
      args.thread_counts = [args.thread_counts[0]] * 2
    if len(args.rank_counts) == 1:
      args.rank_counts = [args.rank_counts[0]] * 2
    if args.widths is not None and len(args.widths) == 1:
      args.widths = [args.widths[0]] * 2
    if len(args.heights) == 1:
      args.heights = [args.heights[0]] * 2
    if len(args.event_densities) == 1:
      args.event_densities = [args.event_densities[0]] * 2
    if len(args.ring_sizes) == 1:
      args.ring_sizes = [args.ring_sizes[0]] * 2
    if len(args.times_to_run) == 1:
      args.times_to_run = [args.times_to_run[0]] * 2
    if len(args.small_payloads) == 1:
      args.small_payloads = [args.small_payloads[0]] * 2
    if len(args.large_payloads) == 1:
      args.large_payloads = [args.large_payloads[0]] * 2
    if len(args.large_event_fractions) == 1:
      args.large_event_fractions = [args.large_event_fractions[0]] * 2
    if len(args.imbalance_factors) == 1:
      args.imbalance_factors = [args.imbalance_factors[0]] * 2
    if args.components_per_node is not None and len(args.components_per_node) == 1:
      args.components_per_node = [args.components_per_node[0]] * 2
  return args


# 
def stochastic_grid_shapes(args):
  '''
  Calculate grid shapes for stochastic runs. 
  We are treating the arguments as ranges, and need to sample from them based 
  on if we are doing weak scaling and if the components_per_node or width is specified
  '''

  node_counts = []
  for i in range(args.stochastic):
    node_count = random.randint(args.node_counts[0], args.node_counts[1])
    node_counts.append(node_count)
  thread_counts = []
  for i in range(args.stochastic):
    thread_count = random.randint(args.thread_counts[0], args.thread_counts[1])
    thread_counts.append(thread_count)
  
  rank_counts = []
  for i in range(args.stochastic):
    rank_count = random.randint(args.rank_counts[0], args.rank_counts[1])
    rank_counts.append(rank_count)
  grid_heights = []
  for i in range(args.stochastic):
    height = random.randint(args.heights[0], args.heights[1])
    if args.weak_scaling:
      grid_heights.append(height * node_counts[i])
    else:
      grid_heights.append(height)
  
  grid_widths = []
  if args.components_per_node is not None:
    for i in range(args.stochastic):
      per_node_component_count = random.randint(args.components_per_node[0], args.components_per_node[1])
      component_count = node_counts[i] * per_node_component_count
      grid_width = math.ceil(component_count / grid_heights[i])
      grid_widths.append(grid_width)
  else:
    for i in range(args.stochastic):
      grid_widths.append(random.randint(args.widths[0], args.widths[1]))

  return list(zip(grid_widths, grid_heights, node_counts, rank_counts, thread_counts))


# The weak scaling determines if the "height" parameter is a per-node value or the entire grid.
def calculate_grid_shapes(args):
  '''
  Creates a list of tuples representing the global grid shape and node counts for the different runs.
  Each tuple is (width, height, node_count, rank_count, thread_count)
  '''
  shapes = []
  if not args.weak_scaling and args.components_per_node is None:
    return list(itertools.product(args.widths, args.heights, args.node_counts, args.rank_counts, args.thread_counts))
  elif args.components_per_node is None:
    # Weak scaling on height per node
    for per_node_width, per_node_height, node_count, rank_count, thread_count in itertools.product(args.widths, args.heights, args.node_counts, args.rank_counts, args.thread_counts):
      shapes.append((per_node_width, per_node_height * node_count, node_count, rank_count, thread_count))
  elif not args.weak_scaling:
    # Weak scaling
    for per_node_component_count, grid_height, node_count, rank_count, thread_count in itertools.product(args.components_per_node, args.heights, args.node_counts, args.rank_counts, args.thread_counts):
      component_count = node_count * per_node_component_count
      grid_width = math.ceil(component_count / grid_height)
      shapes.append((grid_width, grid_height, node_count, rank_count, thread_count))
  else:
    # We are weak scaling and using a per-node component count.
    for per_node_component_count, per_node_height, node_count, rank_count, thread_count in itertools.product(args.components_per_node, args.heights, args.node_counts, args.rank_counts, args.thread_counts):
      component_count = node_count * per_node_component_count
      grid_height = per_node_height * node_count
      grid_width = math.ceil(component_count / grid_height)
      shapes.append((grid_width, grid_height, node_count, rank_count, thread_count))
  return shapes


if __name__ == "__main__":
  args = parse_arguments()

  os.chdir(script_dir)
  subprocess.run("make", shell=True, check=True)
  os.chdir(working_dir)

  args = convert_to_ranges(args)
  if args.stochastic is not None:
    
    shape_parameters = stochastic_grid_shapes(args)
    
    non_shape_parameters = []
    for i in range(args.stochastic):
      density = round(random.uniform(*args.event_densities), 2)
      non_shape_point = (density, random.randint(*args.ring_sizes), random.randint(*args.times_to_run), random.randint(*args.small_payloads),
              random.randint(*args.large_payloads), random.uniform(*args.large_event_fractions), random.uniform(*args.imbalance_factors))
      non_shape_parameters.append(non_shape_point)

    parameters = list(zip(shape_parameters, non_shape_parameters))
  else:
    # Non stochastic run, so we do cartesian product of the parameters

    shape_parameters = calculate_grid_shapes(args)
    non_shape_parameters = list(itertools.product(args.event_densities, args.ring_sizes, args.times_to_run,
                                        args.small_payloads, args.large_payloads, args.large_event_fractions, args.imbalance_factors))
    parameters = list(itertools.product(shape_parameters, non_shape_parameters))

  print("parameters: ", parameters)
  for ((width, height, node_count, rank_count, thread_count), (event_density, ring_size, time_to_run, small_payload, large_payload, large_event_fraction, imbalance_factor)) in parameters:
    output_file = f"{args.name}_{node_count}_{rank_count}_{thread_count}_{width}_{height}_{event_density}_{ring_size}_{time_to_run}_{small_payload}_{large_payload}_{large_event_fraction}_{imbalance_factor}"
    sbatch_portion = f"sbatch -N {node_count} -o {output_file}.out"
    command = f"{sbatch_portion} {script_dir}/dispatch.sh {node_count} {rank_count} {thread_count} {width} {height} {event_density} {ring_size} {time_to_run} {small_payload} {large_payload} {large_event_fraction} {imbalance_factor} {output_file}"
    print(command)
    if not args.dry_run:
      print(f"Running: {command}")
      subprocess.run(command, shell=True, check=True)
      