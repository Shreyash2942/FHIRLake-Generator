# 🧠 Core Planning Module (FHIRLake Generator)

This module turns a **user selection** (resource types + counts) into a safe, deterministic **ExecutionPlan** that the orchestrator/runtime can execute without hardcoded rules.

Planning is **registry-driven**, meaning:
- It does **not** contain resource-specific logic (no “Patient / Encounter / Condition” hardcoding)
- All relationships come from `registry.get(resource_type).required_inputs`
- Adding new datasets/resources later requires **only** registry updates

---

## ✅ What Planning Produces

Planning builds an `ExecutionPlan` that includes:

- **expanded** resource set (user-selected + dependency-expanded resources)
- **order** (topologically sorted execution order)
- **counts** (final validated counts per resource type)
- **nodes** (per-resource metadata: dependencies, generator key, count)
- **run_id** and **created_at** metadata (used later by runtime + manifest)

---

## 📌 Key Responsibilities

### 1) Validate user selection
- Reject unknown resource types not present in the registry

### 2) Expand dependencies recursively
If a user selects `Condition`, the planner automatically expands:

Condition → Encounter → Patient

Final expanded set:
{Patient, Encounter, Condition}

### 3) Topological sort (execution order)
Produces a safe execution order such as:
Patient → Encounter → Condition

### 4) Validate counts using dependency rules
Rule enforced:
If count(X) > 0 and X depends on Y, then count(Y) must be > 0.

---

## 📁 Planning Module Structure

Core/planning/
- __init__.py        – Public exports
- models.py          – Data models
- planner.py         – Core planning logic
- builder.py         – Thin future-proof façade
- exceptions.py      – Custom planning errors
- README.md          – This file

```text
```text
Core/planning/                              # Planning engine (dependency expansion + ordering + validation)
    │
    ├── __init__.py                             # Public API exports (UserRequest, ExecutionPlan, build_plan, Builder)
    │                                          # Allows clean imports like: from Core.planning import build_plan
    │
    ├── models.py                               # Data models used by Planning
    │                                          # - UserRequest: user intent (selected resources + counts)
    │                                          # - PlanNode: per-resource execution metadata
    │                                          # - ExecutionPlan: immutable plan consumed by Runtime
    │
    ├── planner.py                              # Core planning logic (engine brain)
    │                                          # - validate user-selected resource types
    │                                          # - expand dependencies recursively via registry
    │                                          # - build dependency graph
    │                                          # - perform topological sort
    │                                          # - validate counts using dependency rules
    │                                          # - return ExecutionPlan
    │
    ├── builder.py                              # Thin future-proof façade over planner
    │                                          # - wraps build_plan()
    │                                          # - enables future multi-stage planning
    │                                          # - useful for GUI preview / plan inspection
    │                                          # - no business logic lives here
    │
    ├── exceptions.py                           # Custom Planning exceptions
    │                                          # - UnknownResourceTypeError
    │                                          # - DependencyCycleError
    │                                          # - InvalidCountsError
    │                                          # Keeps error handling explicit and readable
    │
    └── README.md                               # Planning module documentation
                                               # - explains responsibilities, flow, API, and examples
                                               # - documents registry contract and future-proof design

```

---

## 🧱 Main Public API

build_plan(req, registry) -> ExecutionPlan  
ExecutionPlanBuilder(registry)

---

## 🧾 Data Models

UserRequest:
- selected: set[str]
- counts: dict[str, int]
- optional: seed, strict

ExecutionPlan:
- expanded
- order
- nodes
- run_id
- created_at

---

## 🔌 Registry Contract

registry.has(resource_type: str) -> bool  
registry.get(resource_type: str) -> spec  

Each spec exposes:
spec.required_inputs

---

## ✅ Example Usage

from Core.planning import UserRequest, build_plan
from Core.registry import RESOURCE_REGISTRY

req = UserRequest(
    selected={"Condition"},
    counts={"Condition": 100, "Encounter": 50, "Patient": 50}
)

plan = build_plan(req, RESOURCE_REGISTRY)

---

## 🧪 Recommended Tests

- Unknown resource types
- Dependency expansion
- Cycle detection
- Invalid counts
- Deterministic ordering

---

## 🔮 Why This Is Future-Proof

- No hardcoded resource names
- Registry-driven dependencies
- Supports new datasets automatically
- Supports multi-dataset runs

---

## ➡️ Next Module

Module 3: Runtime
- RunContext
- ResourceStore
- Manifest writer
