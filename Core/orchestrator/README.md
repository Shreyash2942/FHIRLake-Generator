# 🧩 Orchestrator

## Purpose
The `orchestrator/` folder coordinates execution:
- builds an execution plan from dependencies
- runs generators in the correct order
- updates RunContext
- emits logs/progress
- triggers export + manifest writing

This is the engine that makes the project scalable.

---

## Files

### `planner.py`
Builds the execution plan:
- reads dependencies from `registry/`
- produces a dependency-safe order (DAG/topological sort)
Example:
Patient → Encounter → Condition

### `runner.py`
Executes the plan:
- loads generator scripts dynamically
- calls each generator with RunContext
- updates counters/pools
- writes manifest
- later: triggers exporters & storage

---

## Rules
- Planner should be pure logic (no IO)
- Runner should be the main entrypoint used by CLI + Windows App
- Runner must support:
  - `log_fn(message)`
  - `progress_fn(percentage)`
