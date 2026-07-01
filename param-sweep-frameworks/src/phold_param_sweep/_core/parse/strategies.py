from __future__ import annotations

import abc
import argparse
import collections.abc as c_abc
import itertools
import random
import typing as t

import numpy as np

if t.TYPE_CHECKING:
    from argparse import _MutuallyExclusiveGroup as MutuallyExclusiveGroup

_T = t.TypeVar("_T")
_TBoundArgType = t.TypeVar("_TBoundArgType", int, float)


class SweepStrategy(abc.ABC):
    @t.final
    def __init__(self, subparser: argparse.ArgumentParser) -> None:
        type(self)._configure_subparser(subparser)
        self._subparser = subparser

    @classmethod
    def _configure_subparser(cls, subparser: argparse.ArgumentParser) -> None: ...

    @t.final
    def _make_xgroup(
        self, name: str, description: str, required: bool
    ) -> MutuallyExclusiveGroup:
        return self._subparser.add_argument_group(
            name, description
        ).add_mutually_exclusive_group(required=required)

    @t.final
    def add_sweep_param(
        self,
        name: str,
        prefix: str,
        dest: str,
        description: str,
        type_: type[_TBoundArgType],
        default: _TBoundArgType | None = None,
    ) -> None:
        if not name:
            raise ValueError("`name` cannot be empty")
        if not prefix:
            raise ValueError("`prefix` cannot be empty")
        if not dest:
            raise ValueError("`dest` cannot be empty")
        self._configure_sweep_param_group(
            self._make_xgroup(name, description, required=default is None),
            prefix,
            dest,
            type_,
            default=default,
        )

    @classmethod
    @abc.abstractmethod
    def _configure_sweep_param_group(
        cls,
        xgroup: MutuallyExclusiveGroup,
        prefix: str,
        dest: str,
        type_: type[_TBoundArgType],
        default: _TBoundArgType | None = None,
    ) -> None: ...

    @classmethod
    @abc.abstractmethod
    def parse_namespace(
        cls, ns: argparse.Namespace, dests: c_abc.Sequence[str]
    ) -> list[dict[str, t.Any]]: ...


class ProductSweepStrategy(SweepStrategy):
    @classmethod
    def _configure_sweep_param_group(
        cls,
        xgroup: MutuallyExclusiveGroup,
        prefix: str,
        dest: str,
        type_: type[_TBoundArgType],
        default: _TBoundArgType | None = None,
    ) -> None:
        xgroup.add_argument(
            f"--{prefix}-values",
            nargs="+",
            type=type_,
            help=f"List values to run with",
            dest=dest,
            default=None if default is None else cls.from_scalar(default),
        )
        xgroup.add_argument(
            f"--{prefix}-range",
            nargs="+",
            type=type_,
            help="Linspace of values to run with",
            action=cls.RangeAction,
            dest=dest,
        )

    @classmethod
    def parse_namespace(
        cls, ns: argparse.Namespace, dests: c_abc.Sequence[str]
    ) -> list[dict[str, t.Any]]:
        params = [getattr(ns, d) for d in dests]
        if not all(isinstance(p, list) for p in params):
            raise TypeError("Expected all parameters to be coerced to list")
        return [dict(zip(dests, p)) for p in itertools.product(*params)]

    @classmethod
    def from_scalar(cls, value: _TBoundArgType) -> list[_TBoundArgType]:
        return [value]

    @classmethod
    def from_range(
        cls,
        low: _TBoundArgType,
        high: _TBoundArgType,
        step: _TBoundArgType = 1,
    ) -> list[_TBoundArgType]:
        if isinstance(low, int) and isinstance(high, int) and isinstance(step, int):
            return list(range(low, high + step, step))
        if isinstance(low, float):
            return [float(x) for x in np.arange(low, high + step, step)]
        t.assert_never(low)
        t.assert_never(high)
        t.assert_never(step)

    class RangeAction(argparse.Action):
        def __init__(
            self,
            option_strings: c_abc.Sequence[str],
            dest: str,
            nargs: int | str | None = None,
            const: _T | None = None,
            default: _T | None = None,
            type: c_abc.Callable[[str], _T] | None = None,
            choices: c_abc.Iterable[_T] | None = None,
            required: bool = False,
            help: str | None = None,
            metavar: str | tuple[str, ...] | None = None,
            deprecated: bool = False,
        ) -> None:
            if nargs != argparse.ONE_OR_MORE:
                raise ValueError("Expected `nargs` to take one or more argument")
            super().__init__(
                option_strings=option_strings,
                dest=dest,
                nargs=nargs,
                const=const,
                default=default,
                type=type,
                choices=choices,
                required=required,
                help=help,
                metavar=metavar,
                # deprecated=deprecated,
            )

        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | c_abc.Sequence[t.Any] | None,
            option_string: str | None = None,
        ) -> None:
            if not isinstance(values, c_abc.Sequence):
                raise TypeError("Expected a sequence of values")
            if len(values) not in (2, 3):
                raise ValueError("Expected 2 or 3 values")
            typ_ = type(values[0])
            if not all(isinstance(v, typ_) for v in values):
                raise TypeError("Expected values be of uniform type")
            linspace = ProductSweepStrategy.from_range(*values)
            setattr(namespace, self.dest, linspace)


