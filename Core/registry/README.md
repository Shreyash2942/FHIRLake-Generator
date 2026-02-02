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
