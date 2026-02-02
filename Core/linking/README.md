# 🔗 Linking & References

## Purpose
The `linking/` folder ensures resources correctly reference each other using valid FHIR references.

Examples:
- Encounter must reference a Patient
- Condition should reference Encounter (and optionally Patient)
- Observation typically references Patient and/or Encounter

This layer prevents broken datasets.

---

## Files

### `reference_graph.py`
Defines the allowed reference relationships (who can reference whom).
Think of it as a dependency reference map.

### `resolver.py`
Provides helper logic to:
- pick valid references from RunContext pools
- return references in FHIR format like `Patient/<id>`
- enforce safety (don’t reference resources that don’t exist yet)

---

## Rules
- Keep reference rules consistent with FHIR best practices
- Never create references to missing resources
- All reference selection must be deterministic when seed is provided
