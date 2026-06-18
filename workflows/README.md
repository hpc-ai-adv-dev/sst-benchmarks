# SST Workflow Notebooks

This directory contains example Jupyter-notebook based workflows that run SST
PHOLD experiments on an HPC system using Apptainer containers and Slurm.  Over
time we may expand or reorganize this directory. In the meantime, the current
set of notebooks are structured similiarly with the following sections:

1. **Configuration**: set global parameters, initialize logging/working directories, downloads containers and and downloads and builds benchmarks.
2. **Run**: launch SST jobs with output from each job will be stored in sperate run log files.
3. **Preprocess**: extract timing and memory metrics from the run logs into CSV files.
4. **Plot**: generate experiment-specific plots from the CSV data.

## Notebooks in this directory

- [scale_model_size.ipynb](scale_model_size.ipynb): on a single node, scale the model size (number of components).
- [weak_scaling.ipynb](weak_scaling.ipynb): runs weak scaling (fixed model-size per node with increasing node counts).
- [checkpointing.ipynb](checkpointing.ipynb): on a single node, generates baseline, checkpoint, and restore runs.

## How to run these workflows

I run these workflows from the login node of a CrayEX system that has slurm.  I use vscode locally on my laptop to make a remote connection to the supercomputer and load the notebook stored there.  I have the vscode Jupyter notebook extension installed remotely there as well and vscode has helpfully installed it remotely for me.

## Workflow configuration

All three notebooks expose top-level controls in a "global params" cell near the top of the notebook.  For details, refer to the cell in the individual notebooks, but some some common relevant parameters include:

- `container_url`: SST container image URI to convert/download.
- `benchmarkRepos` and `benchmarkPath`: benchmark source location.
- `additional_srun_args`: extra arguments to pass to Slurm. This may be useful to specify job queues or priorities. 
- `force`: a list indicating when certain configuration steps should be forced to rerun (e.g. force re-downloading containers even if they've previously been downloaded).

Valid `force` values include:

- `ALL`
- `DOWNLOAD_CONTAINERS`
- `DOWNLOAD_BENCHMARKS`
- `BUILD_BENCHMARKS`

See comments in the individual notebooks for specific details.

## Helper module behavior

Common logic lives in `utils/workflows.py`:

- Job launch and log streaming (`launch_and_log_sst`).
- Queue watcher widget (`watch_queue_widget`).
- SST output extraction via regex (`extract_sst_output_in_files`).
- CSV normalization, including byte-unit conversion to bytes (`convert_to_csv`).

CSV convention:

- First column is `Size` parsed from log file names matching `size_<number>`. For single node workflows this number corresponds to the model size (i.e. number of componets). For multi node workflows this number is the number of nodes.
- Remaining columns correspond to parsed SST timing/memory fields.