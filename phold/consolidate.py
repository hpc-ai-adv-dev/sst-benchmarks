
import pandas as pd
import numpy as np
import sys
import os

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


from extractors import extract_row, identify_result_dirs

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
