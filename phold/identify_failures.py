import sys
import extractors


if len(sys.argv) != 3:
    print("Usage: python identify_failures.py <output file> <experiment_name>")
    sys.exit(1)

output_file = sys.argv[1]
experiment_name = sys.argv[2]

(successes_dirs, invalid_dirs) = extractors.identify_result_dirs(experiment_name)


data = []
for dir_name, reason in invalid_dirs:
  sbatch_output = dir_name.replace('_dir', '.out')
  reason = extractors.extract_failure_reason(sbatch_output)

  parameters = extractors.extract_parameters(dir_name)
  parameters['Status'] = reason
  data.append(parameters)

if len(data) == 0:
    print("No failures found. Exiting.")
    sys.exit(0)
with open(output_file, 'w') as f:
  entry = data[0]
  f.write(','.join(entry.keys()) + "\n")
  for entry in data:
    f.write(','.join(map(str, entry.values())) + "\n")


print(f"Failures consolidated into {output_file}.")