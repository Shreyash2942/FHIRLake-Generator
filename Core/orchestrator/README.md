# 🧩 Core Orchestrator Module

FHIRLake Generator – CORE Orchestration Layer  
(Resource generation coordination & dependency execution)

---

## 📌 Introduction

The **Core Orchestrator module** is the **central execution engine** of the FHIRLake Generator.

Its responsibility is to:
- Coordinate the generation of multiple FHIR resources
- Enforce generation order based on dependencies
- Manage relationships between resources
- Populate the in-memory `ResourceStore`
- Produce a complete, consistent dataset **without globals**

This module is where **individual resource generators come together** to form a complete, analytics-ready dataset.

---

## 🎯 Why This Module Is Important

FHIR resources are **not independent**.

Examples:
- Encounter depends on Patient
- Condition depends on Patient and often Encounter
- Observation depends on Encounter, Patient, and Code systems
- Claim depends on Encounter, Organization, and Patient

Without an orchestrator:
- Each generator would need to know about others
- Linking logic would be duplicated
- Referential integrity would break
- Scaling to new resources would become chaotic

### ✅ The Orchestrator solves this by:
- Defining a **single source of truth** for generation flow
- Keeping generators **simple and reusable**
- Centralizing dependency handling
- Preventing broken references
- Making the system extensible and testable

---

## 🧠 What the Orchestrator Does (High-Level)

1. Initializes a dataset generation run
2. Creates a `RunContext` (seed, Faker, randomness)
3. Creates a `ResourceStore` (in-memory storage)
4. Generates resources **in dependency order**
5. Links resources using store indexes
6. Returns:
   - populated `ResourceStore`
   - run summary metadata

> The orchestrator **does not write files** and **does not validate schemas**.  
> Those concerns belong to other modules.

---

## 🛠 How to Use This Module

### 1️⃣ Define a Generation Plan
A `GenerationPlan` defines **what to generate**.

```python
from Core.orchestrator import GenerationPlan

plan = GenerationPlan(
    num_patients=10,
    encounters_per_patient=3,
    conditions_per_patient=2
)
```

---

### 2️⃣ Create a RunContext
```python
from Core.runtime import RunContext

ctx = RunContext(seed=42)
```

This ensures:
- Reproducibility
- Shared Faker/random instances
- One run ID and timestamp

---

### 3️⃣ Run the Orchestrator
```python
from Core.orchestrator import run_patient_encounter_condition_job

store, summary = run_patient_encounter_condition_job(
    plan=plan,
    ctx=ctx
)
```

---

### 4️⃣ Inspect Results
```python
print(summary)
print(store.counts())
```

Example output:
```json
{
  "run_id": "b1c7f8c0-2c91-4d14-9d3c-3b5e7c1b9d22",
  "timestamp_utc": "20260202_191233",
  "seed": 42,
  "counts": {
    "patients": 10,
    "encounters": 30,
    "conditions": 20
  }
}
```

---

## 🔍 Detailed Implementation Breakdown

### `run_patient_encounter_condition_job`

This function is the **v1 orchestrator implementation**.

#### Execution Flow:
1. Validate generation plan inputs
2. Initialize `RunContext` (if not provided)
3. Initialize `ResourceStore`
4. Loop through each patient:
   - Generate Patient
   - Generate fixed number of Encounters
   - Generate fixed number of Conditions
5. Link resources using `ResourceStore` relationship indexes
6. Auto-create parent resources if required to maintain integrity
7. Return store + summary

---

### Referential Integrity Guarantee

This orchestrator **never creates broken references**.

If a Condition requires an Encounter and none exist:
- The orchestrator automatically generates a minimal Encounter
- Links it correctly
- Continues generation safely

This behavior will later be configurable via the Linking module.

---

## 📈 Scaling Guidelines (Adding More FHIR Resources)

When adding new resources (Location, Organization, Practitioner, Observation, Claim, etc.):

### ✅ What to Add
- Extend the orchestrator flow **step-by-step**
- Respect dependency order
- Use `ResourceStore` indexes for linking
- Keep generators unaware of orchestration logic

Example future flow:
```
Patient
 ├── Encounter
 │    ├── Condition
 │    ├── Observation
 │    └── Procedure
 └── Claim
```

---

### ❌ What NOT to Do
- Do not embed linking logic inside generators
- Do not access global state
- Do not write files here
- Do not validate FHIR schemas here

---

## 🔗 How This Module Works With Other CORE Modules

| Module | Interaction |
|------|------------|
| Core/runtime | Provides RunContext and ResourceStore |
| Core/linking | Will replace inline linking rules |
| Core/validators | Will validate store integrity |
| Exporter | Reads ResourceStore and writes files |
| CLI | Calls orchestrator as entrypoint |
| GUI | Calls orchestrator directly |

---

## 🧪 Testing Strategy

This module is tested via:
- Manual scripts (development)
- Unit tests with fixed seeds
- Count assertions
- Relationship integrity checks

Because the orchestrator is deterministic when seeded, tests are:
- Reliable
- Fast
- Reproducible

---

## 🧠 Design Philosophy

- Orchestrator is **smart**
- Generators are **dumb**
- Runtime is **stable**
- Linking is **centralized**
- Exporting is **separate**

This separation allows the FHIRLake Generator to scale from:
- 3 resources → 30+ resources
- Local scripts → production pipelines
- CLI → GUI → automation

---

## ✅ Summary

The Core Orchestrator module is the **heart of dataset generation**.

It:
- Coordinates resource creation
- Enforces dependency order
- Guarantees referential integrity
- Enables future scalability

All dataset generation in FHIRLake flows **through this module**.
