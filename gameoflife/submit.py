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
  parser = argparse.ArgumentParser(description="Submit Game Of Life benchmark jobs.")
  
  # submission parameters
  parser.add_argument('--name', type=str, help="Name of the experiment. Default is 'gol'.", default='experiment')
  parser.add_argument('--script', type=str, help="Script to run. Default is 'gol.py'.", default='gol.py')
  # execution environment
  parser.add_argument('--node_counts', '--node-counts', type=int_list, help="List of node counts to use for the benchmark, e.g., '4 8 16'", required=True)
  parser.add_argument('--rank_counts', '--rank-counts', '--rank-count', '--ranks_per_node', '--ranks-per-node', type=int_list, default=[1], help="Number of MPI ranks to run per node. Default is 1.")
  parser.add_argument('--thread_counts', '--thread-counts', '--thread-count', type=int_list, help="List of thread counts to use for the benchmark, e.g., '1 2 4'. Default is [1].", default=[1])
  
  # grid parameters
  parser.add_argument('--widths', '--width', type=int_list, help="List of widths to use for the benchmark, e.g., '100 200 250'", default=None)
  parser.add_argument('--heights', '--height', type=int_list, help="List of heights to use for the benchmark, e.g., '100 200 250'. The grid is distributed over this dimension.", required=True)
  parser.add_argument('--components_per_node', '--components-per-node',  type=int_list, default=None, help="List of components-per-node values to use for the simulation. This is used to calculate widths.")
  parser.add_argument('--components_per_partition', '--components-per-partition',  type=int_list, default=None, help="List of components-per-partition values to use for the simulation. This is used to calculate widths.")

  parser.add_argument('--weak_scaling-node', '--weak', '--weak-scaling', action='store_true',
                      help="If set, the height parameters are treated as per-node heights. If not, then the height parameters are treated as the total grid height.")
  parser.add_argument('--weak-scaling-rank', action='store_true', help='If set, the height parameters are treated as per-rank heights.' )
  parser.add_argument('--weak-scaling-thread', action='store_true', help='If set, the width parameters are treated as per-thread heights.')

  
  # simulation parameters
  parser.add_argument('--probabilities', '--probability', type=int_list, help="List of probabilities (as percents) for the initial state of the grid, e.g., '10 20 30'.", default=[30])
  parser.add_argument('--demands', '--demand', type=int_list, help="List of event `onDemandMode` parameters. 0 or 1 on/off. default [0].", default=[0])
  parser.add_argument('--times_to_run', '--times-to-run', '--time-to-run',type=int_list, help="List of times to run the benchmark, in seconds, e.g., '1 1000 2500'", required=True)
  parser.add_argument('--posts_if_alive', '--post-if-alive', type=int_list, help="Values for postIfAlive. 0 or 1 on/off. Default is [0].", default=[0])

  args = parser.parse_args()
  assert(args.widths is not None or args.components_per_node is not None), "Either --width or --components-per-node must be specified."
  return args

  

def calculate_grid_shapes(args):
  '''
  Returns a tuple of the grid shape and its distribution over nodes, ranks, threads
  '''
  
  shapes = []
  return itertools.product(args.widths, args.heights, args.node_counts, args.rank_counts, args.thread_counts)

if __name__ == "__main__":
  args = parse_arguments()

  os.chdir(script_dir)
  subprocess.run("make", shell=True, check=True)
  os.chdir(working_dir)

  shapes = calculate_grid_shapes(args)

  script = args.script
  for (width, height, node_count, rank_count, thread_count) in shapes:
    for (probability, demand, time_to_run, post_if_alive) in itertools.product( args.probabilities, args.demands, args.times_to_run, args.posts_if_alive):
      time_to_run = str(time_to_run) + 's'
      output_file = f"{args.name}_{script}_{node_count}_{rank_count}_{thread_count}_{width}_{height}_{probability}_{demand}_{time_to_run}_{post_if_alive}"
      sbatch_portion = f"sbatch  -N {node_count} --cpus-per-task {rank_count} --ntasks-per-node {thread_count} -o {output_file}.out"
      bool_flags = ' --postOnlyIfAlive ' if post_if_alive else ' '
      bool_flags += ' --onDemandMode ' if demand else ' '
      sim_flags = bool_flags + f" --prob {probability}"
      command = f'{sbatch_portion} -- {script_dir}/gol-dispatch.sh {script} {node_count} {rank_count} {thread_count} {width} {height} {time_to_run} "{sim_flags}" {output_file} '
      # Construct the command

      
      # Execute the command
      print(command)
      subprocess.run(command, shell=True, check=True)