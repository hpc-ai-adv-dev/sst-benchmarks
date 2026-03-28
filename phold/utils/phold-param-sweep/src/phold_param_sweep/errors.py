from __future__ import annotations

import typing as t


class ResourcesUnavailbleException(Exception):
    """Could not obtain resources to honnor a launch request"""


class MissingOptionalDependencyError(ImportError):
    "An optional dependency is missing"

    @classmethod
    def requires_optional(cls, group: str, msg: str) -> t.Self:
        return cls(
            f"{msg}: "
            f"You should be able to fix this by installing the `{group}` "
            "optional dependencies: "
            f"`pip install pysubmit[{group}]`"
        )
