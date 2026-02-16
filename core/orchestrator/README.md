# 🏃 Core Orchestrator Module (FHIRLake Generator)

The **Orchestrator** is the execution engine of the Core system.

It coordinates:
- Registry
- Planning
- Runtime
- Resolver

and produces a **fully linked, reproducible dataset run**.

---

## 📁 Module Structure

```text
core/orchestrator/
├── __init__.py        # Public exports (run_job, EngineConfig)
├── run.py             # Core engine runner
└── README.md          # This file
```

---

## 🧠 Responsibilities

The Orchestrator is intentionally thin and generic.  
It performs **no FHIR-specific logic**.

It is responsible for:

1. Building an execution plan using **Planning**
2. Creating **RunContext** and **ResourceStore**
3. Executing resources in dependency-safe order
4. Resolving generator inputs using **Resolver**
5. Loading generators dynamically from Registry specs
6. Storing generated resources by registry-defined buckets
7. Registering IDs and parent-child links generically
8. Writing a deterministic run manifest

---

## 🔌 Generator Contract

Generators must implement **one** of the following patterns:

### Function-based generator
```python
def generate(ctx, store, inputs: dict, count: int) -> list[dict]:
    ...
```

### Class-based generator
```python
class MyGenerator:
    def generate(self, ctx, store, inputs: dict, count: int) -> list[dict]:
        ...
```

### Registry Requirement
Each `ResourceSpec` must define:

```python
generator = "Datasets.some_module:generate"
```

or

```python
generator = "Datasets.some_module.MyGenerator"
```

---

## 🧺 Runtime Conventions (REQUIRED)

To allow Resolver to work generically, generators **must register IDs**:

```python
store.register_id(resourceType, resource_id)
```

Example:

```python
store.register_id("Patient", "pat-1")
```

If IDs are not registered, Resolver will fail when resolving dependencies.

---

## 🚀 Example Usage

```python
from core.registry import get_resource_registry
from core.planning import UserRequest
from core.orchestrator import run_job, EngineConfig

registry = get_resource_registry("Datasets")

req = UserRequest(
    selected={"Condition"},
    counts={
        "Patient": 50,
        "Encounter": 100,
        "Condition": 200
    },
    seed=42,
    strict=True
)

store, summary = run_job(
    req,
    registry,
    EngineConfig(output_dir="outputs")
)

print(summary["manifest_path"])
print(store.counts_by_bucket())
```

---

## 📄 Manifest Output

The Orchestrator writes a run summary:

```text
outputs/
└── run_<timestamp>_<run_id>/
    └── run_summary.json
```

The manifest includes:
- Run metadata (run_id, timestamps, seed)
- Planning summary (selected, expanded, order)
- Expected counts
- Actual counts by bucket

This file is ideal for:
- Auditing
- Debugging
- ETL lineage
- Validation

---

## 🧠 Design Philosophy

- Orchestrator is **stateless**
- Orchestrator is **registry-driven**
- Orchestrator contains **no dataset logic**
- Core behavior never changes as datasets grow

All intelligence lives in:
- Registry
- Planning
- Resolver
- Dataset generators

---

## ✅ Summary

The Core Orchestrator module:

- Finalizes the Core execution pipeline
- Guarantees deterministic, reproducible runs
- Ensures Core remains frozen and stable
- Allows unlimited dataset growth without Core changes

Once this module is in place, **Core is complete**.
