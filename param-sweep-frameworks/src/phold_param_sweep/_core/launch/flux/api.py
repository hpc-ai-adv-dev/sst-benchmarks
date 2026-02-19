from __future__ import annotations

import collections.abc as c_abc
import contextlib
import dataclasses
import logging
import os
import shlex
import shutil
import subprocess
import sys
import textwrap
import typing as t

from phold_param_sweep.errors import MissingOptionalDependencyError, StrategyLoadError
from phold_param_sweep.param_set import SSTParamSet

if t.TYPE_CHECKING:
    from types import TracebackType


def _get_flux_version() -> str:
    flux_path = shutil.which("flux")
    if flux_path is None:
        raise FileNotFoundError("Could not find a `flux` executable")
    proc = subprocess.run((flux_path, "version"), stdout=subprocess.PIPE)
    lines = proc.stdout.decode("utf-8").splitlines()
    words = (line.split() for line in lines)
    words = (ws for ws in words if len(ws) == 2)
    versions = [vers for tool, vers in words if tool == "commands:"]
    if proc.returncode or len(versions) != 1:
        raise ValueError("Found `flux` but failed to parse flux version number")
    return versions[0]


try:
    import flux
    import flux.job
except ImportError as e:
    try:
        version = _get_flux_version()
    except Exception as e_msg:
        raise StrategyLoadError("Flux", str(e_msg)) from e
    raise MissingOptionalDependencyError(
        "Flux",
        textwrap.dedent(f"""\
            Could not import `flux`!

                Hint: Consider installing the correct bindings from PyPI? To
                install the correct bindings for your version of flux, try running
                the following command:

                {sys.executable} -m pip install flux-python=={version}
            """),
    ) from e


_LOGGER = logging.Logger(__name__)


@dataclasses.dataclass(frozen=True)
class ExecutorLauncher:
    executor: flux.job.FluxExecutor
    sst: str | os.PathLike[str]
    simulation: str | os.PathLike[str]

    @classmethod
    def default_executor(
        cls, sst: str | os.PathLike[str], simulation: str | os.PathLike[str]
    ) -> contextlib.AbstractContextManager[t.Self]:
        @contextlib.contextmanager
        def _impl() -> c_abc.Generator[t.Self, None, None]:
            with flux.job.FluxExecutor() as executor:
                yield cls(executor, sst, simulation)

        return _impl()

    def launch(self, param: SSTParamSet) -> None:
        sst = os.fspath(self.sst)
        sim = os.fspath(self.simulation)

        _LOGGER.warning(
            "Flux does not allow `--tasks-per-node` and `--cores-per-task` at"
            " the same time. Setting the total number of ranks to match the"
            " expected total number of ranks, but cannot guarantee that flux"
            " places them evenly across nodes."
        )

        self.executor.submit(
            flux.job.JobspecV1.from_command(
                [sst, *param.sst_flags, sim, "--", *param.simulation_flags],
                exclusive=True,
                num_nodes=param.node_count,
                num_tasks=param.node_count * param.ranks_per_node,
                cores_per_task=param.threads_per_rank,
            )
        )
