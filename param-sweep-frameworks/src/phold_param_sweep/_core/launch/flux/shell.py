from __future__ import annotations

import collections.abc as c_abc
import dataclasses
import logging
import os
import shlex
import shutil
import subprocess
import textwrap
import typing as t

from phold_param_sweep.param_set import SSTParamSet

if t.TYPE_CHECKING:
    from types import TracebackType


_LOGGER = logging.Logger(__name__)


@dataclasses.dataclass(frozen=True)
class BulkSubmit:
    sst: str | os.PathLike[str]
    simulation: str | os.PathLike[str]
    _params: list[SSTParamSet] = dataclasses.field(init=False, default_factory=list)

    def __enter__(self) -> t.Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> t.Literal[False]:
        def esc_args(args: c_abc.Sequence[str]) -> str:
            return shlex.quote(shlex.join(args))

        flux = "flux" if (path := shutil.which("flux")) is None else os.fspath(path)
        sst = os.fspath(self.sst)
        sim = os.fspath(self.simulation)

        _LOGGER.warning(
            "Flux does not allow `--tasks-per-node` and `--cores-per-task` at"
            " the same time. Setting the total number of ranks to match the"
            " expected total number of ranks, but cannot guarantee that flux"
            " places them evenly across nodes."
        )

        params = (
            (
                str(p.node_count),
                str(p.ranks_per_node * p.node_count),  # See warning above
                str(p.threads_per_rank),
                esc_args(p.sst_flags),
                esc_args(p.simulation_flags),
            )
            for p in self._params
        )
        nodes, ranks, threads, sst_flags, sim_flags = map(" ".join, zip(*params))

        cmd = shlex.split(textwrap.dedent(f"""\
            {flux} bulksubmit
                --wait --nodes={{0}} --exclusive
                --ntasks={{1}} --cores-per-task={{2}}
                {sst} job-{{seq}} {{3}} {sim} -- {{4}}
            :::  {nodes}
            :::+ {ranks}
            :::+ {threads}
            :::+ {sst_flags}
            :::+ {sim_flags}"""))
        _LOGGER.debug("Bulk Submit Command: %s", shlex.join(cmd))
        subprocess.run(cmd, check=True)

        return False

    def launch(self, param: SSTParamSet) -> None:
        self._params.append(param)
