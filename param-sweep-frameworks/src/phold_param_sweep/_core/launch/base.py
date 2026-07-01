import contextlib
import typing as t

from phold_param_sweep.param_set import SSTParamSet

LaunchContext: t.TypeAlias = "contextlib.AbstractContextManager[LaunchStrategy]"


class LaunchStrategy(t.Protocol):
    def launch(self, param: SSTParamSet) -> None: ...
