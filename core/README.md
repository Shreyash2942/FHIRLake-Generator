# Core Engine - FHIRLake Generator

## Overview
The `core` module is the central execution engine of the FHIRLake Generator project.

It is responsible for coordinating configuration loading, dependency resolution, runtime state management, and orchestration of dataset generation. The Core module contains no resource-specific logic and is designed to be small, reusable, and scalable.

This separation allows new FHIR resources to be added without modifying the engine itself.

---

## Responsibilities
The Core engine handles:

- Loading global defaults and execution profiles
- Registering available FHIR resources and their generators
- Building dependency graphs between resources
- Planning execution order (DAG-based)
- Managing runtime state and reference resolution
- Tracking run metadata and output manifests

---

## Module Structure

```text
core/
+-- __init__.py                          # Core package exports
+-- __main__.py                          # python -m core entrypoint
¦
+-- config/                              # Configuration layer (no business logic)
¦   +-- Profiles/                        # Predefined run profiles for CLI/GUI
¦
+-- engine/                              # Engine package
¦   +-- __init__.py                      # Engine exports
¦   +-- __main__.py                      # python -m core.engine entrypoint
¦   +-- scripts/                         # Engine implementation
¦       +-- engine.py                    # run_engine entrypoint
¦       +-- engine_models.py             # ExportOptions, EngineResult
¦       +-- logging_utils.py             # Engine logging helpers
¦       +-- main.py                      # Engine CLI
¦
+-- registry/                            # Single source of truth for resources
¦   +-- __init__.py                      # Public registry API
¦   +-- models.py                        # ResourceSpec dataclass + DependencyPolicy
¦   +-- loader.py                        # Auto-discovers resource_spec.py plugins
¦   +-- registry.py                      # Builds & caches RESOURCE_REGISTRY
¦
+-- runtime/                             # Execution-time state (FHIR-agnostic)
¦   +-- __init__.py                      # Runtime package marker
¦   +-- context.py                       # RunContext (run_id, seed, RNG, timestamps)
¦   +-- store.py                         # ResourceStore (in-memory resources + pools)
¦   +-- manifest.py                      # Run manifest / run_summary.json writer
¦
+-- planning/                            # Planning & dependency resolution
¦   +-- __init__.py                      # Exposes planner APIs
¦   +-- models.py                        # UserRequest, ExecutionPlan dataclasses
¦   +-- builder.py                       # Thin builder facade
¦   +-- planner.py                       # Planner implementation
¦
+-- resolver/                            # Relationship & reference resolution
¦   +-- __init__.py                      # Exposes resolver
¦   +-- resolver.py                      # ReferenceResolver
¦   +-- strategies.py                    # Selection strategies
¦   +-- models.py                        # ResolvedInputs dataclass
¦   +-- exceptions.py                    # Resolver errors
¦
+-- orchestrator/                        # Execution engine (core loop)
    +-- __init__.py                      # Exposes run_job + helpers
    +-- run.py                           # Generic runner
```

---

## Call Graph

```text
CLI/GUI
  +- core.engine.scripts.engine.run_engine
       +- core.orchestrator.run.run_job
       ¦    +- core.planning.planner.build_plan
       ¦    +- core.resolver.resolver.Resolver.resolve
       ¦    +- core.orchestrator.run._call_generate
       ¦    +- core.runtime.store.ResourceStore.add_many_from_spec
       ¦    +- core.runtime.store.ResourceStore.register_id / register_link
       ¦    +- core.runtime.manifest.write_manifest
       ¦
       +- core.engine.scripts.logging_utils.make_engine_logger
       +- core.engine.scripts.engine._write_run_summary
       +- core.engine.scripts.engine._export_resources
            +- Exporter.plan_json_exports / plan_ndjson_exports
            +- Storage.write_text (LocalStorage or other backend)
```

---

## Core Concepts

### RunContext
A shared object passed to all generators that stores:
- Generated resource IDs
- Reference pools (patients, encounters, etc.)
- Counters and runtime metadata

This guarantees referential integrity across all resources.

### Resource Registry
The registry defines:
- Which resources exist
- Where their generator scripts live
- Their dependency requirements

This allows plug-and-play resource expansion.

### Dependency & Execution Planning
Dependencies are modeled as a graph:
- Patient -> Encounter -> Condition
- Planner builds a DAG
- Runner executes generators in a safe order

---

## What Core Does NOT Do
- Generate FHIR resources
- Export data to files
- Handle storage backends
- Parse CLI arguments

Those concerns belong to other modules.

---

## Extending the System
To add a new resource:
1. Add generator under `Datasets/`
2. Register it in `resource_registry.py`
3. Define relationships in `reference_graph.py`

No Core logic changes required.

---

## Design Philosophy
- Strict separation of concerns
- Dependency-driven execution
- Deterministic, repeatable runs
- Enterprise-scale extensibility
