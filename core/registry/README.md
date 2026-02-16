# 🧾 Resource Registry

## 📌 Purpose

The Resource Registry defines which FHIR resources the system supports, how they are generated, and how they depend on each other.

This module acts as a core discovery and metadata layer for the FHIRLake Generator engine.

Instead of hard-coding resources inside the CORE engine, the registry works as a plugin system:

- Each dataset provides its own metadata using a resource_spec.py file
- CORE automatically discovers all supported resources
- Planning and orchestration adapt dynamically
- Adding new datasets does NOT require changing CORE logic

This design keeps the engine scalable, modular, and future-proof.

---

## 🧠 How the Registry Works (High-Level)

1. CORE scans the Datasets directory
2. Each dataset folder may include a resource_spec.py file
3. The registry loader imports those specs dynamically
4. All discovered ResourceSpec objects are combined into a single registry
5. Planning, orchestrator, CLI, and GUI all use this registry as the source of truth

---

## 📂 Registry Folder Structure

```text
Core  
└── registry                         — Registry package (single source of truth for supported resources)  
    ├── __init__.py                  — Exposes the public registry API to CORE, CLI, and GUI  
    │                                  (for example: get_resource_registry, supported_resource_types)  
    │  
    ├── models.py                    — Defines registry data models only  
    │                                  • ResourceSpec dataclass  
    │                                  • DependencyPolicy (AUTO_CREATE, ERROR, FALLBACK)  
    │                                  • No business logic in this file  
    │  
    ├── loader.py                    — Plugin discovery and loading logic  
    │                                  • Scans Datasets/ for resource_spec.py files  
    │                                  • Dynamically imports each plugin  
    │                                  • Validates RESOURCE_SPEC objects  
    │                                  • Prevents duplicate resource_type entries  
    │  
    ├── registry.py                  — Registry builder and cache manager  
    │                                  • Builds the final registry dictionary  
    │                                  • Caches registry per datasets_root  
    │                                  • Used by planning, orchestrator, CLI, and GUI  
    │  
    └── README.md                    — Human-readable documentation  
                                       • Explains registry purpose and design  
                                       • Shows how plugin-based discovery works  
                                       • Provides scaling and best-practice guidance  

```

---

## 🧩 ResourceSpec (Registry Entry Model)

Each supported FHIR resource is described using a ResourceSpec object.

A ResourceSpec defines:

- resource_type  
  FHIR resource name (Patient, Encounter, Condition)

- bucket  
  Storage key used in ResourceStore (patients, encounters, conditions)

- generator  
  Importable reference to the generator function  
  Format: module.path:function_name

- dependencies  
  List of required parent resources  
  Example: Condition depends on Patient and Encounter

- optional_dependencies  
  List of optional parent resources  
  Example: Condition optionally links to Practitioner

- required_inputs  
  Parameters the generator requires  
  Example: patient_id, encounter_id

- optional_inputs  
  Optional parameters the generator can use if available  
  Example: practitioner_id

- dependency_policy  
  How missing dependencies are handled  
  Options: AUTO_CREATE, ERROR, FALLBACK

- description (optional)  
  Human-readable explanation used by CLI and GUI

---

## 🧪 Example Plugin (resource_spec.py)

Each dataset folder provides its own plugin file.

Example folder layout:
```text
Datasets
└── FHIRLake_resources
    └── clinical
        └── Summary
            └── Condition
                ├── generate_fhir_condition.py
                └── resource_spec.py
```

The resource_spec.py file defines one RESOURCE_SPEC object with:

- resource_type: Condition
- bucket: conditions
- generator: Datasets.FHIRLake_resources.clinical.Summary.Condition.generate_fhir_condition:generate_condition
- dependencies: Patient, Encounter
- required_inputs: patient_id, encounter_id
- dependency_policy: AUTO_CREATE
- description: Synthetic Condition linked to Patient and Encounter

---

## 🔗 Why the Registry Matters

The registry enables CORE to be resource-agnostic.

It allows the engine to:

- Dynamically discover available datasets
- Automatically expand dependencies
- Enforce correct execution order
- Resolve required inputs safely
- Support CLI and GUI without hard-coded logic
- Scale to dozens of resources without refactoring CORE

---

## 🧠 Registry Integration Across CORE

### Planning Module

The planning module uses the registry to:

- Validate user-selected resources
- Automatically include required dependencies
- Build a correct execution DAG (topological order)

Example:
User selects Condition  
Planner expands to: Patient → Encounter → Condition

---

### Orchestrator Module

The orchestrator uses the registry to:

- Dynamically load generator functions
- Execute resources in dependency order
- Store output in correct ResourceStore buckets

No resource-specific imports exist in the orchestrator.

---

### Linking / Resolver Module

The resolver uses the registry to:

- Read required_inputs
- Resolve references such as patient_id and encounter_id
- Enforce dependency policies safely

---

### CLI & GUI (Future)

The registry enables UI layers to:

- Display supported resources dynamically
- Show dependency hints and warnings
- Auto-select required parent resources
- Stay in sync without UI code changes

---

## 📈 Scaling Guidelines (Adding New Resources)

When adding a new resource (example: Observation):

Step 1 — Add Generator  
Create generate_fhir_observation.py

Step 2 — Add Plugin  
Create resource_spec.py defining:
- resource_type = Observation
- dependencies = Patient, Encounter
- required_inputs = patient_id, encounter_id

Step 3 — Optional Linking Logic  
Extend Core/linking/resolver.py if needed

No changes are required in:
- Registry loader
- Planning module
- Orchestrator
- Exporter
- Storage

---

## ✅ Registry Rules & Best Practices

- One RESOURCE_SPEC per resource
- resource_type must be unique
- Generator import string must be stable and importable
- Dependencies must be declared explicitly
- Required inputs must match generator signature
- Do not hard-code registry entries in CORE

---

## 🧾 Summary

The Resource Registry is the foundation of scalability in the FHIRLake Generator.

It ensures that:
- CORE remains clean and generic
- Dependency management is centralized
- Planning and orchestration stay correct
- New datasets can be added safely and independently
- CLI and GUI remain dynamic and future-proof

This registry design allows the engine to grow from 3 resources to 50+ resources without architectural changes.
