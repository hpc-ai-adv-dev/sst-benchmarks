# This file contains functions useful in notebook-only workflows for extracting results from PHOLD benchmark outputs.

import os
import humanfriendly
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def extract_failure_reason(output_filename):
  """
  Extract the failure reason from the srun output file.

  :arg: output_filename: The path to the srun output file. This should contain the output from srun as well as the output of the job
  """
  if not os.path.exists(output_filename):
    return "No output file found."

  with open(output_filename, 'r') as f:
    lines = f.readlines()
  
  for line in lines:
    if "DUE TO TIME LIMIT" in line:
      return "Timeout"
    elif "inet_connect" in line:
      return "Network Socket Failure"
    elif "LE resources not recovered during flow control. FI_CXI_RX_MATCH_MODE=[hybrid|software] is required" in line:
      return "Network Fabric Failure"
    elif 'MPICH ERROR' in line:
      return "MPI Failure"
    elif "DUE TO TASK FAILURE" in line:
      return "Out of Memory"

  return "Other Failure"

# Parse a single sync file. Helper function used by extract_sync_data to process files in parallel.
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
    """Extracts and consolidates per-thread synchronization time data
    """
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


# Extracts timing and memory usage data from log files from SST 15.0.0 runs.
def extract_time_data_eq15(result_dir, logfile_name='run.log'):
    """Extracts timing and memory usage data from log files from runs executed with SST version 15.0.0."""
    log_file = os.path.join(result_dir, logfile_name)
    with open(log_file, 'r') as f:
        lines = f.readlines()
        time_data = {}
        for line in lines:
            if 'Build time:' in line:
                time_data['Build Time (s)'] = float(
                    line.split(':')[1].strip().split()[0])
            elif 'Run loop time:' in line:
                time_data['Run Time (s)'] = float(
                    line.split(':')[1].strip().split()[0])
            elif 'Max Resident Set Size:' in line:
                time_data['Max Resident Set Size (bytes)'] = humanfriendly.parse_size(
                    line.split(':')[1].strip())
            elif 'Global Max RSS Size:' in line:
                time_data['Max Global Set Size (bytes)'] = humanfriendly.parse_size(
                    line.split(':')[1].strip())
    return time_data

# Extracts timing and memory usage data from log files from SST >15.0.0 runs.


def extract_time_data_g15(result_dir, logfile_name='run.log'):
  """Extracts timing and memory usage data from log files from runs executed with SST versions greater than 15.0.0."""
  log_file = os.path.join(result_dir, logfile_name)
  with open(log_file, 'r') as f:
    lines = f.readlines()
    time_data = {}
    for line in lines:
      if '├ ■ build' in line:
        # take the next line
        build_time_line = lines[lines.index(line) + 1]
        time_data['Build Time (s)'] = float(
            build_time_line.split(':')[1].strip().split()[0])
      elif '■ execute' in line:
        # take the next line
        run_time_line = lines[lines.index(line) + 1]
        time_data['Run Time (s)'] = float(
            run_time_line.split(':')[1].strip().split()[0])
      elif 'Max Resident Set Size:' in line:
         time_data['Max Resident Set Size (bytes)'] = humanfriendly.parse_size(
             line.split(':')[1].strip())
      elif 'Global Max RSS Size:' in line:
         time_data['Max Global Set Size (bytes)'] = humanfriendly.parse_size(
             line.split(':')[1].strip())
  return time_data

def extract_time_data(result_dir, version):
    if version == '15.0.0':
        return extract_time_data_eq15(result_dir)
    else:
        return extract_time_data_g15(result_dir)
    
def extract_parameters(result_dir):
  '''Extract parameters from the run name, which is the last part of the path
  '''
  run_name = os.path.basename(result_dir)
  parts = run_name.split('_')
  return {
      'Experiment Name': parts[0],
      'Node Count': int(parts[1]),
      'Ranks Per Node': int(parts[2]),
      'Threads Per Rank': int(parts[3]),
      'Width': int(parts[4]),
      'Height': int(parts[5]),
      'Event Density': float(parts[6]),
      'Ring Size': int(parts[7]),
      'Time to Run (ns)': int(parts[8]),
      'Small Payload (bytes)': int(parts[9]),
      'Large Payload (bytes)': int(parts[10]),
      'Large Event Fraction': float(parts[11]),
      'Imbalance Factor': float(parts[12]),
      'Component Size (bytes)': int(parts[13]) if len(parts) > 13 else 0,
      'Component Computations': int(parts[14]) if len(parts) > 14 else 0
  }

