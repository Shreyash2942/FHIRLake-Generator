# Adding New Resources (Dataset Guide)

This guide explains how to add a new FHIR resource generator to FHIRLake-Generator, wire dependencies, and make it available in CLI/engine runs.

## 1) Create the resource folder

Follow the existing dataset layout under `Datasets/FHIRLake_resources/...`.

Example:

```
Datasets/
  FHIRLake_resources/
    clinical/
      Summary/
        Observation/
          generate_fhir_observation.py
          resource_spec.py
          README.md (optional)
```

Keep one resource per folder and one `resource_spec.py` per resource.

## 2) Implement the generator

Your generator must expose a new-style entrypoint:

```
# generate_fhir_observation.py

def generate(ctx, store, inputs, count):
    # ctx: RunContext (seed, run_id, timestamp)
    # store: ResourceStore (register_id, pools)
    # inputs: resolved inputs (required + optional)
    # count: number of resources to generate
    resources = []
    # ... build resources here ...
    # store.register_id("Observation", obs_id)
    return resources
```

Required inputs come from `resource_spec.required_inputs`.
Optional inputs come from `resource_spec.optional_inputs`.

## 3) Create the resource_spec.py

Use `ResourceSpec` to register your resource with the engine.

Example:

```
from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Observation",
    bucket="observations",
    generator="Datasets.FHIRLake_resources.clinical.Summary.Observation.generate_fhir_observation:generate",

    # Required dependencies (used for planning order + count validation)
    dependencies=["Patient", "Encounter"],
    required_inputs=["patient_id", "encounter_id"],

    # Optional dependencies (only included if user opts in)
    optional_dependencies=["Practitioner"],
    optional_inputs=["practitioner_id"],

    description="Synthetic Observation linked to Patient and Encounter.",
)
```

## 4) Decide dependencies and optional links

Rules:
- `dependencies` are required. Planner expands them and enforces counts.
- `optional_dependencies` are only included if the user opts in.
- `required_inputs` are enforced by the Resolver.
- `optional_inputs` are resolved if available, otherwise `None`.

If you want strict referential integrity for optional links, instruct users to include optional datasets in the interactive CLI when prompted.

## 5) Register IDs in your generator

Always register generated IDs so downstream resources can reference them:

```
store.register_id("Observation", obs_id)
```

This creates a pool like `observation_ids` for resolver use.

## 6) Update any generator to use optional inputs correctly

If you accept optional inputs, use them when present and fall back to random values or omit fields when absent, based on your design.

Example:

```
practitioner_id = inputs.get("practitioner_id")
if practitioner_id:
    resource["performer"] = [{"reference": f"Practitioner/{practitioner_id}"}]
else:
    # fallback random or omit
    resource["performer"] = [{"reference": f"Practitioner/{uuid4()}"}]
```

## 7) Run an interactive check

Use interactive CLI to verify dependencies and counts:

```
python -m cli.commands.interactive
```

When prompted, choose whether to include optional datasets to make cross-links real.

## 8) Common pitfalls

- Missing `RESOURCE_SPEC` or wrong import path in `generator`.
- Not registering IDs via `store.register_id`.
- Putting optional inputs into `required_inputs` (causes failures when pool is empty).
- Forgetting to add required dependencies to `dependencies` (planner will not order correctly).

## 9) Where to look for examples

- `Datasets/FHIRLake_resources/clinical/Summary/Condition/`
- `Datasets/FHIRLake_resources/base/Management/Encounter/`
- `Datasets/FHIRLake_resources/base/Entities_1/Location/`

## 10) Notes on required vs optional

- Required dependencies guarantee referential integrity.
- Optional dependencies give flexibility. If user does not opt in, optional references will be random/fallback and not guaranteed to resolve to real resources.

```

Save this file as:
Documents/README_Adding_Resources.md