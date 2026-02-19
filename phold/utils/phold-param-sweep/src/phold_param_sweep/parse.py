from __future__ import annotations

import argparse
import collections.abc as c_abc
import logging
import os
import pathlib
import shutil
import typing as t

from phold_param_sweep import errors as _errors
from phold_param_sweep._core.launch.dry_run import DryRunLaunch as _DryRunLaunch
from phold_param_sweep._core.parse import strategies as _strats
from phold_param_sweep._core.parse.builder import (
    ParamSweepParserBuilder as _ParamSweepParserBuilder,
)
from phold_param_sweep.param_set import SSTParamSet

if t.TYPE_CHECKING:
    from phold_param_sweep._core.launch.base import LaunchContext

_LAUNCH_METHODS: dict[
    str, c_abc.Callable[[pathlib.Path, pathlib.Path], LaunchContext]
] = {"dry-run": _DryRunLaunch}

_LOGGER = logging.getLogger(__name__)

try:
    from phold_param_sweep._core.launch.dragon import ProcessGroupLaunch as _PGLaunch
except _errors.MissingOptionalDependencyError as e:
    _LOGGER.warning(str(e))
else:
    _LAUNCH_METHODS["dragon-pg"] = _PGLaunch

try:
    from phold_param_sweep._core.launch.smartsim import (
        SmartSimBatchLaunch as _SSBatchLaunch,
    )
except _errors.MissingOptionalDependencyError as e:
    _LOGGER.warning(str(e))
else:
    _LAUNCH_METHODS["smartsim"] = _SSBatchLaunch


def parse_arguments() -> tuple[LaunchContext, c_abc.Iterable[SSTParamSet]]:
    parser = argparse.ArgumentParser(
        description="Submit PHOLD benchmark jobs using dragon"
    )

    parser.add_argument(
        "--launch-method",
        type=str,
        choices=_LAUNCH_METHODS,
        help="How to execute the parameter sweep.",
        required=True,
    )
    parser.add_argument(
        "--name",
        type=str,
        default="phold",
        help="Name of the benchmark job prepended to output files.",
    )
    parser.add_argument(
        "--simulation",
        type=pathlib.Path,
        help="Path to the phold benchmark script to sweep",
        required=True,
    )
    parser.add_argument(
        "--sst",
        type=pathlib.Path,
        help="Path to the sst binary to launch the parameter sweep with",
        default=None,
        required=False,
    )

    builder = (
        _ParamSweepParserBuilder(
            parser,
            {
                "product": _strats.ProductSweepStrategy,
                "sample": _strats.SampleSweepStrategy,
            },
        )
        .add_sweep_param(
            "Nodes", "node-count", "The number of nodes to with which to run.", int
        )
        .add_sweep_param(
            "Ranks",
            "ranks-per-node",
            "Number of MPI ranks to run per node. Default is 1.",
            int,
            default=1,
        )
        .add_sweep_param(
            "Threads",
            "threads-per-rank",
            "List of thread counts to use for the benchmark, e.g., '1 2 4'. Default is 1.",
            int,
            default=1,
        )
        .add_sweep_param(
            "Widths",
            "width",
            "List of widths to use for the benchmark, e.g., '100 200 250'."
            "The grid is distributed over this dimension.",
            int,
        )
        .add_sweep_param(
            "Heights",
            "height",
            "List of heights to use for the benchmark, e.g., '100 200 250'."
            "The grid is distributed over this dimension.",
            int,
        )
        .add_sweep_param(
            "Event Density",
            "event-density",
            "List of event densities to use for the benchmark, e.g., '0.1 0.5 10'.",
            float,
        )
        .add_sweep_param(
            "Time to Run",
            "time-to-run",
            "List of times to run the benchmark, in nanoseconds, e.g., '1 1000 2500'.",
            int,
        )
        .add_sweep_param(
            "Ring Size",
            "ring-size",
            "How many rings of neighboring components each component should"
            "connect to, e.g., '1 2 4'. Default is 1.",
            int,
            default=1,
        )
        .add_sweep_param(
            "Small Payload Size",
            "small-payload",
            "List of small payload sizes in bytes, e.g., '8 16 32'. Default is 8.",
            int,
            default=8,
        )
        .add_sweep_param(
            "Large Payload Size",
            "large-payload",
            "List of large payload sizes in bytes, e.g., '1024 2048 4096'. Default is 1024.",
            int,
            default=1024,
        )
        .add_sweep_param(
            "Large Event Fraction",
            "large-event-fraction",
            "List of fractions of large events, e.g., '0.1 0.2 0.5'. Default is 0.0.",
            float,
            default=0.0,
        )
        .add_sweep_param(
            "Imbalance Factor",
            "imbalance-factor",
            "List of imbalance fractions to use, e.g., '0.1 0.2 0.5'. Default is 0.0.",
            float,
            default=0.0,
        )
        .add_sweep_param(
            "Component Size",
            "component-size",
            "List of component sizes to use, in bytes. Default is 0.",
            int,
            default=0,
        )
    )
    ns, kws = builder.parse_params()

    sst: pathlib.Path | None = ns.sst
    if sst is None:
        sst = pathlib.Path(shutil.which("sst") or "sst")
    else:
        sst = sst.resolve()

    simulation: pathlib.Path = ns.simulation.resolve()
    if not simulation.is_file():
        raise FileNotFoundError(f"Could not find simulation `{os.fspath(simulation)}`")

    if (ctx := _LAUNCH_METHODS.get(ns.launch_method)) is None:
        # In theory unreachable if argparse does its job
        raise ValueError("Unknown action selected")

    return (ctx(sst, simulation), (SSTParamSet(name=ns.name, **kw) for kw in kws))
