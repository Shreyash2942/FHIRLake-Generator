# 🧠 Core Runtime Module

FHIRLake Generator – CORE Runtime Layer  
(Foundational execution context & in-memory state management)

---

## 📌 Overview

The **Core Runtime module** provides the **foundational execution layer** for the FHIRLake Generator.  
It is responsible for managing **run-level state**, **controlled randomness**, and **in-memory storage of generated FHIR resources** during a dataset generation job.

This module intentionally contains **no FHIR-specific business logic**.  
Instead, it provides **stable primitives** that all other CORE modules rely on.

> Think of this module as the **“operating system”** for a single dataset generation run.

---

## 🎯 Why This Module Exists

Before introducing `Core/runtime`, the project relied on:
- Global variables
- Scattered `Faker()` instances
- Uncontrolled randomness (`random.choice`)
- Ad-hoc timestamps
- Hard-to-reproduce dataset runs

These patterns become **unmaintainable** when:
- More FHIR resources are added
- CLI / GUI entrypoints are introduced
- Multiple dataset runs are executed in one process
- Deterministic testing and validation are required

### ✅ Runtime solves this by providing:
- One shared execution context per run
- Deterministic and reproducible data generation
- Centralized in-memory resource storage
- Clean separation between **generation**, **linking**, and **export**

---

## 🧩 What This Module Contains

```
Core/runtime/
│
├── context.py   # RunContext (run-level execution state)
├── store.py     # ResourceStore (in-memory resource + indexes)
└── __init__.py
```

---

## 🧠 Key Concepts

### 1️⃣ RunContext

`RunContext` represents **one dataset generation run**.

It stores:
- Random seed (for reproducibility)
- Shared Faker instance
- Shared random number generator
- Unique run ID
- Consistent UTC timestamp

#### Responsibilities
- Eliminate global state
- Ensure reproducible dataset runs
- Provide shared utilities across CORE modules

---

### 2️⃣ ResourceStore

`ResourceStore` is an **in-memory registry** for all generated resources.

It:
- Stores resources grouped by logical bucket (patients, encounters, etc.)
- Tracks relationships between resources
- Enables fast existence checks
- Provides summary counts for validation & logging

#### Responsibilities
- Replace global `data_store` dictionaries
- Maintain referential integrity metadata
- Serve as the single source of truth during generation

---

## 🛠 How This Module Works (High-Level)

1. A dataset run starts
2. A `RunContext` is created
3. A `ResourceStore` is created
4. CORE orchestrator generates resources
5. Each generated resource is:
   - Converted to JSON
   - Added to the ResourceStore
   - Indexed for relationships
6. Other CORE modules (linking, validation, export) consume the store

---

## 🚀 How to Use This Module in the Project

### Step 1: Create a RunContext
```python
from Core.runtime import RunContext

ctx = RunContext(seed=42)
```

This ensures:
- Controlled randomness
- Reproducibility
- One run ID for the dataset

---

### Step 2: Create a ResourceStore
```python
from Core.runtime import ResourceStore

store = ResourceStore()
```

This store will hold **all resources generated in this run**.

---

### Step 3: Add resources to the store
```python
store.add(
    "patients",
    {
        "resourceType": "Patient",
        "id": "patient-1"
    }
)
```

---

### Step 4: Link relationships (used by linking module)
```python
store.link_patient_encounter("patient-1", "encounter-1")
store.link_patient_condition("patient-1", "condition-1")
store.link_encounter_condition("encounter-1", "condition-1")
```

---

### Step 5: Inspect run results
```python
store.counts()
```

Example output:
```json
{
  "patients": 10,
  "encounters": 30,
  "conditions": 20
}
```

---

## 🔍 Implementation Details

### RunContext (`context.py`)
- Uses `@dataclass(slots=True)` for memory efficiency
- Creates **one Faker instance per run**
- Seeds both Faker and Python `random`
- Generates:
  - `run_id` (UUID)
  - `timestamp_utc` (used in filenames, metadata, logs)

### ResourceStore (`store.py`)
- Uses structured dictionaries and lists
- Tracks:
  - patient → encounters
  - patient → conditions
  - encounter → conditions
- Maintains an internal `(resourceType, id)` set for fast validation

---

## 📈 Scaling Guidelines (Adding More FHIR Resources)

When adding new resources (Location, Organization, Practitioner, Observation, Claim, etc.):

### ✅ What to do
- Add new buckets in `ResourceStore.resources`
- Add new relationship indexes **only if needed**
- Keep resource generators unaware of storage details
- Let CORE orchestrator decide:
  - generation order
  - cardinality
  - linking rules

### ❌ What NOT to do
- Do not add FHIR logic inside `runtime`
- Do not hard-code relationships here
- Do not add export logic here

> Runtime should remain **generic and stable**, even as the project grows.

---

## 🔗 How This Module Integrates With Other CORE Modules

| Module | How it Uses Runtime |
|------|---------------------|
| Core/orchestrator | Creates RunContext & ResourceStore |
| Core/linking | Reads & writes relationship indexes |
| Core/validators | Uses existence checks + indexes |
| Exporter | Reads final ResourceStore |
| CLI | Initializes RunContext (seed, config) |
| GUI (future) | Calls CORE using same runtime |

---

## 🧪 Testing Guidance

This module can be tested **independently**:
- Reproducibility tests (seeded runs)
- Store existence checks
- Relationship index integrity

Because there is no FHIR logic here, tests are:
- Fast
- Deterministic
- Easy to maintain

---

## 🧠 Design Philosophy

- **No globals**
- **One run = one context**
- **Runtime is boring by design**
- **All intelligence lives above this layer**

This makes the FHIRLake Generator:
- Scalable
- Testable
- CLI / GUI friendly
- Production-ready

---

## ✅ Summary

The Core Runtime module is the **foundation** of FHIRLake Generator.

It ensures:
- Reproducible dataset runs
- Clean state management
- Safe scaling as more resources and features are added

All other CORE modules are built **on top of this layer**.