class SampleSweepStrategy(SweepStrategy):
    @classmethod
    def _configure_subparser(cls, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--num-samples", type=int, required=True)

    @classmethod
    def _configure_sweep_param_group(
        cls,
        xgroup: MutuallyExclusiveGroup,
        prefix: str,
        dest: str,
        type_: type[_TBoundArgType],
        default: _TBoundArgType | None = None,
    ) -> None:
        xgroup.add_argument(
            f"--{prefix}-fixed",
            nargs=1,
            type=type_,
            help="A fixed parameter value that will not be sampled",
            dest=dest,
            action=cls.ExpandAction,
            default=(None if default is None else cls.from_scalar(default)),
        )
        xgroup.add_argument(
            f"--{prefix}-bounds",
            nargs=2,
            type=type_,
            help="The bounds on which the parameter should be sampled from (inclusive)",
            action=cls.SampleAction,
            dest=dest,
        )

    @classmethod
    def parse_namespace(
        cls, ns: argparse.Namespace, dests: c_abc.Sequence[str]
    ) -> list[dict[str, t.Any]]:
        n = ns.num_samples
        params = [getattr(ns, d) for d in dests]
        if not isinstance(n, int):
            raise TypeError("Expected number of samples to be coerced to int")
        if not all(callable(p) for p in params):
            raise TypeError(
                "Expected all parameter generators to be coerced to callable"
            )
        return [dict(zip(dests, p)) for p in zip(*(fn(n) for fn in params))]

    @classmethod
    def from_scalar(
        cls, value: _TBoundArgType
    ) -> c_abc.Callable[[int], list[_TBoundArgType]]:
        return lambda n: [value for _ in range(n)]

    @classmethod
    def from_bounds(
        cls, low: _TBoundArgType, high: _TBoundArgType
    ) -> c_abc.Callable[[int], list[_TBoundArgType]]:
        if isinstance(low, int) and isinstance(high, int):
            return lambda n: [random.randint(low, high) for _ in range(n)]
        if isinstance(low, float):
            return lambda n: [random.uniform(low, high) for _ in range(n)]
        t.assert_never(low)
        t.assert_never(high)

    class SampleAction(argparse.Action):
        def __init__(
            self,
            option_strings: c_abc.Sequence[str],
            dest: str,
            nargs: int | str | None = None,
            const: _T | None = None,
            default: _T | None = None,
            type: c_abc.Callable[[str], _T] | None = None,
            choices: c_abc.Iterable[_T] | None = None,
            required: bool = False,
            help: str | None = None,
            metavar: str | tuple[str, ...] | None = None,
            deprecated: bool = False,
        ) -> None:
            if nargs != 2:
                raise ValueError("Expected `nargs` to be exactly 2")
            super().__init__(
                option_strings=option_strings,
                dest=dest,
                nargs=nargs,
                const=const,
                default=default,
                type=type,
                choices=choices,
                required=required,
                help=help,
                metavar=metavar,
                # deprecated=deprecated,
            )

        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | c_abc.Sequence[t.Any] | None,
            option_string: str | None = None,
        ) -> None:
            if not isinstance(values, c_abc.Sequence):
                raise TypeError("Expected a sequence of values")
            if len(values) != 2:
                raise ValueError("Expected 2 values")
            typ_ = type(values[0])
            low, high = sorted(values)
            if not (isinstance(low, typ_) and isinstance(high, typ_)):
                raise TypeError("Expected values be of uniform type")
            if not isinstance(low, float) or not isinstance(high, float):
                raise ValueError("Expected bounds to be a subtype of `float`")
            fn = SampleSweepStrategy.from_bounds(low, high)
            setattr(namespace, self.dest, fn)

    class ExpandAction(argparse.Action):
        def __init__(
            self,
            option_strings: c_abc.Sequence[str],
            dest: str,
            nargs: int | str | None = None,
            const: _T | None = None,
            default: _T | None = None,
            type: c_abc.Callable[[str], _T] | None = None,
            choices: c_abc.Iterable[_T] | None = None,
            required: bool = False,
            help: str | None = None,
            metavar: str | tuple[str, ...] | None = None,
            deprecated: bool = False,
        ) -> None:
            if nargs != 1:
                raise ValueError("Expected `nargs` to be exactly 1")
            super().__init__(
                option_strings=option_strings,
                dest=dest,
                nargs=nargs,
                const=const,
                default=default,
                type=type,
                choices=choices,
                required=required,
                help=help,
                metavar=metavar,
                # deprecated=deprecated,
            )

        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: str | c_abc.Sequence[t.Any] | None,
            option_string: str | None = None,
        ) -> None:
            if not isinstance(values, c_abc.Sequence):
                raise TypeError("Expected a sequence of values")
            if isinstance(values, str):
                raise TypeError("String is not a valid sequence")
            if len(values) != 1:
                raise ValueError("Expected 1 value")
            val: t.Any = values[0]  # Gotta lie to the type checker here
            fn = SampleSweepStrategy.from_scalar(val)
            setattr(namespace, self.dest, fn)
