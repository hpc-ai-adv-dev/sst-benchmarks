import math
import argparse
import itertools
import subprocess
import os
import random

working_dir = os.getcwd()
script_dir = os.path.dirname(os.path.realpath(__file__))

def int_list(value: str) -> list[int]:
  """Parse a whitespace-separated string into a list of integers.
  Args:
      value: A whitespace-separated string of integers or mathematical expressions.
      
  Returns:
      A list of integers parsed from the input string.
      
  Raises:
      argparse.ArgumentTypeError: If the input cannot be converted to integers.
      
  Examples:
      >>> int_list('1 2 3')
      [1, 2, 3]
      >>> int_list('1 2*2 4')
      [1, 4, 4]
  """
  try:
    return [int(eval(x)) for x in value.split()]
  except ValueError:
    raise argparse.ArgumentTypeError(f"Invalid list of integers: '{value}'")
  
def float_list(value: str) -> list[float]:
  """Parse a whitespace-separated string into a list of floating-point numbers.

  Args:
      value: A whitespace-separated string of floating-point numbers.
      
  Returns:
      A list of floats parsed from the input string.
      
  Raises:
      argparse.ArgumentTypeError: If the input cannot be converted to floats.
      
  Examples:
      >>> float_list('0.1 0.5 1.0')
      [0.1, 0.5, 1.0]
      >>> float_list('1.5 2.5 3.5')
      [1.5, 2.5, 3.5]
  """
  try:
    return [float(x) for x in value.split()]
  except ValueError:
    raise argparse.ArgumentTypeError(f"Invalid list of floats: '{value}'")

def parse_arguments() -> argparse.Namespace:
  """Parse and validate command-line arguments for PHOLD benchmark submission.
  
  Raises:
      AssertionError: If neither --width nor --components-per-node is specified.
      SystemExit: If parsing fails or required arguments are missing.
  """
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
  parser.add_argument('--component_sizes', '--component-sizes', '--component-size', type=int_list, default=[0], help="List of component sizes to use, in bytes. Default is [0]")
  parser.add_argument('--component_computations', '--component-computations', '--component-computation', type=int_list, default=[0], help="List of component computation times to use, in random number generations per event. Default is [0]")

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
  """
  Normalizes the arguments for stochastic runs by expanding single-value arguments into a single-value range.
  """
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
    if args.component_sizes is not None and len(args.component_sizes) == 1:
      args.component_sizes = [args.component_sizes[0]] * 2
    if args.component_computations is not None and len(args.component_computations) == 1:
      args.component_computations = [args.component_computations[0]] * 2
  return args


# 
def stochastic_grid_shapes(args):
  """
  Calculate grid shapes for stochastic runs. 
  We are treating the arguments as ranges, and need to sample from them based 
  on if we are doing weak scaling and if the components_per_node or width is specified
  """

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

def generate_parameter_list(args):
  """
  Given an argparser Namespace `args`, produces a list of tuples representing the parameters of each run to execute. 
  Each tuple contains two tuples: (shape_parameter_tuple, non_shape_parameter_tuple).
  The shape parameter tuple is: (width, height, node_count, rank_count, thread_count)
  The non-shape parameter tuple is:
    (event_density, ring_size, time_to_run, 
     small_payload, large_payload, large_event_fraction, 
     imbalance_factor, component_size, component_computation)
  """
  args = convert_to_ranges(args)
  if args.stochastic is not None:
    shape_parameters = stochastic_grid_shapes(args)
    non_shape_parameters = []
    for i in range(args.stochastic):
      density = round(random.uniform(*args.event_densities), 2)
      non_shape_point = (density, random.randint(*args.ring_sizes), 
                         random.randint(*args.times_to_run), random.randint(*args.small_payloads),
                         random.randint(*args.large_payloads), random.uniform(*args.large_event_fractions),
                         random.uniform(*args.imbalance_factors), random.randint(*args.component_sizes), 
                         random.randint(*args.component_computations))
      non_shape_parameters.append(non_shape_point)
    parameters = list(zip(shape_parameters, non_shape_parameters))
  else:
    # Non stochastic run, so we do cartesian product of the parameters
    shape_parameters = calculate_grid_shapes(args)
    non_shape_parameters = list(itertools.product(args.event_densities, args.ring_sizes, args.times_to_run,
                                                  args.small_payloads, args.large_payloads, args.large_event_fractions, 
                                                  args.imbalance_factors, args.component_sizes, args.component_computations))
    parameters = list(itertools.product(shape_parameters, non_shape_parameters))
  
  return parameters

