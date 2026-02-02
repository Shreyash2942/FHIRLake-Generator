# 🗄️ Storage Module

The **Storage module** is responsible for **persisting exported datasets** produced by the FHIRLake Generator project.

This module defines *where and how data is saved*, while remaining completely agnostic to:
- How data is generated (Generators)
- How data is serialized (Exporters)
- How datasets are defined (Dataset Contract)

The Storage module is the **final step** in the FHIRLake data flow.

---

## 🎯 Purpose

The Storage module exists to:

- Save exported datasets to a target destination
- Enforce consistent folder and file naming conventions
- Support multiple storage backends (local, cloud, etc.)
- Enable reproducible, run-based outputs
- Keep persistence logic isolated and reusable

This module does **not** create data and does **not** format data.

---

## 🧠 Design Principles

The Storage module follows these core principles:

- **Storage-only responsibility**  
  Handles file persistence only — no generation or serialization.

- **Backend-agnostic**  
  Supports local filesystem now; cloud backends (S3, ADLS, GCS) can be added later.

- **Run-based isolation**  
  Each execution writes to its own output directory.

- **Safe writes**  
  Uses atomic or overwrite-safe operations where possible.

- **Dataset-first alignment**  
  Output paths reflect dataset taxonomy and resource type.

---

## 📂 Module Structure

```text
src/fhirlake/storage/
├── README.md
├── writer.py              # Core save/write orchestration
├── paths.py               # Output directory & file naming rules
├── manifest.py            # Run metadata (optional but recommended)
│
└── backends/              # Storage backends
    ├── __init__.py
    ├── local_fs.py        # Local filesystem backend
    └── s3.py              # Cloud backend (planned)
```

---

## 🧩 Responsibilities

### What the Storage module DOES:
- Create output directories
- Write bytes/text to files
- Organize outputs by run, format, and resource
- Optionally write run manifests

### What the Storage module DOES NOT do:
- Generate synthetic data
- Convert data formats
- Define dataset taxonomy
- Apply business logic or validation

---

## 🔄 Typical Data Flow

```text
Generators → Exporters → Storage → Output Files
```

---

## 📁 Example Output Layout

```text
data/output/
└── run_2026-02-01T140512Z/
    ├── json/
    │   └── Patient.json
    ├── ndjson/
    │   └── Patient.ndjson
    ├── csv/
    │   └── patients.csv
    ├── xml/
    │   └── Patient.xml
    ├── turtle/
    │   └── Patient.ttl
    └── manifest.json
```

---

## 📄 Run Manifest (Optional)

The Storage module may generate a **manifest file** per run containing:

- Run ID and timestamp
- Dataset profile used
- Resources generated and record counts
- Export formats
- Notes or metadata

Manifests improve:
- Auditability
- Debugging
- Reproducibility

---

## 🔐 Compliance & Safety

- Storage supports **synthetic data** by default
- HIPAA and FHIR do not restrict storage formats
- Access control and encryption are backend responsibilities
- This project does not store real PHI

---

## ➕ Adding a New Storage Backend

To add a new backend (e.g., S3):

1. Create a new backend module under `backends/`
2. Implement the required write interface
3. Keep backend logic isolated from exporters and generators
4. Update documentation if needed

---

## 📌 Guiding Principle

> **Storage defines where data lives — not what it is or how it looks.**
