
import pandas as pd
import numpy as np
import sys
import os
import humanfriendly

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


def _parse_sync_file(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        thread_count_line = lines[-11]
        thread_time_line = lines[-10]
        thread_count = int(thread_count_line.split(':')[1].strip())
        thread_time = float(thread_time_line.split(' ')[-2].strip())
        rank_count_line = lines[-7]
        rank_time_line = lines[-6]
        rank_count = int(rank_count_line.split(':')[1].strip())
        rank_time = float(rank_time_line.split(' ')[-2].strip())
        return (thread_count, thread_time, rank_count, rank_time)
    except:
        return None  # skip malformed or incomplete files

def extract_sync_data(result_dir):
    sync_files = [
        os.path.join(result_dir, file_name)
        for file_name in os.listdir(result_dir)
        if file_name.startswith('rank')
    ]

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(_parse_sync_file, sync_files)

    sync_data = [r for r in results if r is not None]

    if not sync_data:
        return {}

    thread_sync_counts = [count for count, _, _, _ in sync_data]
    thread_sync_times = [time for _, time, _, _ in sync_data]
    rank_sync_counts = [count for _, _, count, _ in sync_data]
    rank_sync_times = [time for _, _, _, time in sync_data]

    return {
        'Rank Sync Time Max (s)': np.max(rank_sync_times),
        'Rank Sync Time Min (s)': np.min(rank_sync_times),
        'Rank Sync Time Mean (s)': np.mean(rank_sync_times),
        'Rank Sync Time Std (s)': np.std(rank_sync_times),
        'Rank Sync Count Max': np.max(rank_sync_counts),
        'Rank Sync Count Min': np.min(rank_sync_counts),
        'Rank Sync Count Mean': np.mean(rank_sync_counts),
        'Rank Sync Count Std': np.std(rank_sync_counts),
        'Thread Sync Time Max (s)': np.max(thread_sync_times),
        'Thread Sync Time Min (s)': np.min(thread_sync_times),
        'Thread Sync Time Mean (s)': np.mean(thread_sync_times),
        'Thread Sync Time Std (s)': np.std(thread_sync_times),
        'Thread Sync Count Max': np.max(thread_sync_counts),
        'Thread Sync Count Min': np.min(thread_sync_counts),
        'Thread Sync Count Mean': np.mean(thread_sync_counts),
        'Thread Sync Count Std': np.std(thread_sync_counts)
    }

def extract_sync_data2(result_dir):
  """
  Extract synchronization times from the result files in the given directory.
  """
  sync_files = []
  for file_name in os.listdir(result_dir):
    if file_name.startswith('rank'):
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
        max_resident = humanfriendly.parse_size(lines[2].strip())
        max_global = humanfriendly.parse_size(lines[3].strip())
        return {
          'Build Time (s)': build_time,
          'Run Time (s)': run_time,
          'Max Resident Set Size (bytes)': max_resident,
          'Max Global Set Size (bytes)': max_global
        }

  return None

def extract_parameters(results_dir):
  """
  Extract parameters from the directory name.
  """
  results_dir = results_dir.split('/')[-1]  # Get the last part of the path
  parts = results_dir.split('_')
  if len(parts) < 5:
    raise ValueError("Directory name does not contain enough parts to extract parameters.")
  
  experiment_name = parts[0]
  node_count = int(parts[1])
  rank_count = int(parts[2])
  thread_count = int(parts[3])  
  width = int(parts[4])
  height = int(parts[5])
  event_density = float(parts[6])
  ring_size = int(parts[7])
  time_to_run = int(parts[8])
  small_payload = int(parts[9])
  large_payload = int(parts[10])
  large_event_fraction = float(parts[11])
  imbalance_factor = float(parts[12]) if len(parts) > 12 else 0.0  # Default to 0.0 if not present
  component_size = int(parts[13]) if len(parts) > 13 else 0.0
  return {
    'Experiment Name': experiment_name,
    'Node Count': node_count,
    'Ranks Per Node': rank_count,
    'Thread Count': thread_count,
    'Width': width,
    'Height': height,
    'Event Density': event_density,
    'Ring Size': ring_size,
    'Time to Run (ns)': time_to_run,
    'Small Payload (bytes)': small_payload,
    'Large Payload (bytes)': large_payload,
    'Large Event Fraction': large_event_fraction,
    'Imbalance Factor': imbalance_factor,
    "Component Size": component_size
  }


def extract_failure_reason(sbatch_output):
  """
  Extract the failure reason from the sbatch output file.
  """
  if not os.path.exists(sbatch_output):
    return "No sbatch output file found."

  with open(sbatch_output, 'r') as f:
    lines = f.readlines()
  
  if "DUE TO TIME LIMIT" in lines[-1]:
    return "Timeout"
  else:
    return "Other Failure"
  

def extract_row(results_dir):
  try:
    parameters = extract_parameters(results_dir)
    time_data = extract_time_data(results_dir)
    sync_data = extract_sync_data(results_dir)
  except Exception as e:

    #print(f"Error extracting data from {results_dir}. Skipping this directory.")

    return None
  
  return parameters | time_data | sync_data
