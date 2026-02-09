# 🧭 CORE Relationship Planning & Linking Roadmap

This document explains **how FHIRLake Generator will scale relationships** across many FHIR resources and how we will ensure **user-selected resources always meet required dependencies**.

It includes:
- A practical, step-by-step implementation plan
- Module boundaries (who does what)
- How to validate user selections
- How to scale to many resources without spaghetti logic

---

## ✅ Goal

Build a **data-driven dependency system** so that:

1. Users can select any set of FHIR resources (CLI / GUI checkboxes)
2. CORE automatically:
   - validates the request
   - expands dependencies (adds required parents)
   - produces a correct generation order
3. Linking logic is centralized:
   - references never point to missing resources
   - policies decide whether to auto-create, error, or fallback

---

## 🧩 Core Design Principles

### 1) Generators are “dumb”
Each generator creates **one resource** given necessary IDs:
- `generate_encounter(patient_id)`
- `generate_condition(patient_id, encounter_id)`

Generators do NOT:
- decide dependencies
- pick related resources
- read global state
- write files

### 2) Orchestrator executes a plan
Orchestrator should be a small loop:
- iterate steps in correct order
- call generators
- register resources in store
- delegate relationships to linking layer

### 3) Planning + Linking is centralized
All relationship decisions must live in CORE modules:
- `Core/planning` builds the execution plan
- `Core/linking` applies policies + selects related IDs

---

## 📦 Modules We Will Add

### ✅ `Core/planning/`
Responsible for:
- validating user resource selection
- expanding dependencies
- determining generation order (topological sort)
- enforcing count minimums (e.g., Observation requires encounters >= 1)
- producing a final executable `GenerationPlan`

### ✅ `Core/linking/`
Responsible for:
- relationship rules and policies
- selecting related resource IDs for linking
- auto-creating required parents if policy says so
- registering relationship indexes in ResourceStore
- preventing broken references

### ✅ `Core/validators/` (later)
Responsible for:
- verifying referential integrity across the entire run
- reporting missing/broken references
- generating a validation report

---

## 🧠 Dependency Graph Model

We maintain a registry that defines:

- what each resource depends on
- whether dependencies are required or optional
- minimum cardinality requirements

Example (v1 for your current scope):

| Resource | Depends On | Requirement |
|---------|------------|------------|
| Patient | — | — |
| Encounter | Patient | required |
| Condition | Patient | required |
| Condition | Encounter | policy-controlled (required for analytics) |

Later additions:

| Resource | Depends On | Requirement |
|---------|------------|------------|
| Observation | Patient, Encounter | required |
| Claim | Patient, Encounter, Organization | required |
| Location | (used by Encounter.location) | optional / recommended |

---

## 🧪 Relationship Policies

Policies decide what to do when a required relationship is missing.

### Supported actions (recommended)
1. **AUTO_CREATE**
   - create the missing parent resource and continue
2. **ERROR**
   - stop and tell user what to change
3. **FALLBACK**
   - preserve contract using your extension/note approach

Example policy:
- `Condition.encounter` is **required** for your analytics dataset
- if no Encounter exists → `AUTO_CREATE` encounter

---

## 🧱 Implementation Steps (Proper Roadmap)

### ✅ Step 1 — Create ResourceType Registry (Data-driven)
Create a centralized registry for resources and dependencies.

Deliverable:
- `Core/planning/registry.py`

What it contains:
- Supported resource types list
- Dependency edges
- Default policies per relationship
- Minimums for count enforcement

---

### ✅ Step 2 — Implement Plan Builder
Build a planner that takes user selection and produces a finalized plan.

Deliverables:
- `Core/planning/models.py` (dataclasses for request + plan)
- `Core/planning/builder.py` (expand dependencies + ordering)

Planner responsibilities:
1. Validate requested resource types are supported
2. Expand dependencies recursively
3. Perform topological sort to compute execution order
4. Enforce minimum counts for required parents
5. Return `GenerationPlan`

---

### ✅ Step 3 — Implement Linking Manager (v1)
Centralize all relationship behavior here.

Deliverables:
- `Core/linking/policies.py`
- `Core/linking/relationship_manager.py`

Responsibilities:
- Provide selectors like:
  - `pick_encounter(patient_id)`
  - `ensure_min_encounters(patient_id, min_count)`
- Apply policy:
  - AUTO_CREATE if missing
  - ERROR if missing
  - FALLBACK if missing
- Register links in ResourceStore indexes

---

### ✅ Step 4 — Refactor Orchestrator to Use Plan + Linking
Orchestrator becomes simple:
- execute steps from plan in order
- let linking manager handle references

Deliverables:
- Update `Core/orchestrator/run.py` to:
  - accept `UserRequest`
  - call `PlanBuilder`
  - execute generated plan
  - call linking manager for selection + integrity

---

### ✅ Step 5 — Add Validator Module (Integrity Report)
After execution, validate:
- every reference points to an existing resource
- counts match plan expectations
- report warnings/errors

Deliverables:
- `Core/validators/reference_integrity.py`
- `Core/validators/report.py`

Output:
- `validation_report.json`
- summary printed in CLI/GUI

---

### ✅ Step 6 — Integrate with Exporter + Storage
Exporter should already work because it writes `store.resources`.

Storage:
- creates output folders
- writes run summary + validation report

Deliverables:
- add `validation_report.json` writing in `storage/local.py`

---

### ✅ Step 7 — CLI / GUI Integration (User-selected resources)
Now your CLI/GUI can safely do:

1. user selects resources
2. planner expands dependencies
3. system generates correct dataset
4. exporter writes output
5. validator reports integrity

---

## 📈 Scaling Guide (Adding More Resources)

When you add a new resource like `Observation`:

### 1) Add it to the registry
- supported resources: `Observation`
- dependencies: `Patient`, `Encounter`
- policy: required relationships

### 2) Add generator mapping
Tell orchestrator which generator function to call.

Example mapping:
- `"Observation": generate_observation`

### 3) Add linking methods (if needed)
If Observation needs special linking:
- choose encounter for patient
- choose observation codes
- register indexes (optional)

### 4) Exporter + Storage require no changes
Because exporter loops over store buckets automatically.

---

## 🔗 Integration With Other Modules

| Module | Uses Planning? | Uses Linking? | Uses Runtime Store? |
|-------|-----------------|---------------|---------------------|
| Orchestrator | ✅ yes | ✅ yes | ✅ yes |
| Exporter | ❌ no | ❌ no | ✅ yes |
| Storage | ❌ no | ❌ no | ✅ yes (paths) |
| CLI | ✅ yes | indirectly | indirectly |
| GUI | ✅ yes | indirectly | indirectly |
| Validators | indirectly | indirectly | ✅ yes |

---

## ✅ Summary

This roadmap ensures:

- Centralized dependency management
- Automatic expansion of user-selected resources
- Policy-driven relationship handling
- No broken references
- Clean scaling to many resources
- Stable CORE API usable by CLI + GUI

---

## Next Implementation Target (Recommended)

Implement v1 for your current 3 resources:

1) `Core/planning` registry + builder
2) `Core/linking` relationship manager
3) Refactor orchestrator to use plan + linking

Then expand the registry to new resources gradually.
