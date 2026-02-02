# 🧠 Core Engine – FHIRLake Generator

## 📌 Overview
The `Core` module is the **central execution engine** of the FHIRLake Generator project.

It is responsible for coordinating configuration loading, dependency resolution, runtime state management, and orchestration of dataset generation. The Core module contains **no resource-specific logic** and is designed to be small, reusable, and scalable.

This separation allows new FHIR resources to be added without modifying the engine itself.

---

## 🎯 Responsibilities
The Core engine handles:

- Loading global defaults and execution profiles
- Registering available FHIR resources and their generators
- Building dependency graphs between resources
- Planning execution order (DAG-based)
- Managing runtime state and reference resolution
- Tracking run metadata and output manifests

---

## 🗂️ Module Structure

```text
Core/
├── config/
│   ├── defaults.yaml              # Global generation defaults
│   └── profiles/                  # small_demo, large_run, etc.
│
├── registry/
│   └── resource_registry.py       # Resource → generator + dependencies
│
├── runtime/
│   ├── context.py                 # RunContext (state, counters, pools)
│   └── manifest.py                # Run manifest model + writer
│
├── linking/
│   ├── reference_graph.py         # Defines valid FHIR relationships
│   └── resolver.py                # Resolves references safely
│
├── orchestrator/
│   ├── planner.py                 # Builds execution plan (DAG)
│   └── runner.py                  # Executes generators in order
│
└── README.md
```

---

## 🧩 Core Concepts

### 🔹 RunContext
A shared object passed to all generators that stores:
- Generated resource IDs
- Reference pools (patients, encounters, etc.)
- Counters and runtime metadata

This guarantees **referential integrity** across all resources.

### 🔹 Resource Registry
The registry defines:
- Which resources exist
- Where their generator scripts live
- Their dependency requirements

This allows **plug-and-play resource expansion**.

### 🔹 Dependency & Execution Planning
Dependencies are modeled as a graph:
- Patient → Encounter → Condition
- Planner builds a DAG
- Runner executes generators in a safe order

---

## 🔗 What Core Does NOT Do
- Generate FHIR resources
- Export data to files
- Handle storage backends
- Parse CLI arguments

Those concerns belong to other modules.

---

## ➕ Extending the System
To add a new resource:
1. Add generator under `Datasets/`
2. Register it in `resource_registry.py`
3. Define relationships in `reference_graph.py`

No Core logic changes required.

---

## 🧠 Design Philosophy
- Strict separation of concerns
- Dependency-driven execution
- Deterministic, repeatable runs
- Enterprise-scale extensibility
