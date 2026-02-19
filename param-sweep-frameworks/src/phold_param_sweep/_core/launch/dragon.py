from __future__ import annotations

import collections.abc as c_abc
import dataclasses
import itertools
import logging
import os
import pathlib
import time
import typing as t

from phold_param_sweep.errors import (
    MissingOptionalDependencyError,
    ResourcesUnavailbleException,
)
from phold_param_sweep.param_set import SSTParamSet

try:
    import dragon
    from dragon.globalservices.node import get_list as _untyped_get_node_id_list
    from dragon.infrastructure.facts import PMIBackend
    from dragon.infrastructure.policy import Policy
    from dragon.native.machine import Node, cpu_count
    from dragon.native.process import ProcessTemplate
    from dragon.native.process_group import ProcessGroup
    from dragon.workflows.batch import Batch
except ImportError as e:
    raise MissingOptionalDependencyError.requires_optional("Dragon", "dragon") from e

if t.TYPE_CHECKING:
    from types import TracebackType

_LOGGER = logging.getLogger(__name__)

_NodeID = t.NewType("_NodeID", int)
_CPUID = t.NewType("_CPUID", int)
_NumProcs = t.NewType("_NumProcs", int)
_AwaitNextCompletionStrategyType: t.TypeAlias = c_abc.Callable[
    [c_abc.Collection[ProcessGroup]], ProcessGroup
]


class _NodeLike(t.Protocol):
    """Stub for `dragon.native.machine.Node` to type check against"""

    @property
    def hostname(self) -> _NodeID: ...
    @property
    def num_cpus(self) -> int: ...
    @property
    def cpus(self) -> list[_CPUID]: ...


class ProcessGroupLaunch:
    def __init__(
        self,
        sst: str | os.PathLike[str],
        simulation: str | os.PathLike[str],
        awaiter: _AwaitNextCompletionStrategyType | None = None,
    ) -> None:
        self._sst: t.Final = pathlib.Path(sst)
        self._simulation: t.Final = pathlib.Path(simulation)
        self._available: t.Final = set(_get_node_id_list())
        self._running: t.Final = dict[ProcessGroup, tuple[_NodeID, ...]]()
        self._awaiter: t.Final = (
            awaiter if awaiter is not None else _poll_awaiter(interval=10)
        )

    @property
    def _all_nodes(self) -> set[_NodeID]:
        return self._nodes_in_use | self._available

    @property
    def _nodes_in_use(self) -> set[_NodeID]:
        return set(itertools.chain.from_iterable(self._running.values()))

    def __enter__(self) -> t.Self:
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> t.Literal[False]:
        self.join()
        return False

    def launch(self, param: SSTParamSet) -> None:
        pg = ProcessGroup(restart=False, pmi=PMIBackend.CRAY)
        nodes = self._get_available_nodes(
            param.node_count,
            (_cpu_count_filter(param.ranks_per_node * param.threads_per_rank),),
        )

        def on_avail_nodes(param: SSTParamSet) -> list[tuple[_NumProcs, Policy]]:
            return _strict_placement_with_affinity(param, avail_nodes=nodes)

        for nproc, tmpl in _to_templates(
            self._sst, self._simulation, param, on_avail_nodes
        ):
            pg.add_process(nproc=nproc, template=tmpl)
        pg.init()
        pg.start()
        self._running[pg] = tuple(nodes)

    def join(self) -> None:
        for pg in list(self._running):
            self._join_process_group(pg, err_on_missing=False)

    def _get_available_nodes(
        self,
        num: int,
        filters: c_abc.Collection[c_abc.Callable[[_NodeLike], bool]] = (),
    ) -> list[_NodeID]:
        nodes = self._all_nodes
        if num > len(nodes):
            raise ValueError(f"Cannot request more than {len(nodes)}")

        def is_qualified(node: _NodeID) -> bool:
            return all(f(_to_nodelike(node)) for f in filters)

        def qualified(nodes: c_abc.Iterable[_NodeID]) -> c_abc.Iterable[_NodeID]:
            return filter(is_qualified, nodes)

        if num > len(list(qualified(nodes))):
            raise ValueError(f"Cannot find {num} nodes that meet qualifications")

        while True:
            avail_nodes = list(qualified(self._available))
            if len(avail_nodes) >= num:
                avail_nodes = avail_nodes[:num]
                self._available -= set(avail_nodes)
                return avail_nodes
            pg = self._await_next_completed()
            if pg is None:
                raise RuntimeError(
                    "Unexpectedly could not find a set of available nodes"
                )
            self._join_process_group(pg)

    def _await_next_completed(self) -> ProcessGroup | None:
        return self._awaiter(running) if (running := self._running) else None

    def _join_process_group(self, pg: ProcessGroup, *, err_on_missing: bool = True) -> None:
        nodes = self._running.pop(pg, None)
        if nodes is None:
            msg = f"Process Group is not tracked by {type(self).__name__}"
            if err_on_missing:
                raise ValueError(msg)
            else:
                _LOGGER.warning(msg)
                return
        try:
            pg.join()
        except Exception as e:
            _LOGGER.error("Process Group failed to join with exception: %s", str(e))
            _LOGGER.debug(
                "Hint: Use the `dragon-cleanup` command to collect running processes"
            )
        else:
            for id_, err in pg.exit_status:
                if err != 0:
                    _LOGGER.warning("Process %d failed with status code: %d", id_, err)
            for node in nodes:
                self._available.add(node)
        finally:
            pg.close()


