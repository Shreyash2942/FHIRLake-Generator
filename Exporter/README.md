# 📦 Exporter Module

The **Exporter module** is responsible for converting generated datasets into **ingestion-ready file formats**.

It defines *how data is serialized*, not *where it is stored*. This clear separation ensures that format logic, storage logic, and dataset governance remain independent and scalable.

---

## 🎯 Purpose

The Exporter module exists to:

- Serialize FHIR resources into multiple ingestion formats
- Support interoperability, analytics, and semantic use cases
- Keep format-specific logic isolated and reusable
- Enable easy extension with new formats without refactoring

The module strictly follows the **dataset-first architecture** and **FHIR-aligned dataset contract** defined in:

- `Datasets/FHIRLake_resources/README.md`

---

## 🧠 Design Principles

The Exporter module follows these core principles:

- **Serialization only**  
  Exporters convert in-memory data structures into bytes or text formats.

- **No storage responsibility**  
  Exporters do not manage file paths, directories, retention, or destinations.

- **FHIR-aligned**  
  Exported data preserves FHIR resource structure and semantics.

- **Pluggable & extensible**  
  New formats can be added without impacting existing exporters.

---

## 📦 Supported Export Formats (Ingestion Layer)

The following formats are supported or planned for ingestion workflows:

| Format | Purpose |
|------|--------|
| JSON | Canonical FHIR resource representation |
| NDJSON | Bulk ingestion, Spark, Glue, streaming |
| CSV | Inspection and lightweight analytics |
| XML | FHIR interoperability support |
| Turtle (RDF) | Semantic web and graph-based use cases |

These formats are selected based on **FHIR standards** and **data engineering best practices**.

FHIR defines data structure, not storage format.

---

## 📂 Module Structure

```text
src/fhirlake/exporters/
├── __init__.py
├── base.py              # Abstract exporter interface
├── json_exporter.py     # FHIR JSON exporter
├── ndjson_exporter.py   # NDJSON (FHIR Bulk-style)
├── csv_exporter.py      # Flattened CSV exporter
├── xml_exporter.py      # FHIR XML exporter (planned)
└── turtle_exporter.py  # RDF / Turtle exporter (planned)
```

---

## 🧩 Exporter Interface

All exporters implement a shared interface defined in `base.py`.

Key characteristics:
- Accepts a FHIR resource type and iterable of records
- Returns serialized output as bytes
- Stateless and reusable

This ensures consistency across all formats.

---

## 🔄 Typical Usage Flow

```text
Generators → Exporter → Storage → Output Files
```

---

## 🚦 Scope & Non-Goals

### In scope:
- Serialization logic
- Format-specific transformations
- Ingestion-ready outputs

### Out of scope:
- File system access
- Folder naming or retention policies
- Dataset taxonomy or grouping
- Validation or business rules

---

## ➕ Adding a New Exporter

To add a new format:

1. Create a new exporter file in this directory
2. Extend the base exporter interface
3. Implement the `export()` method
4. Register the exporter (if using a factory)
5. Update documentation if needed

New exporters must:
- Preserve FHIR semantics
- Follow dataset-first rules
- Remain storage-agnostic

---

## 🔐 Compliance Notes

- Exporters may be used with **synthetic or real data**
- HIPAA and FHIR do not restrict file formats
- Security and access control are handled outside this module

This project uses **synthetic data only**.

---

## 📌 Guiding Principle

> **Exporters define format, not governance.**
