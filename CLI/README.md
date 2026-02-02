# 🖥️ Command Line Interface (CLI)

## 📌 Overview
The `CLI` module provides the **user-facing entry point** for the FHIRLake Generator platform.

It translates command-line arguments into structured execution requests and delegates all generation logic to the Core engine.

The CLI is intentionally thin and declarative.

---

## 🎯 Responsibilities
The CLI is responsible for:

- Parsing command-line arguments
- Selecting execution profiles
- Passing runtime options to the Core engine
- Triggering dataset generation
- Providing user-friendly feedback

---

## 🗂️ Module Structure

```text
CLI/
├── fhirlake.py        # Command entrypoint
└── README.md
```

---

## ▶️ Execution Flow

```text
User Command
 ↓
CLI Argument Parsing
 ↓
Load Config + Profile
 ↓
Invoke Core Orchestrator
 ↓
Dataset Generation
 ↓
Export + Storage
```

---

## 🧪 Example Usage (Planned)

```bash
fhirlake generate \
  --profile small_demo \
  --resources Patient,Encounter,Condition \
  --formats json,ndjson,csv \
  --output ./output
```

---

## ⚙️ CLI Design Principles
- No business logic
- No resource-specific rules
- No file-format handling
- Delegates everything to Core

This keeps the CLI stable even as the system grows.

---

## 🔮 Planned Enhancements
- Validation commands
- Dry-run / plan preview
- Dataset statistics summary
- Manifest inspection
- Cloud execution flags

---

## 📎 Notes
- CLI is optional for library usage
- Core engine can be invoked programmatically
- CLI exists for ease of use and demos
