# 🤝 Contributing to FHIRLake Generator

Thank you for your interest in contributing to **FHIRLake Generator** 🎉  
This project is designed to be **FHIR-aligned, dataset-first, and modular**, and we welcome contributions that follow these principles.

Before contributing, please read this document carefully.

---

## 📌 Key Reference (Must Read)

FHIRLake Generator follows a **dataset contract** defined in:

📄 **Dataset Grouping Reference**  
`Datasets/FHIRLake_resources/README.md`

This document is the **single source of truth** for:
- Dataset grouping
- FHIR resource taxonomy
- Folder structure
- Contribution rules at the dataset level

> Any contribution that violates the dataset contract will not be accepted.

---

## 🎯 What You Can Contribute

You can contribute in several ways:

### ✅ Dataset Scaffolding
- Adding new FHIR resource folders (only if defined in the dataset contract)
- Adding group-level README files
- Improving dataset documentation

### ✅ Dataset Generation Logic (Code)
- Implementing generators for existing dataset folders
- Improving data realism while keeping it synthetic
- Adding new output formats (CSV, NDJSON, Parquet, etc.)

### ✅ Documentation
- Improving READMEs
- Adding examples
- Clarifying dataset usage

---

## 🚦 Contribution Rules (Dataset-First)

### 1️⃣ Follow the FHIR Dataset Contract

All datasets **must**:
- Match the official FHIR Resource Type Index  
  https://build.fhir.org/resourcelist.html
- Appear in the dataset tables before implementation
- Be placed in the correct FHIR group and sub-group

No custom dataset categories are allowed.

---

### 2️⃣ One Resource = One Dataset

- Each FHIR resource maps to **exactly one dataset folder**
- Do not merge multiple FHIR resources into one dataset
- Do not split one resource across multiple folders

Examples:
- ✅ `base/Individuals/Patient/`
- ❌ `base/Individuals/Patient_Practitioner/`

---

### 3️⃣ Dataset Structure Comes Before Code

Before writing code:
- Ensure the dataset folder exists
- Ensure the resource is listed in the Dataset Grouping Reference
- Confirm correct placement

Implementation without structure approval is discouraged.

---

### 4️⃣ Synthetic Data Only

FHIRLake Generator **must never** generate real or identifiable data.

Rules:
- No real names, addresses, or identifiers
- No real medical record numbers
- Randomized but realistic values only

This project is for:
- Analytics testing
- Education
- Development
- Portfolio demonstration

---

### 5️⃣ Incremental Contributions Are Encouraged

- You do not need to implement all resources at once
- Placeholder folders are allowed
- Focus on correctness and clarity over volume

---

## 🛠️ How to Add a New Dataset (High-Level)

1. Check the **Dataset Grouping Reference**
2. Confirm the FHIR resource exists in the tables
3. Create the dataset folder (if not already present)
4. Add or update documentation
5. Implement generation logic (optional, separate PR)

---

## 🧪 Testing Expectations

If contributing code:
- Include basic tests when possible
- Ensure referential integrity (e.g., Encounter → Patient)
- Avoid breaking existing generators

---

## 📦 Pull Request Checklist

Before submitting a PR:

- [ ] Dataset placement follows FHIR grouping
- [ ] README or documentation updated if needed
- [ ] No real or identifiable data introduced
- [ ] Changes are modular and focused

---

## 🧭 Guiding Principle

> **Dataset structure is a contract, not an implementation detail.**

Design decisions favor:
- Standards over shortcuts
- Clarity over speed
- Long-term scalability over quick wins

Thank you for contributing to FHIRLake Generator! 🚀
