from __future__ import annotations

import collections.abc as c_abc
import dataclasses
import logging
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
    from dragon.native.machine import Node, cpu_count
    from dragon.native.process import ProcessTemplate
    from dragon.native.process_group import ProcessGroup
    from dragon.workflows.batch import Batch
except ImportError as e:
    raise MissingOptionalDependencyError.requires_optional(
        "dragon", "Failed to load Dragon launching strategy"
    ) from e

if t.TYPE_CHECKING:
    from types import TracebackType

_LOGGER = logging.getLogger(__name__)


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
        pg = ProcessGroup(restart=False, pmi=PMIBackend.CRAY)
        for nproc, tmpl in _to_templates(
            self.sst, self.simulation, param, _strict_placement_with_affinity
        ):
            pg.add_process(nproc=nproc, template=tmpl)
        pg.init()
        print("=" * 80)
        try:
            pg.start()
            pg.join()
        finally:
            pg.close()
        print("=" * 80)


@dataclasses.dataclass(frozen=True)
class NaiveBatchLaunch:
    sst: str | os.PathLike[str]
    simulation: str | os.PathLike[str]
    process_templates: list[list[tuple[int, ProcessTemplate]]] = dataclasses.field(
        default_factory=list, init=False
    )

    def __enter__(self) -> t.Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> t.Literal[False]:
        if not self.process_templates:
            return False

        num_nodes = len(get_node_id_list())
        batch = Batch(pool_nodes=num_nodes)
        all_jobs = [
            batch.job(process_templates=tmpls) for tmpls in self.process_templates
        ]

        try:
            batch.fence()
            for job in all_jobs:
                ret_codes = job.get()
                if any(ret_codes):
                    _LOGGER.error(
                        f"Job {job} exited with at least one nonzero exit code: "
                        f"{ret_codes}"
                    )
        finally:
            batch.close()
            batch.join()

        return False

    def launch(self, param: SSTParamSet) -> None:
        self.process_templates.append(
            _to_templates(self.sst, self.simulation, param, _as_ranks)
        )


def _to_templates(
    sst: str | os.PathLike[str],
    simulation: str | os.PathLike[str],
    param: SSTParamSet,
    to_policies: c_abc.Callable[[SSTParamSet], list[tuple[int, Policy | None]]],
) -> list[tuple[int, ProcessTemplate]]:
    sst = os.fspath(sst)
    simulation = os.fspath(simulation)
    args = (*param.sst_flags, simulation, "--", *param.simulation_flags)
    fmt_param_str = param.as_param_str(sep="_")
    out_file = f"{fmt_param_str}.out"
    err_file = f"{fmt_param_str}.err"

    def to_tmpl(policy: Policy | None) -> ProcessTemplate:
        # TODO: out and err here
        return ProcessTemplate(policy=policy, target=sst, args=args)

    return [(n_proc, to_tmpl(pol)) for n_proc, pol in to_policies(param)]


def _strict_placement_with_affinity(param: SSTParamSet) -> list[tuple[int, Policy]]:
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
        (
            1,
            Policy(
                placement=Policy.Placement.HOST_NAME,
                host_name=node.hostname,
                cpu_affinity=node.cpus[
                    i * param.threads_per_rank : (i + 1) * param.threads_per_rank
                ],
            ),
        )
        for node in nodes
        for i in range(param.ranks_per_node)
    ]


def _as_ranks(param: SSTParamSet) -> list[tuple[int, None]]:
    _LOGGER.warning(
        "Launching processes strictly by number of ranks. Dragon will launch the"
        " expected number number of ranks, but cannot guarantee that the ranks"
        " will be placed evenly across nodes."
    )
    _LOGGER.debug(
        "Hint: For more control over where processes are placed consider using %s",
        _strict_placement_with_affinity.__name__,
    )
    nproc = param.ranks_per_node * param.node_count
    return [(nproc, Policy(placement=Policy.Placement.ANYWHERE))]
