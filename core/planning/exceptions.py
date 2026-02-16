# Core/planning/exceptions.py

class PlanningError(Exception):
    """Base class for all planning-related errors."""


class UnknownResourceTypeError(PlanningError):
    """Raised when a requested resource type is not present in the registry."""
    pass


class DependencyCycleError(PlanningError):
    """Raised when a dependency cycle is detected during planning."""
    pass


class InvalidCountsError(PlanningError):
    """Raised when counts violate dependency rules (e.g. child > 0 but parent = 0)."""
    pass
