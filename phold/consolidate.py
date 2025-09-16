
import pandas as pd
import numpy as np
import sys
import os

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


from extractors import extract_row, identify_result_dirs
import extractors

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
  
  with ProcessPoolExecutor(max_workers=8) as executor:
    data = list(executor.map(extract_row, result_dirs))

  failure_indices = [i for i, d in enumerate(data) if d is None]
  additional_failures = [result_dirs[i] for i in failure_indices]
  invalid_dirs += [(failure, 'Collection failure') for failure in additional_failures]

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


  failure_outfile = outfile.replace('.csv', '-failures.csv')
  print(f"Now consolidating failures into {failure_outfile}...")

  failure_data = []
  for dir_name, reason in invalid_dirs:
    srun_output_file = dir_name.replace('_dir', '.err')
    srun_output_path = os.path.join(dir_name, srun_output_file)
    reason = extractors.extract_failure_reason(srun_output_path)

    parameters = extractors.extract_parameters(dir_name)
    parameters['Status'] = reason
    failure_data.append(parameters)

  if len(failure_data) == 0:
    print("No failures found. Exiting.")
    sys.exit(0)
  with open(failure_outfile, 'w') as f:
    entry = failure_data[0]
    f.write(','.join(entry.keys()) + "\n")
    for entry in failure_data:
      f.write(','.join(map(str, entry.values())) + "\n")

  print(f"Failures consolidated into {failure_outfile}.")
