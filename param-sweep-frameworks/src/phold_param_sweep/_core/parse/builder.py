from __future__ import annotations

import collections.abc as c_abc
import typing as t

if t.TYPE_CHECKING:
    import argparse

    from phold_param_sweep._core.parse.strategies import SweepStrategy


_TBoundArgType = t.TypeVar("_TBoundArgType", int, float)


class ParamSweepParserBuilder:
    def __init__(
        self,
        parser: argparse.ArgumentParser,
        sweep_strategies: dict[
            str, c_abc.Callable[[argparse.ArgumentParser], SweepStrategy]
        ],
    ) -> None:
        self._parser = parser
        subparsers = parser.add_subparsers(required=True, dest="strategy")
        self._strategies = [
            init(subparsers.add_parser(name)) for name, init in sweep_strategies.items()
        ]
        self._sweep_param_aggregators = {
            name: type(s).parse_namespace
            for name, s in zip(sweep_strategies, self._strategies)
        }
        self._sweep_params: list[str] = []

    def add_sweep_param(
        self,
        name: str,
        prefix: str,
        description: str,
        type_: type[_TBoundArgType],
        default: _TBoundArgType | None = None,
    ) -> t.Self:
        prefix = prefix.lower().replace(" ", "-")
        dest = prefix.replace("-", "_")
        self._sweep_params.append(dest)
        for strat in self._strategies:
            strat.add_sweep_param(
                name, prefix, dest, description, type_, default=default
            )
        return self

    def parse_sweep_params(
        self, args: c_abc.Sequence[str] | None = None
    ) -> list[dict[str, t.Any]]:
        _, sweeps = self.parse_params(args)
        return sweeps

    def parse_params(
        self, args: c_abc.Sequence[str] | None = None
    ) -> tuple[argparse.Namespace, list[dict[str, t.Any]]]:
        ns = self._parser.parse_args(args)
        aggregator = self._sweep_param_aggregators.get(ns.strategy)
        if aggregator is None:
            raise ValueError("Failed to look up sweep aggregation strategy")
        return ns, aggregator(ns, self._sweep_params)
