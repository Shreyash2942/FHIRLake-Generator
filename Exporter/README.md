# Exporter Module

The Exporter module is responsible for converting generated datasets into ingestion-ready file formats.

It defines how data is serialized, not where it is stored. This clear separation ensures that format logic, storage logic, and dataset governance remain independent and scalable.

---

## Purpose

The Exporter module exists to:

- Serialize FHIR resources into multiple ingestion formats
- Support interoperability, analytics, and semantic use cases
- Keep format-specific logic isolated and reusable
- Enable easy extension with new formats without refactoring

The module strictly follows the dataset-first architecture and FHIR-aligned dataset contract defined in:

- `Datasets/FHIRLake_resources/README.md`

---

## Design Principles

The Exporter module follows these core principles:

- Serialization only
  Exporters convert in-memory data structures into bytes or text formats.

- No storage responsibility
  Exporters do not manage file paths, directories, retention, or destinations.

- FHIR-aligned
  Exported data preserves FHIR resource structure and semantics.

- Pluggable and extensible
  New formats can be added without impacting existing exporters.

---

## Supported Export Formats (Ingestion Layer)

The following formats are supported or planned for ingestion workflows:

| Format | Purpose |
|------|--------|
| JSON | Canonical FHIR resource representation |
| NDJSON | Bulk ingestion, Spark, Glue, streaming |
| CSV | Inspection and lightweight analytics |
| XML | FHIR interoperability support |
| Turtle (RDF) | Semantic web and graph-based use cases |

FHIR defines data structure, not storage format.

---

## Module Structure

```text
Exporter/
+-- __init__.py
+-- JSON/
¦   +-- __init__.py
¦   +-- json_writer.py
+-- NDJSON/
¦   +-- __init__.py
¦   +-- ndjson_writer.py
+-- CSV/
¦   +-- __init__.py
¦   +-- csv_writer.py
+-- XML/
¦   +-- __init__.py
¦   +-- xml_writer.py
+-- Turtle/
    +-- __init__.py
    +-- turtle_writer.py
```

---

## Exporter Interface

Each exporter exposes two functions:
- `serialize_<format>(records)` returns string content
- `plan_<format>_exports(store_resources, ...)` returns planned outputs

Storage writes are handled by the engine via `Storage.write_text()`.

---

## Typical Usage Flow

```text
Generators -> Exporter -> Storage -> Output Files
```

---

## Scope and Non-Goals

In scope:
- Serialization logic
- Format-specific transformations
- Ingestion-ready outputs

Out of scope:
- File system access
- Folder naming or retention policies
- Dataset taxonomy or grouping
- Validation or business rules

---

## Adding a New Exporter

To add a new format:

1. Create a new exporter file in this directory
2. Implement `serialize_<format>` and `plan_<format>_exports`
3. Register the functions in `Exporter/__init__.py`
4. Update documentation if needed

New exporters must:
- Preserve FHIR semantics
- Follow dataset-first rules
- Remain storage-agnostic

---

## Compliance Notes

- Exporters may be used with synthetic or real data
- HIPAA and FHIR do not restrict file formats
- Security and access control are handled outside this module

This project uses synthetic data only.

---

## Guiding Principle

Exporters define format, not governance.