def _poll_awaiter(interval: int) -> _AwaitNextCompletionStrategyType:
    def await_(
        pgs: c_abc.Collection[ProcessGroup], timeout: int | None = None
    ) -> ProcessGroup:
        if not pgs:
            raise ValueError("No process groups provided to await")

        if timeout is not None:
            start = time.perf_counter()

            def should_poll() -> bool:
                return time.perf_counter() - start <= timeout

        else:

            def should_poll() -> bool:
                return True

        while should_poll():
            for pg in pgs:
                if not pg.puids:
                    return pg
            _LOGGER.debug("Polling for next completed process...")
            time.sleep(interval)
        raise TimeoutError("Failed to find a process group in time")

    return await_


@dataclasses.dataclass(frozen=True)
class NaiveBatchLaunch:
    sst: str | os.PathLike[str]
    simulation: str | os.PathLike[str]
    _process_templates: list[list[tuple[int, ProcessTemplate]]] = dataclasses.field(
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
        if not self._process_templates:
            return False

        num_nodes = len(_get_node_id_list())
        batch = Batch(pool_nodes=num_nodes)
        all_jobs = [
            batch.job(process_templates=tmpls) for tmpls in self._process_templates
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
        self._process_templates.append(
            _to_templates(self.sst, self.simulation, param, _as_ranks)
        )


def _to_templates(
    sst: str | os.PathLike[str],
    simulation: str | os.PathLike[str],
    param: SSTParamSet,
    to_policies: c_abc.Callable[[SSTParamSet], list[tuple[_NumProcs, Policy | None]]],
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


def _cpu_count_filter(n_cpus: int) -> c_abc.Callable[[_NodeLike], bool]:
    def _has_n_cpus(node: _NodeLike) -> bool:
        return node.num_cpus >= n_cpus

    return _has_n_cpus


def _strict_placement_with_affinity(
    param: SSTParamSet, *, avail_nodes: t.Collection[_NodeID] | None = None
) -> list[tuple[_NumProcs, Policy]]:
    avail_nodes = avail_nodes if avail_nodes is not None else _get_node_id_list()
    thread_count = param.ranks_per_node * param.threads_per_rank
    has_threads = _cpu_count_filter(thread_count)
    nodes_ = (_to_nodelike(id_) for id_ in avail_nodes)
    nodes = [node for node in nodes_ if has_threads(node)]
    if len(nodes) < param.node_count:
        raise ResourcesUnavailbleException(
            "Could not find nodes with requested number of threads: "
            f"requested {thread_count} threads/node"
        )
    nodes = nodes[: param.node_count]
    return [
        (
            _NumProcs(1),
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


def _as_ranks(param: SSTParamSet) -> list[tuple[_NumProcs, None]]:
    _LOGGER.warning(
        "Launching processes strictly by number of ranks. Dragon will launch the"
        " expected number number of ranks, but cannot guarantee that the ranks"
        " will be placed evenly across nodes."
    )
    _LOGGER.debug(
        "Hint: For more control over where processes are placed consider using %s",
        _strict_placement_with_affinity.__name__,
    )
    nproc = _NumProcs(param.ranks_per_node * param.node_count)
    return [(nproc, Policy(placement=Policy.Placement.ANYWHERE))]


def _to_nodelike(node_id: _NodeID) -> _NodeLike:
    """Wrap `dragon.native.machine.Node` constructor to type check against"""
    return Node(node_id)  # type: ignore[no-any-return]


def _get_node_id_list() -> list[_NodeID]:
    """Wrap `dragon.globalservices.node.get_list` to type check against"""
    return _untyped_get_node_id_list()  # type: ignore[no-any-return]
