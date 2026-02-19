from __future__ import annotations

import os
import typing as t

from phold_param_sweep.errors import MissingOptionalDependencyError
from phold_param_sweep.param_set import SSTParamSet

try:
    from smartsim.experiment import Experiment
except ImportError as e:
    raise MissingOptionalDependencyError.requires_optional(
        "smartsim", "Failed to load SmartSim launching strategy"
    ) from e

if t.TYPE_CHECKING:
    from types import TracebackType


class SmartSimBatchLaunch:
    def __init__(
        self, sst: str | os.PathLike[str], simulation: str | os.PathLike[str]
    ) -> None:
        self._exp = Experiment("sst-param-sweep", launcher="auto")
        self._sst = sst
        self._simulation = simulation

    def __enter__(self) -> t.Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> t.Literal[False]:
        self._exp.poll()
        self._exp.summary()
        return False

    def launch(self, param: SSTParamSet) -> None:
        rs = self._exp.create_run_settings(
            exe=os.fspath(self._sst),
            exe_args=[
                *param.sst_flags,
                os.fspath(self._simulation),
                "--",
                *param.simulation_flags,
            ],
        )
        rs.set_nodes(param.node_count)
        rs.set_tasks_per_node(param.ranks_per_node)
        rs.set_cpus_per_task(param.threads_per_rank)
        # Optional: Bind threads to cores?
        # bindings = list(range(param.ranks_per_node * param.threads_per_rank))
        # rs.set_cpu_bindings(bindings)

        bs = self._exp.create_batch_settings()
        bs.set_nodes(param.node_count)

        model = self._exp.create_model(
            name=param.as_param_str(), run_settings=rs, batch_settings=bs
        )
        self._exp.generate(model)
        self._exp.start(model, block=False)
