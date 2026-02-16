# 🧬 Base FHIR Dataset Layer

## 📌 Purpose
The `base/` folder represents the **core, canonical dataset layer** of the FHIRLake Generator project.

It contains the **foundational FHIR resource definitions and generators** that form the backbone of all synthetic healthcare datasets produced by this platform.

This layer follows **HL7 FHIR standards strictly** and serves as the **authoritative source of truth** for:
- Folder structure
- Resource placement
- Generator responsibilities
- Dataset contracts

All higher-level datasets, extensions, or future domains must build on top of this base layer.

---

## 🧠 Design Philosophy

The base dataset layer is designed with the following principles:

- **FHIR-aligned**: Folder structure mirrors FHIR resource taxonomy
- **Dataset-first**: Structure is defined before pipelines or execution logic
- **Composable**: Each resource is generated independently
- **Deterministic-ready**: Supports reproducible generation via Core runtime
- **Extensible**: New resources can be added without modifying existing ones

---
### Resource Type Index – Base

| **Individuals** | **Entities #1** | **Entities #2** | **Workflow** | **Management** |
|-----------------|----------------|----------------|--------------|----------------|
| Patient | Organization | Substance | Task | Encounter |
| Practitioner | OrganizationAffiliation | BiologicallyDerivedProduct | Appointment | EpisodeOfCare |
| PractitionerRole | HealthcareService | Device | AppointmentResponse | Flag |
| RelatedPerson | Endpoint | DeviceAlert | Schedule | List |
| Person | Location | DeviceMetric | Slot | Library |
| Group | | NutritionProduct | | |

---

## 🗂️ Folder Structure

```text
base/
└── Individuals/
    ├── Patient/
    │   ├── fhir_patient_generator.py
    │   ├── README.md
    │   └── sample_output/
    │
    ├── Encounter/        # planned / in-progress
    │   ├── fhir_encounter_generator.py
    │   ├── README.md
    │   └── sample_output/
    │
    └── Condition/        # planned / in-progress
        ├── fhir_condition_generator.py
        ├── README.md
        └── sample_output/
```

---

## 📦 What Belongs in `base/`

The base layer includes:
- Core FHIR resources (Patient, Encounter, Condition, etc.)
- Resource generators that:
  - Produce valid FHIR JSON
  - Do not handle export formats
  - Do not handle storage or orchestration
- Sample outputs for validation and documentation

---

## ❌ What Does NOT Belong in `base/`

- Export logic (CSV, NDJSON, JSON writers)
- Runtime orchestration
- Dependency planning
- Storage backends
- UI or CLI logic

Those concerns belong to:
- `Core/`
- `Exporter/`
- `Storage/`
- `CLI/`

---

## 🧩 Generator Contract (Important)

Each generator in the base layer must expose one of the following interfaces.

### Option A (Recommended)

```python
def generate(ctx, config) -> list[dict]:
    """
    Generate FHIR resources for this resource type.

    - ctx: RunContext from core (shared state + pools)
    - config: merged defaults + profile overrides
    """
    ...
```

### Option B (Supported)

```python
class Generator:
    def generate(self, ctx, config) -> list[dict]:
        ...
```

Rules:
- Returned objects **must** be valid FHIR JSON dictionaries
- `resourceType` should be present or will be injected by Core
- Generators must be deterministic when a seed is provided

---

## 🔗 Relationship Handling

Generators **must not manually resolve dependencies**.

All inter-resource relationships (e.g., Encounter → Patient) are handled by:
- `Core/linking/reference_graph.py`
- `Core/linking/resolver.py`

Generators should:
- Request references from `RunContext`
- Never hardcode foreign keys, IDs, or execution order

---

## ➕ Adding a New Base Resource

To add a new FHIR resource to the base layer:

1. Create a new folder under `base/Individuals/`
   ```text
   base/Individuals/Observation/
   ```
2. Add the following files:
   ```text
   fhir_observation_generator.py
   README.md
   sample_output/
   ```
3. Register the resource in:
   ```text
   Core/registry/resource_registry.py
   ```
4. Define reference rules in:
   ```text
   Core/linking/reference_graph.py
   ```

No Core logic changes are required.

---

## 📎 Notes
- All data generated in this layer is **synthetic**
- No real patient or clinical data is used
- This layer is safe for education, testing, analytics, and portfolio use