def extract_single_result(result_dir, sst_version, logfile_name='run.log'):
    """Extracts output results and run parameters from the result of a PHOLD simulation.
    
    This function assumes that the `result_dir` path has already been checked to be a valid result directory.
        Exceptions thrown during processing are assumed to indicate a invalid or incomplete run, and are to be 
        handled by the caller of this function.
    
    Args:
        result_dir: The path to the directory containing the results of a single PHOLD simulation run. 
            This directory should contain a log file with timing and memory usage data, as well as one
            or more synchronization files starting with 'rank'.
        sst_version: The version of SST used for the simulation run, which determines how timing data is extracted.
        logfile_name: The name of the log file to look for in the result directory. Default is 'run.log'.
        
    Returns:
        dict: A dictionary containing the extracted results and parameters.
    """
    parameters = extract_parameters(result_dir)
    time_data = extract_time_data(result_dir, sst_version)
    if len(time_data) != 4:
        raise ValueError(f"Expected to extract 4 time/memory data points, but got {len(time_data)}. Data: {time_data}")
    sync_data = extract_sync_data(result_dir)
    return {**parameters, **time_data, **sync_data, 'SST Version': sst_version}

def identify_result_dirs(search_dir, logfile_name, experiment_name=None):
    """ Identify directories containing result files.

    This function crawls the given `search_dir` for subdirectories that contain
        the necessary files for data extraction, specifically a log file with 
        the name specified by `logfile_name` and one or more synchronization files
        starting with 'rank'. If `experiment_name` is provided, only subdirectories
        whose names start with the given experiment name will be considered.

    Args:
        search_dir (str): The directory to search for result subdirectories.
        logfile_name (str): The name of the log file to look for in each subdirectory
        experiment_name (str, optional): If provided, only subdirectories starting with 
            this string will be considered. Default is None, meaning all subdirectories 
            will be considered.
    
    Returns:
        tuple: A tuple containing two lists:
            - valid_dirs: A list of subdirectory names that contain the necessary files for data extraction
            - invalid_dirs: A list of tuples, each containing a subdirectory name and a reason why 
                it was considered invalid (e.g., missing log file, missing sync files, etc.)
    """
    result_dirs = []
    invalid_dirs = []

    for candidate in os.listdir(search_dir):
        candidate_path = os.path.join(search_dir, candidate)

        # Skip non-directories
        if not os.path.isdir(candidate_path):
            continue
        # Skip if there's a experiment name filter and this candidate doesn't match
        if experiment_name is not None and not candidate.startswith(experiment_name):
            continue

        # Check for a log file and at least one sync file
        has_output_file = any(file.endswith('run.log') for file in os.listdir(candidate_path))
        has_rank_files = any(file.startswith('rank') for file in os.listdir(candidate_path))

        if not has_output_file:
            invalid_dirs.append((candidate, "Missing run.log file"))
        elif not has_rank_files:
            invalid_dirs.append((candidate, "Missing rank files"))
        else:
            result_dirs.append(candidate)
        
    return (result_dirs, invalid_dirs)

def extract_results(results_dir, sst_version, logfile_name='run.log', experiment_name=None):
    """Extracts PHOLD simulation results from a directory containing multiple run subdirectories.
    
    The `results_dir` argument should be the full path to a directory containing subdirectories for each simulation
        run. Each run subdirectory should be named according to the paremeter encoding sceme defined in `extract_parameters` and
        produced by the `generate_phold_args` function in the `submit.py` script. The run subdirectory should contain a file with 
        the same name as the `logfile_name` argument, by default `run.log`, as well as one or more `rank*.log` files containing 
        synchronization data.
    

    Args:
        results_dir (str): The path to the directory containing subdirectories for each simulation run.
        sst_version (str): The version of SST used for the runs, which determines how time data is extracted.
        logfile_name (str): The name of the log file to look for in each run subdirectory. Default is 'run.log'.
        experiment_name (str, optional): If provided, only subdirectories starting with this string will be processed. Default is None, meaning all subdirectories will be processed.
        
    Returns:
        tuple: A tuple containing two lists:
            - successes: A list of dictionaries, each containing extracted data for a successful run.
            - failures: A list of dictionaries, each containing parameters and failure reasons for failed runs."""
    successes = []
    failures = []
    valid_dirs, invalid_dirs = identify_result_dirs(results_dir, logfile_name, experiment_name=experiment_name)
    
    # Process the valid dirs, if there's a problem, add to the invalid dirs
    for valid_dir in valid_dirs:
        try:
            result_dir = os.path.join(results_dir, valid_dir)
            result = extract_single_result(result_dir, sst_version, logfile_name=logfile_name)
            result['Status'] = 'Success'
            successes.append(result)
        except Exception as e:
            invalid_dirs.append((valid_dir, f"Error during data extraction: {e}"))
            
    for (invalid_dir, reason) in invalid_dirs:
        parameters = extract_parameters(os.path.join(results_dir, invalid_dir))
        output_filepath = os.path.join(results_dir, invalid_dir, logfile_name)
        if os.path.exists(output_filepath):
            reason = extract_failure_reason(output_filepath)
        parameters.update({'Status': 'Failure', 'Failure Reason': reason, 'SST Version': sst_version})
        failures.append(parameters)
    return successes, failures