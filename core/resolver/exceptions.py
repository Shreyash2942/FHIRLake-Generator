from __future__ import annotations


class ResolverError(RuntimeError):
    """Base error for resolver failures."""


class InvalidInputKeyError(ResolverError):
    """Raised when a required_inputs key cannot be mapped to a resource type."""


class MissingDependencyError(ResolverError):
    """Raised when required dependency IDs are missing and policy=ERROR."""


class AutoCreateDependencyError(ResolverError):
    """
    Raised when policy=AUTO_CREATE and required dependency IDs are missing.

    Orchestrator can catch this and create the missing dependency resource(s),
    then retry resolution.
    """

    def __init__(self, resource_type: str, message: str | None = None):
        self.resource_type = resource_type
        super().__init__(
            message or f"Missing dependency resources for '{resource_type}' (AUTO_CREATE)."
        )
