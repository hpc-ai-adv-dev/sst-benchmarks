
import pandas as pd
import numpy as np
import sys
import os
import traceback

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def identify_result_dirs(experiment_name=None):
  """
  Identify directories containing result files.
  """
  result_dirs = []
  invalid_dirs = []
  for item in os.listdir('.'):
    if os.path.isdir(item) and item.endswith('_dir'):
      if experiment_name is not None and not item.startswith(experiment_name):
        continue  
      has_time_file = any(file.endswith('.time') for file in os.listdir(item))
      has_rank_files = any(file.startswith('rank') for file in os.listdir(item))

      if not has_time_file:
        invalid_dirs.append((item, "Missing .time file"))
      elif not has_rank_files:
        invalid_dirs.append((item, "Missing rank files"))
      else:
        result_dirs.append(item)
        
  return (result_dirs, invalid_dirs)

def extract_sync_data(result_dir):
  """
  Extract synchronization times from the result files in the given directory.
  """
  sync_files = []
  for file_name in os.listdir(result_dir):
    if file_name.startswith('rank') and not '.' in file_name:
      sync_files.append(os.path.join(result_dir, file_name))
  sync_data = []
  for sync_file in sync_files:
    with open(sync_file, 'r') as f:
      lines = f.readlines()
      thread_count_line = lines[-11]
      thread_time_line = lines[-10]
      thread_count = int(thread_count_line.split(':')[1].strip())
      thread_time = float(thread_time_line.split(' ')[-2].strip())
      rank_count_line = lines[-7]
      rank_time_line = lines[-6]
      rank_count = int(rank_count_line.split(':')[1].strip())
      rank_time = float(rank_time_line.split(' ')[-2].strip())
      sync_data.append((thread_count, thread_time, rank_count, rank_time))


  thread_sync_counts = [count for count, _, _, _ in sync_data]
  thread_sync_times = [time for _, time, _, _ in sync_data]
  rank_sync_counts = [count for _, _, count, _ in sync_data]
  rank_sync_times = [time for _, _, _, time in sync_data]

  rank_sync_time_mean = np.mean(rank_sync_times) if rank_sync_times else None
  rank_sync_time_std = np.std(rank_sync_times) if rank_sync_times else None
  rank_sync_count_mean = np.mean(rank_sync_counts) if rank_sync_counts else None
  rank_sync_count_std = np.std(rank_sync_counts) if rank_sync_counts else None
  rank_sync_time_max = np.max(rank_sync_times) if rank_sync_times else None
  rank_sync_time_min = np.min(rank_sync_times) if rank_sync_times else None
  rank_sync_count_max = np.max(rank_sync_counts) if rank_sync_counts else None
  rank_sync_count_min = np.min(rank_sync_counts) if rank_sync_counts else None

  thread_sync_time_mean = np.mean(thread_sync_times) if thread_sync_times else None
  thread_sync_time_std = np.std(thread_sync_times) if thread_sync_times else None
  thread_sync_count_mean = np.mean(thread_sync_counts) if thread_sync_counts else None
  thread_sync_count_std = np.std(thread_sync_counts) if thread_sync_counts else None
  thread_sync_time_max = np.max(thread_sync_times) if thread_sync_times else None
  thread_sync_time_min = np.min(thread_sync_times) if thread_sync_times else None
  thread_sync_count_max = np.max(thread_sync_counts) if thread_sync_counts else None
  thread_sync_count_min = np.min(thread_sync_counts) if thread_sync_counts else None

  return {
    'Rank Sync Time Max (s)': rank_sync_time_max,
    'Rank Sync Time Min (s)': rank_sync_time_min,
    'Rank Sync Time Mean (s)': rank_sync_time_mean,
    'Rank Sync Time Std (s)': rank_sync_time_std,
    'Rank Sync Count Max': rank_sync_count_max,
    'Rank Sync Count Min': rank_sync_count_min,
    'Rank Sync Count Mean': rank_sync_count_mean,
    'Rank Sync Count Std': rank_sync_count_std,
    'Thread Sync Time Max (s)': thread_sync_time_max,
    'Thread Sync Time Min (s)': thread_sync_time_min,
    'Thread Sync Time Mean (s)': thread_sync_time_mean,
    'Thread Sync Time Std (s)': thread_sync_time_std,
    'Thread Sync Count Max': thread_sync_count_max,
    'Thread Sync Count Min': thread_sync_count_min,
    'Thread Sync Count Mean': thread_sync_count_mean,
    'Thread Sync Count Std': thread_sync_count_std
  }


def extract_time_data(results_dir):
  """
  Extract build and run time data from the result files in the given directory.
  """
  time_files = []
  for file_name in os.listdir(results_dir):
    if file_name.endswith('.time'):
      path = os.path.join(results_dir, file_name)
      with open(path, 'r') as f:
        lines = f.readlines()
        build_time = float(lines[0].strip())
        run_time = float(lines[1].strip())
        return {
          'Build Time (s)': build_time,
          'Run Time (s)': run_time
        }

  return None

def extract_parameters(results_dir):
  """
  Extract parameters from the directory name.
  """
  results_dir = results_dir.split('/')[-1]  # Get the last part of the path
  parts = results_dir.split('_')[:-1] # Remove the last part which is  'dir'
  if len(parts) < 5:
    raise ValueError("Directory name does not contain enough parts to extract parameters.")
  
  experiment_name = parts[0]
  script_name = parts[1]
  print(parts)
  experiment_name, script_name, node_count, rank_count, thread_count, width, height, probability, demand, time_to_run, post_if_alive = parts

  return {
    'Experiment Name': experiment_name,
    'Node Count': node_count,
    'Ranks Per Node': rank_count,
    'Thread Count': thread_count,
    'Width': width,
    'Height': height,
    'Time to Run (s)': time_to_run.strip('s'),
    'Probability': probability,
    'Demand': demand,
    'Post If Alive': post_if_alive.strip('s'),
    'Script Name': script_name
  }

failures = []
def extract_row(results_dir):
  try:
    parameters = extract_parameters(results_dir)
    time_data = extract_time_data(results_dir)
    sync_data = extract_sync_data(results_dir)
  except Exception as e:
    print(f"Error extracting data from {results_dir}. Skipping this directory.", e)
    return None
  
  return parameters | time_data | sync_data


if __name__ == "__main__":
  if len(sys.argv) > 3 or len(sys.argv) < 2:
    print("Usage: python consolidate.py [output_file.csv] [optional experiment name to look for]")
    sys.exit(1)
  if len(sys.argv) == 3:
    experiment_name = sys.argv[2]
  else:
    experiment_name = None
  
  outfile = sys.argv[1]

  (result_dirs,invalid_dirs) = identify_result_dirs(experiment_name)
  for invalid_dir, reason in invalid_dirs:
    print(f"Skipping invalid directory {invalid_dir}: {reason}")


  with ProcessPoolExecutor(max_workers=8) as executor:
    data = list(executor.map(extract_row, result_dirs))

  #data = [extract_row(result_dir) for result_dir in result_dirs]
  data = [d for d in data if d is not None]
  if len(data) == 0:
    print("No valid data found. Exiting.")
    sys.exit(0)
  with open(outfile, 'w') as f:
      entry = data[0]
      f.write(','.join(entry.keys()) + "\n")
      for entry in data:
          f.write(','.join(map(str, entry.values())) + "\n")


  print(f"Results consolidated into {outfile}.")
