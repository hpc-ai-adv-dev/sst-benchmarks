from __future__ import annotations

import dataclasses
import os
import typing as t

from phold_param_sweep.errors import (
    MissingOptionalDependencyError,
    ResourcesUnavailbleException,
)
from phold_param_sweep.param_set import SSTParamSet

try:
    import dragon
    from dragon.globalservices.node import get_list as get_node_id_list
    from dragon.infrastructure.facts import PMIBackend
    from dragon.infrastructure.policy import Policy
    from dragon.native.machine import Node
    from dragon.native.process import ProcessTemplate
    from dragon.native.process_group import ProcessGroup
except ImportError as e:
    raise MissingOptionalDependencyError.requires_optional(
        "dragon", "Failed to load Dragon launching strategy"
    ) from e

if t.TYPE_CHECKING:
    from types import TracebackType


@dataclasses.dataclass(frozen=True)
class ProcessGroupLaunch:
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
        converter = _ProcessConverter(
            sst=self.sst,
            # TODO: need a way to set/edit this
            simulation=self.simulation,
            param=param,
        )
        pg = converter.to_process_group()
        pg.init()
        try:
            pg.start()
            pg.join()
        finally:
            pg.close()


@dataclasses.dataclass(frozen=True)
class _ProcessConverter:
    sst: str | os.PathLike[str]
    simulation: str | os.PathLike[str]
    param: SSTParamSet

    def _to_templates(self) -> list[ProcessTemplate]:
        param = self.param
        fmt_param_str = param.as_param_str(sep="_")
        out_file = f"{fmt_param_str}.out"
        err_file = f"{fmt_param_str}.err"
        sst = os.fspath(self.sst)
        simulation = os.fspath(self.simulation)

        def to_tmpl(policy: Policy) -> ProcessTemplate:
            return ProcessTemplate(
                policy=policy,
                target=sst,
                args=(
                    *param.sst_flags,
                    simulation,
                    "--",
                    *param.simulation_flags,
                ),
                # TODO: out and err here
            )

        return list(map(to_tmpl, self._to_policies()))

    def _to_policies(self) -> list[Policy]:
        param = self.param
        thread_count = param.ranks_per_node * param.threads_per_rank
        nodes_ = (Node(id_) for id_ in get_node_id_list())
        nodes = [node for node in nodes_ if node.num_cpus >= thread_count]
        if len(nodes) < param.node_count:
            raise ResourcesUnavailbleException(
                "Could not find nodes with requested number of threads: "
                f"requested {thread_count} threads/node"
            )
        nodes = nodes[: param.node_count]
        return [
            Policy(
                placement=Policy.Placement.HOST_NAME,
                host_name=node.hostname,
                cpu_affinity=node.cpus[
                    i * param.threads_per_rank : (i + 1) * param.threads_per_rank
                ],
            )
            for node in nodes
            for i in range(param.ranks_per_node)
        ]

    def to_process_group(self) -> ProcessGroup:
        pg = ProcessGroup(restart=False, pmi=PMIBackend.CRAY)
        for tmpl in self._to_templates():
            pg.add_process(nproc=1, template=tmpl)
        return pg
