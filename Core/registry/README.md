# 🧾 Resource Registry

## Purpose
The `registry/` folder defines which FHIR resources the system supports and where to find their generator scripts.

It works like a plugin system:
- Add a generator script in `Datasets/`
- Register it here
- Core automatically includes it in planning and execution

---

## File

### `resource_registry.py`
Maps:
- `resource_type` (Patient, Encounter, Condition, etc.)
- generator path (script location)
- dependencies (Encounter depends on Patient)

Example:
- Patient: no deps
- Encounter: depends on Patient
- Condition: depends on Encounter (and often Patient)

---

## Why Registry Matters
- makes Core resource-agnostic
- supports future scaling (more resources)
- enables Windows UI to display available resources dynamically

---

## Rules
- One entry per resource type
- Always list dependencies correctly
- Keep generator path stable and importable

---

## ✅ Implementation Plan

This section explains **how we will implement and use the registry** as the project scales.

### 1) Create the Registry Structure
Recommended folder structure:

```text
Core/
└── registry/
├── init.py
├── resource_registry.py
└── README.md
```

---

### 2) Define a Standard Registry Entry
Each resource will have one registry entry that describes:
- **resource_type**: FHIR type name (e.g., `Patient`, `Encounter`)
- **bucket**: where it is stored in `ResourceStore` (e.g., `patients`, `encounters`)
- **generator**: importable generator reference (preferred over filesystem paths)
- **dependencies**: list of required resource types
- **policy (optional)**: relationship enforcement rule (AUTO_CREATE / ERROR / FALLBACK)

✅ Recommended generator format (stable & importable):
- `"patient.generate_patient_fhir:generate_patient"`
- `"encounter.generate_encounter_fhir:generate_encounter"`
- `"condition.generate_condition_fhir:generate_condition"`

This avoids fragile filesystem paths and works well for CLI + GUI.

---

### 3) Add v1 Entries (Patient, Encounter, Condition)
Initial registry will support the 3 core resources:

- **Patient**: no dependencies
- **Encounter**: depends on Patient
- **Condition**: depends on Patient, and may also require Encounter depending on dataset contract policy

---

### 4) Integrate Registry Into Planning
The **planning module** will use the registry to:

✅ Validate user selection
- User selects resources in CLI/GUI
- Planner confirms they exist in registry

✅ Expand dependencies automatically
- If user selects `Condition`, planner auto-adds `Patient`
- If policy says `Condition.encounter` is required, planner also auto-adds `Encounter`

✅ Build correct execution order (topological sort)
Example execution order:
1. Patient
2. Encounter
3. Condition

---

### 5) Integrate Registry Into Orchestrator Execution
The orchestrator will:
- Load the final expanded plan from Planning
- Use the registry’s generator mappings to call the correct functions
- Store output in `ResourceStore` under correct bucket keys

This keeps the orchestrator **resource-agnostic** and avoids hard-coded imports per resource.

---

### 6) Enable Windows GUI (Future)
The GUI will read the registry to:
- Display resource list dynamically (checkboxes)
- Show dependency tooltips like:
  - “Condition requires Patient and Encounter”
- Auto-select or warn about required dependencies
- Stay synced with CORE without UI code changes when new resources are added

---

## 📈 Scaling Guidelines (Adding New Resources)

When you add a new resource (example: `Observation`):

### Step A — Add generator
Create:
- `observation/generate_observation_fhir.py`

### Step B — Register it
Add an entry in `resource_registry.py`:
- resource_type: Observation
- generator: import string or callable
- dependencies: Patient + Encounter

### Step C — Add linking rules (if needed)
If Observation needs special linking (encounter selection, code selection), implement in:
- `Core/linking/relationship_manager.py`

✅ Exporter and Storage require **no change**, because they write whatever is in `ResourceStore`.

---

## ✅ Summary
The registry is a **core scaling primitive** for FHIRLake Generator.

It ensures:
- CORE stays resource-agnostic
- dependency expansion is automatic
- generation order is correct
- GUI and CLI can stay dynamic and consistent
- new resources can be added with minimal code changes
