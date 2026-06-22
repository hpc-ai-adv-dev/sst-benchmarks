# SST Experimental Tooling Design

## Overview

This document outlines a pragmatic tooling approach that builds upon our current
foundation while providing essential automation for repeatable experiments,
data collection, and analysis.

## Key Usage Scenarios

- Users should be able to run a weak scaling study for phold and a strong
  scaling study for pingpong from the same tool.
- Parameters specific to each component (SST, Slurm, benchmark) should be
  captured with the results to support reproducibility.
- Users should be able to run the same experiments on different execution
  environments (host, container, e4s-cl).
- Users should be able to run parameter sweeps for all benchmarks, along
  with sweeping certain Slurm and SST parameters.
- Users should be able to run single experiments with specific parameters.
- Users should be able to run stochastic sampling of parameter spaces where
  applicable.
- Users should be able to easily compare and analyze results from different
  studies.
- The tool should have a user configuration file to define SST installations
  and container images with paths and version numbers of SST.
- The tool should optionally include studying the cost of adding in one or
  more checkpoints and, if so, also the option to request studying the cost
  of restoring from a checkpoint.
- The tool should accommodate running parameter sweeps for all the
  benchmarks.
- The tool should also allow users to run single experiments with specific
  parameters.
- The tool should support stochastic sampling of parameter spaces where
  applicable.
- The tool should provide a clear and consistent output format for all
  experiment results, making it easy to compare and analyze different
  studies.
- Should support extracting data from experiment logs and generating summary
  statistics and visualizations.


## Design Philosophy

### Maintainability First

- Prefer reusable, extendable classes in Python over shell scripts.
- Do not hardcode values; use configuration files for test parameters.
- Prefer YAML and CSV over databases for flexibility.
- Keep the code modular and try to lift out common functionality.

### Benchmark Agnostic

- Provide a unified interface for multiple benchmarks (pingpong, phold,
  gameoflife) while allowing benchmark-specific parameterization through config
  files that set up the experiment.

### Automated Experimentation

- Automate the entire experiment lifecycle from configuration generation,
  execution, data collection, to analysis and visualization.

### Auditable and Reproducible

- Ensure all configurations, code versions, and results are logged and
  easily traceable to support reproducibility.

### Centralized Configuration

- Use a single YAML configuration file to define all experiment parameters,
  including benchmark settings, execution environments, and analysis options.

### Slurm Integration

- Integrate with Slurm for job scheduling and resource management.

### e4s-cl and Container Support

- Support running experiments in both native and containerized environments
  (e.g., e4s-cl, apptainer, docker/podman) to compare performance and ensure
  consistency.

### Monitoring and Logging

- Implement logging and monitoring to capture performance metrics and system
  states during experiments.
- Monitor and report on failed experiments, retries, etc.

### Data Flexibility

- Use human-readable YAML configurations and CSV data outputs to accommodate
  rapidly evolving data storage needs.

### Modular Components

- Design modular classes for configuration management, experiment execution,
  and data analysis to facilitate maintenance and future enhancements. Config
  files can control which modules are used., e.g., choice of data extraction and
  analysis methods.

### Extensibility

- Architect the tool to easily incorporate new benchmarks, execution
  environments, and analysis methods.

### User-Friendly

- Provide clear documentation and examples to help users get started quickly
  and understand advanced features.

### Directory Structure

- Organize the tooling with a clear directory structure separating source
  code, configurations, experiment result data, analysis output, and documentation.


## Considerations

- Should we include support for other tooling, like HPC Toolkit?
- Is there a configuration of `phold` that can be used to represent each of the
  existing benchmarks, and, if so, can we deprecate them?
- Should we support user-defined scripts to be executed pre- and
  post-experiment?