def generate_phold_args(node_counts=[1], thread_counts=[1], rank_counts=[1], 
                        widths=[100], heights=[100], components_per_node=None,
                        event_densities=[0.1], ring_sizes=[1], times_to_run=[1000],
                        small_payloads=[8], large_payloads=[1024], large_event_fractions=[0.0], 
                        imbalance_factors=[0.0], component_sizes=[0], component_computations=[0],
                        name="phold", weak_scaling=False, stochastic=None) -> list[tuple[str, str, str]]:
  """Generate PHOLD benchmark parameter combinations and corresponding srun/phold arguments.
  
  This is the primary library interface for generating PHOLD benchmark configurations.
  It supports both deterministic parametric sweeps (Cartesian product of parameters) and
  stochastic sampling of the parameter space. Useful for notebook workflows and programmatic
  benchmark configuration.
  
  Args:
      node_counts (list[int]): Node counts for benchmark runs. Each value represents the number
          of computing nodes to allocate for a run. Default is [1].
      thread_counts (list[int]): Thread counts per node. Controls CPU parallelism within each rank.
          Default is [1].
      rank_counts (list[int]): Number of MPI ranks to run per node. Controls MPI parallelism
          within each node. Default is [1].
      widths (list[int]): Grid widths for the simulation. Represents the first dimension of the
          component grid. Either this or components_per_node must be specified. Default is [100].
      heights (list[int]): Grid heights or per-node heights (see weak_scaling). Represents the
          second dimension over which the grid is distributed. Default is [100].
      components_per_node (list[int] | None): Target component counts per node. When specified,
          grid widths are dynamically calculated to achieve approximately this many components per
          node. Mutually exclusive with direct width specification for weak scaling calculations.
          Default is None.
      event_densities (list[float]): Event densities for the simulation. Controls the frequency
          of events generated per component. Higher densities produce more events. Examples: 0.1, 0.5, 10.
          Default is [0.1].
      ring_sizes (list[int]): Number of rings of neighboring components each component should connect to.
          Controls graph connectivity. ring_size=1 means only immediate neighbors, ring_size=2 includes
          neighbors one ring further out, etc. Default is [1].
      times_to_run (list[int]): Simulation times in nanoseconds (ns). Controls how long each simulation runs.
          Examples: 1000, 10000, 100000. Default is [1000].
      small_payloads (list[int]): Small event payload sizes in bytes. Default is [8].
      large_payloads (list[int]): Large event payload sizes in bytes. Default is [1024].
      large_event_fractions (list[float]): Fraction of events that should be large (vs. small).
          Must be in range [0.0, 1.0]. 0.0 means all events are small, 1.0 means all are large.
          Default is [0.0].
      imbalance_factors (list[float]): Load imbalance factors. Controls computational load variation
          across components. 0.0 means perfectly balanced, > 0.0 introduces increasing imbalance.
          Default is [0.0].
      component_sizes (list[int]): Component memory sizes in bytes. Allows simulation of varying
          component footprints. Default is [0] (minimal).
      component_computations (list[int]): Computation iterations per event. Controls the amount of
          work performed per event reception. Specified in random number generations. Default is [0] (no computation).
      name (str): Job name prefix prepended to all output filenames. Useful for organizing benchmark runs.
          Default is "phold".
      weak_scaling (bool): If True, height parameters are treated as per-node heights (components scale
          with node count). If False, height represents the total grid height (strong scaling).
          Default is False.
      stochastic (int | None): If set to a positive integer N, treats list parameters as range bounds
          [min, max] and randomly samples N points from each parameter's range instead of performing
          a Cartesian product. Enables efficient exploration of high-dimensional parameter spaces.
          Default is None (deterministic Cartesian product).
          
  Returns:
      list[tuple[str, str, str, str]]: List of tuples, one per benchmark run, containing:
          - srun_args (str): srun command-line arguments (--nodes, --cpus-per-task, --ntasks-per-node)
          - sst_args (str): sst command-line arguments (primarily thread count)
          - phold_args (str): PHOLD executable arguments (height, width, event density, etc.)
          - run_name (str): Unique identifier for the run based on all parameters
  """

  args = argparse.Namespace(node_counts=node_counts, thread_counts=thread_counts, rank_counts=rank_counts, widths=widths, heights=heights,
                          components_per_node=components_per_node, event_densities=event_densities, ring_sizes=ring_sizes, times_to_run=times_to_run,
                          small_payloads=small_payloads, large_payloads=large_payloads, large_event_fractions=large_event_fractions, 
                          imbalance_factors=imbalance_factors, component_sizes=component_sizes, component_computations=component_computations,
                          name=name, weak_scaling=weak_scaling, stochastic=stochastic)
  
  parameter_tuples = generate_parameter_list(args)
  
  arg_tuples = [] # The quadruples that contain the srun arguments, sst arguments, phold script arguments, and the run name
  for ((width, height, node_count, rank_count, thread_count), 
       (event_density, ring_size, time_to_run, small_payload, large_payload, 
        large_event_fraction, imbalance_factor, component_size, component_computation)) in parameter_tuples:
    srun_args = f"--nodes={node_count} --cpus-per-task={thread_count} --ntasks-per-node={rank_count}"
    sst_args = f"--num-threads={thread_count}"
    phold_args = f"--height {height} --width {width} --eventDensity {event_density} --timeToRun {time_to_run}ns --numRings {ring_size} --smallPayload {small_payload} --largePayload {large_payload} --largeEventFraction {large_event_fraction} --imbalance-factor {imbalance_factor} --componentSize {component_size} --componentComputation {component_computation}"
    run_name = f"{name}_{node_count}_{rank_count}_{thread_count}_{width}_{height}_{event_density}_{ring_size}_{time_to_run}_{small_payload}_{large_payload}_{large_event_fraction}_{imbalance_factor}_{component_size}_{component_computation}"
    arg_tuples.append((srun_args, sst_args, phold_args, run_name))
  return arg_tuples

if __name__ == "__main__":
  args = parse_arguments()

  os.chdir(script_dir)
  subprocess.run("make", shell=True, check=True)
  os.chdir(working_dir)

  parameters = generate_parameter_list(args)

  print("parameters: ", parameters)
  for ((width, height, node_count, rank_count, thread_count), 
       (event_density, ring_size, time_to_run, small_payload, large_payload, large_event_fraction, imbalance_factor, component_size, component_computation)) in parameters:
    output_file = f"{args.name}_{node_count}_{rank_count}_{thread_count}_{width}_{height}_{event_density}_{ring_size}_{time_to_run}_{small_payload}_{large_payload}_{large_event_fraction}_{imbalance_factor}_{component_size}_{component_computation}"
    sbatch_portion = f"sbatch -N {node_count} -o {output_file}.out"
    command = f"{sbatch_portion} {script_dir}/dispatch.sh {node_count} {rank_count} {thread_count} {width} {height} {event_density} {ring_size} {time_to_run} {small_payload} {large_payload} {large_event_fraction} {imbalance_factor} {component_size} {component_computation} {output_file}"
    print(command)
    if not args.dry_run:
      print(f"Running: {command}")
      subprocess.run(command, shell=True, check=True)
      