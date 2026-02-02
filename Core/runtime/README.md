# 🧠 Runtime

## Purpose
The `runtime/` folder manages everything that exists during a run:
- shared run state
- counters
- generated IDs and pools
- manifest reporting

This ensures:
✅ referential integrity  
✅ reproducibility (via seed)  
✅ traceability (manifest output)

---

## Files

### `context.py`
Defines `RunContext`, which stores:
- pools of generated resources (Patient, Encounter, etc.)
- counters per resource type
- shared random seed / RNG
- optional metadata cache

Generators receive the same `RunContext` so they can link resources correctly.

### `manifest.py`
Defines `Manifest`, which tracks:
- run id, timestamps
- profile used
- resources generated
- output formats
- counts per resource
- list of files written

Manifest is written at the end of every run (example: `manifest.json`).

---

## Rules
- `RunContext` should stay lightweight and serializable
- Manifest must always be written even if exports are skipped
