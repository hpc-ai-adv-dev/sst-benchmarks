from __future__ import annotations

import typing as t


class ResourcesUnavailbleException(Exception):
    """Could not obtain resources to honnor a launch request"""


class StrategyLoadError(Exception):
    def __init__(self, strategy: str, reason: str) -> None:
        super().__init__(f"Failed to load {strategy} launching strategy: {reason}")


class MissingOptionalDependencyError(StrategyLoadError):
    "An optional dependency is missing"

    @classmethod
    def requires_optional(cls, strategy: str, group: str) -> t.Self:
        return cls(
            strategy=strategy,
            reason=(
                f"You should be able to fix this by installing the `{group}` "
                "optional dependencies: "
                f"`pip install phold-param-sweep[{group}]`"
            ),
        )
