import dataclasses
import logging
import os
import typing as t
from types import TracebackType

from phold_param_sweep.param_set import SSTParamSet

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class DryRunLaunch:
    sst: str | os.PathLike[str]
    simulation: str | os.PathLike[str]

    def __enter__(self) -> t.Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> t.Literal[False]:
        return False

    def launch(self, param: SSTParamSet) -> None:
        _LOGGER.info("=" * 80)
        _LOGGER.info(
            " ".join(
                (
                    "srun",
                    "-N",
                    str(param.node_count),
                    "--ntasks-per-node",
                    str(param.ranks_per_node),
                    "--cpus-per-task",
                    str(param.threads_per_rank),
                    os.fspath(self.sst),
                    *param.sst_flags,
                    os.fspath(self.simulation),
                    "--",
                    *param.simulation_flags,
                )
            )
        )
        _LOGGER.info("=" * 80)
