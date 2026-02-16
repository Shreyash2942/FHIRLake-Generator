# Core/planning/builder.py
from __future__ import annotations

from typing import Optional

from .models import UserRequest, ExecutionPlan
from .planner import build_plan
from .exceptions import PlanningError


class ExecutionPlanBuilder:
    """
    Thin builder facade (future-proof hook).

    Today: delegates to build_plan().
    Later: can grow to support previews, cost estimation, sharding, etc.
    """

    def __init__(self, registry):
        self._registry = registry
        self._request: Optional[UserRequest] = None

    def with_request(self, request: UserRequest) -> "ExecutionPlanBuilder":
        self._request = request
        return self

    def build(self) -> ExecutionPlan:
        if self._request is None:
            raise PlanningError("UserRequest must be provided before build().")
        return build_plan(self._request, self._registry)
