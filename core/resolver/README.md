## 🔌 Registry Contract (What Resolver Expects)

Resolver depends on **Registry specs**, but does **NOT** modify them.

Each `ResourceSpec` may define:

```python
required_inputs = ["patient_id", "encounter_id"]
dependency_policy = "AUTO_CREATE" | "ERROR" | "FALLBACK"
```

### Important Notes

- `required_inputs` are generator input keys, not resource types
- Resolver automatically converts `*_id` → `ResourceType`
- `dependencies` (resource types) are used by **Planning**, not Resolver

---

## 🧠 Runtime Contract (What Resolver Uses)

Resolver interacts with `ResourceStore` only through **generic interfaces**.

### Required Runtime APIs

```python
store.get_pool(pool_name) -> list[str]
```

### Pool Naming Convention

```text
{resource_type.lower()}_ids
```

### Examples

```text
Patient     → patient_ids
Encounter   → encounter_ids
Observation → observation_ids
```

Resolver never hardcodes resource names.

---

## 🧩 Key Concepts

### 1️⃣ Input Key → Resource Type Mapping

Resolver maps generator inputs like:

```text
patient_id               → Patient
encounter_id             → Encounter
medication_id            → Medication
medication_request_id    → MedicationRequest
```

#### Rules

- Input key must end with `_id`
- `snake_case` → `PascalCase`
- No registry changes required

#### Optional Override (Advanced Use)

```python
spec.input_resource_types = {
    "subject_id": "Patient"
}
```

---

### 2️⃣ Dependency Policies

Resolver enforces the registry-defined policy:

```text
ERROR        → Raise error if dependency missing
FALLBACK     → Pass None into generator
AUTO_CREATE  → Signal orchestrator to create missing parents (default)
```

> ⚠️ `AUTO_CREATE` does NOT create resources itself.  
> It raises a signal that the **Orchestrator** handles.

---

### 3️⃣ ResolvedInputs (Resolver Output)

Resolver returns a `ResolvedInputs` object:

```python
ResolvedInputs(
    values={"patient_id": "pat-1"},
    parent_refs=[("Patient", "pat-1")]
)
```

#### values

- Passed directly into the generator
- Generator remains unaware of resolution logic

#### parent_refs

- Used by Orchestrator after child creation
- Enables generic link registration
- Prevents hardcoded relationships

---

## 🔗 Linking Without a Linking Module

Resolver replaces the linking module.

Instead of:
- generating resources
- then linking later

We now:
- resolve parents first
- generate children safely
- register links immediately

### Example (Handled by Orchestrator)

```python
for parent_type, parent_id in resolved.parent_refs:
    store.register_link(
        parent_type,
        parent_id,
        child_resource_type,
        child_id
    )
```

---

## 🚀 Example Usage

```python
from core.runtime import RunContext, ResourceStore
from core.resolver import Resolver

ctx = RunContext(seed=42)
store = ResourceStore()

# Simulate previously generated Patients
store.register_id("Patient", "pat-1")
store.register_id("Patient", "pat-2")

class EncounterSpec:
    required_inputs = ["patient_id"]
    dependency_policy = "ERROR"

resolver = Resolver()
resolved = resolver.resolve(
    resource_type="Encounter",
    spec=EncounterSpec(),
    ctx=ctx,
    store=store
)

print(resolved.values)
# {"patient_id": "pat-1"}

print(resolved.parent_refs)
# [("Patient", "pat-1")]
```

---

## 🔗 How Resolver Fits in Core Flow

```text
Registry ──▶ Planning ──▶ Runtime
                          │
                          ▼
                       Resolver
                          │
                          ▼
                     Orchestrator
```

Resolver ensures:
- Planning assumptions are respected
- Runtime pools are used safely
- Orchestrator remains dumb and clean

---

## 📈 Scaling & Future-Proofing

### ✅ When adding new datasets

You only need to:
- Add new generators
- Add new registry specs with `required_inputs`

Resolver supports them automatically.

### ❌ What NOT to do

- Do not hardcode resource names
- Do not add FHIR logic here
- Do not add export logic here

---

## 🧠 Design Philosophy

- Resolver is stateless
- Resolver is generic
- Resolver contains no FHIR logic
- Resolver does not mutate Runtime directly
- Resolver exists to make Core unbreakable

---

## ✅ Summary

The Core Resolver module:
- Replaces a dedicated linking module
- Guarantees safe reference resolution
- Enables deterministic, reproducible datasets
- Ensures Core never changes as datasets grow

Once Resolver is in place, the next and final Core module is:

➡️ **Core Orchestrator (Engine Runner)**

This will tie everything together with minimal logic.
