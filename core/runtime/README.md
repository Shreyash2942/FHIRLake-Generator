## 🧠 Key Concepts

### 1️⃣ RunContext

`RunContext` represents **one dataset generation run**.

It stores:

- `run_id` (UUID)
- `created_at` (UTC ISO timestamp)
- `timestamp_utc` (compact UTC string for folders)
- Optional random seed
- Shared `random.Random` instance
- Shared `Faker` instance

#### Responsibilities

- Eliminate global state  
- Ensure reproducible dataset runs  
- Provide shared randomness and utilities across CORE modules  

#### Example

```python
from core.runtime import RunContext

ctx = RunContext(seed=42)
```

---

### 2️⃣ ResourceStore (100% Future-Proof)

`ResourceStore` is a **generic, registry-driven in-memory store**.

It makes **no assumptions** about:

- Which resources exist  
- How they relate  
- What datasets are installed  

Everything is driven by **Registry specs** and **Planning output**.

---

#### 🗂 Bucketed Resource Storage

Resources are stored by bucket, defined in the Registry:

```text
store.resources[bucket] -> list[resource_json]
```

Buckets come from:

```python
spec.bucket
```

Example:

```python
store.add("patients", {"resourceType": "Patient", "id": "pat-1"})
```

No resource names are hardcoded in Runtime.

---

#### 🔎 Existence Index

Runtime tracks all generated resources using:

```text
(resourceType, id)
```

This enables:

- Fast reference validation  
- Safe linking  
- Validator checks later  

Example:

```python
store.exists("Patient", "pat-1")
```

---

#### 🧺 Generic Pools (Resolver-Driven)

Pools are generic ID lists used by Resolver:

```python
store.pools["patient_ids"] = ["pat-1", "pat-2"]
store.pools["observation_ids"] = ["obs-1"]
```

Standard convention:

```text
{resource_type.lower()}_ids
```

Example helper:

```python
store.register_id("Patient", "pat-1")
```

---

#### 🔗 Generic Link Indexes (No Hardcoding)

Links are stored generically as:

```text
store.links[index_name][parent_id] -> [child_ids]
```

Standard convention:

```text
{parent.lower()}_to_{child.lower()}
```

Example:

```python
store.register_link(
    parent_type="Patient",
    parent_id="pat-1",
    child_type="Encounter",
    child_id="enc-1"
)
```

This works for **any future dataset**:

- Patient → Observation  
- Organization → Practitioner  
- Claim → ExplanationOfBenefit  
- etc.

No Runtime changes required.

---

### 3️⃣ Run Manifest (`manifest.py`)

Runtime writes a stable run summary:

```text
run_summary.json
```

It includes:

- Run metadata (run_id, timestamps, seed)
- Plan overview (selected, expanded, order)
- Expected counts (from Planning)
- Actual counts (from ResourceStore)
- Optional bucket-level aggregation (via Registry)

This file is ideal for:

- Auditing  
- Debugging  
- ETL lineage  
- Validation reports  

---

## 🛠 High-Level Execution Flow

1. Engine starts a run  
2. `RunContext` is created  
3. `ResourceStore` is created  
4. Planning provides execution order  
5. Orchestrator generates resources  
6. Resources are stored by bucket  
7. Pools and links are registered  
8. Manifest is written  
9. Storage / Export modules consume the store  

---

## 🚀 Example Usage

```python
from core.runtime import RunContext, ResourceStore, write_manifest

ctx = RunContext(seed=42)
store = ResourceStore()

store.add("patients", {"resourceType": "Patient", "id": "pat-1"})
store.register_id("Patient", "pat-1")

store.add("encounters", {"resourceType": "Encounter", "id": "enc-1"})
store.register_id("Encounter", "enc-1")

store.register_link("Patient", "pat-1", "Encounter", "enc-1")

write_manifest(
    "outputs/run_1",
    ctx=ctx,
    plan=execution_plan,
    store=store,
    registry=registry
)
```

---

## 🔗 Integration With Other CORE Modules

| Module | How it Uses Runtime |
|------|---------------------|
| Planning | Supplies execution order & counts |
| Resolver | Reads pools & writes links |
| Orchestrator | Owns RunContext & ResourceStore |
| Validators | Uses existence checks & links |
| Storage | Persists ResourceStore |
| Export | Reads ResourceStore |
| CLI / GUI | Initializes RunContext |

---

## 📈 Scaling Guidelines

### ✅ When adding new datasets

- Add new generators + registry specs  
- Declare `bucket`, `dependencies`, `required_inputs`  
- Use `register_id()` and `register_link()` in generators  

### ❌ What NOT to do

- Do not hardcode resource names in Runtime  
- Do not add FHIR logic here  
- Do not add export logic here  

Runtime must remain **boring, stable, and generic**.

---

## 🧠 Design Philosophy

- No globals  
- One run = one context  
- Runtime contains no business logic  
- All intelligence lives in Planning, Resolver, and Generators  

---

## ✅ Summary

The Core Runtime module is the **foundation** of the FHIRLake Generator.

It guarantees:

- Reproducible runs  
- Clean state isolation  
- Unlimited future dataset growth  

Once finalized, **this module never needs to change again**.
