# 🩺 FHIRLake Generator – Condition Resource Generator

This module generates **FHIR-style `Condition` resources** using the `fhir.resources` library and `Faker`.  
It produces **synthetic, CMS-aligned diagnosis data** linked to `Patient` and `Encounter` resources for downstream **ETL processing (Bronze → Silver → Gold)** in the **FHIRLake / MetricCare Data Lakehouse**.

---

## 📌 Overview

The generator produces **FHIR-compliant Condition JSON objects** that include:

- **SNOMED CT diagnosis codes** (Condition.code)
- **Clinical + verification status**
- **Category + severity**
- **Links to Patient & Encounter**
- **Stage + evidence (model-supported)**
- **Onset/Abatement choice fields** (FHIR choice type rules)
- **Structured annotation notes**, including:
  - CMS category + metric mapping
  - Schema version
  - Unsupported fields stored safely in `note` (so your dataset contract remains complete)

Each record is unique, randomized, and ready for ingestion into your **AWS Data Lakehouse (S3 → Glue → Hudi → Athena)** pipeline.

---

## ⚙️ Features

| Feature | Description |
|--------|-------------|
| ✅ **FHIR-style JSON** | Condition resource objects validated by `fhir.resources` |
| 🧠 **CMS-mapped SNOMED logic** | Supports mortality, infection, chronic, general groupings |
| 🔗 **Linked to Patient & Encounter** | Referential integrity across datasets |
| 🧾 **Structured `note` annotations** | Key-value notes for easy parsing in Glue/dbt |
| 🧩 **ETL-ready fields** | Compatible with Bronze/Silver/Gold transformations |
| 🔒 **Synthetic, HIPAA-safe** | No PHI; fully Faker-generated data |
| 🧰 **Contract-preserving** | Unsupported fields are stored under `note` with `unsupported.*` keys |

---

## 🧾 Example Output

```jsonc
{
  "resourceType": "Condition",
  "id": "d6a909de-5c7c-41c4-b0db-0d4a942d354b",
  "identifier": [
    {
      "system": "MetricCare-Condition",
      "value": "COND-12345678"
    }
  ],

  "clinicalStatus": {
    "text": "active"
  },
  "verificationStatus": {
    "coding": [
      { "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed" }
    ],
    "text": "Confirmed"
  },

  "category": [
    {
      "coding": [
        { "system": "http://terminology.hl7.org/CodeSystem/condition-category", "code": "encounter-diagnosis" }
      ],
      "text": "Encounter Diagnosis"
    }
  ],
  "severity": { "text": "moderate" },

  "code": {
    "coding": [
      { "system": "http://snomed.info/sct", "code": "233604007", "display": "Pneumonia" }
    ],
    "text": "Pneumonia"
  },

  "bodySite": [{ "text": "Chest" }],

  "subject": { "reference": "Patient/pat-841212b9-bd20-41ee-b03e-8b654c3a2f6c" },
  "encounter": { "reference": "Encounter/enc-6fa30a07-c7a2-4cd3-8f94-b239f16db3b8" },

  "onsetDateTime": "2025-08-14T09:32:12.441Z",
  "abatementDateTime": "2025-08-17T09:32:12.441Z",
  "recordedDate": "2025-08-14T09:32:12.441Z",

  "stage": [
    {
      "summary": { "text": "Stage II" },
      "assessment": [{ "reference": "Observation/example" }],
      "type": { "text": "Clinical staging" }
    }
  ],

  "evidence": [
    {
      "concept": { "text": "Lab confirmation" },
      "reference": { "reference": "Observation/example" }
    }
  ],

  "note": [
    { "authorString": "cms_category", "text": "Infection" },
    { "authorString": "metric", "text": "HAI Rate" },
    { "authorString": "condition_display", "text": "Pneumonia" },
    { "authorString": "version", "text": "1.0" },

    { "authorString": "unsupported.bodyStructure", "text": "BodyStructure/example" },
    { "authorString": "unsupported.recorder", "text": "Practitioner/example" },
    { "authorString": "unsupported.asserter", "text": "Practitioner/example" }
  ]
}
```
---
## 🧩 Annotation Notes Breakdown

This generator uses structured `Annotation` items inside `Condition.note` so your ETL can parse values reliably.

---

### ✅ Standard analytics notes

| authorString | Example | Description | Used For |
|--------------|---------|-------------|----------|
| `cms_category` | Infection / Death / Chronic / General | Condition grouping | CMS metric grouping |
| `metric` | HAI Rate / Mortality Rate / Readmission | Metric indicator | Gold aggregation |
| `condition_display` | Pneumonia | Human-readable name | Reporting |
| `version` | 1.0 | Schema version | Contract tracking |

---

### 🧾 Contract-preserving notes (unsupported fields)

Some FHIR fields listed in your dataset specification may not be available in your installed `fhir.resources` model.  
To keep the dataset contract complete, those fields are stored as structured notes.

| authorString | Example | Meaning |
|--------------|---------|---------|
| `unsupported.bodyStructure` | BodyStructure/example | Stored as note because model rejects field |
| `unsupported.recorder` | Practitioner/example | Stored as note because model rejects field |
| `unsupported.asserter` | Practitioner/example | Stored as note because model rejects field |

---

## 🩺 CMS Metric Alignment

| Category | Example Condition | SNOMED Code | Metric |
|---------|------------------|-------------|--------|
| ⚰️ Death | Death | 419620001 | Mortality Rate |
| 🦠 Infection | Pneumonia, Sepsis, UTI | 233604007, 91302008, 68566005 | HAI Rate |
| 💊 Chronic | Diabetes, Hypertension, COPD | 44054006, 38341003, 13645005 | Readmission / Comorbidity |
| 🧠 General | Other diagnoses | varies | Non-Infection Analytics |

---

## 🧠 FHIR Choice-Type Rule (onset[x] and abatement[x])

FHIR defines `onset[x]` and `abatement[x]` as **choice types**.

That means:

### ✅ Only **one onset field** can exist at a time:
- `onsetDateTime`
- `onsetAge`
- `onsetPeriod`
- `onsetRange`
- `onsetString`

### ✅ Only **one abatement field** can exist at a time:
- `abatementDateTime`
- `abatementAge`
- `abatementPeriod`
- `abatementRange`
- `abatementString`

The generator randomly selects **one valid choice** for onset and **one valid choice** for abatement.

---

## 🧱 Data Lakehouse Integration

| Layer | Action | Output Table |
|------|--------|--------------|
| 🥉 Bronze | Ingest raw JSON from S3 | `bronze_condition` |
| 🥈 Silver | Normalize and derive flags (`is_death`, `is_infection`, `is_chronic`) | `silver_condition` |
| 🥇 Gold | Aggregate CMS metrics | `gold_mortality_rate`, `gold_hai_rate`, `gold_readmission_rate` |

### Silver-derived fields

```text
is_death      -> cms_category = 'Death'
is_infection  -> cms_category = 'Infection'
is_chronic    -> cms_category = 'Chronic'
length_days   -> (abatementDateTime - onsetDateTime) when both exist
```

---

## 📤 Output Path Structure

```text
s3://<bucket-name>/bronze/condition/YYYY/MM/DD/condition_<timestamp>.json
```

Each file can contain multiple Condition records linked to Patients and Encounters.

---

## ⚙️ Usage

### Install dependencies
```bash
pip install fhir.resources faker
```

### Run the generator
```bash
python generate_fhir_condition.py
```

### Output
- Prints formatted JSON to console
- Can be extended to write files to disk or upload to S3

---

## ✅ Deliverables

| File | Description |
|------|-------------|
| `generate_fhir_condition.py` | Generates CMS-aligned Condition resources |
| `README.md` | Documentation and dataset contract reference |
| `bronze_condition.py` | Glue ingestion job (optional) |
| `silver_condition.py` | Cleaning and classification job (optional) |
| `gold_hai_rate.py` | Infection metrics aggregation (optional) |
| `gold_mortality_rate.py` | Mortality metrics aggregation (optional) |
| `gold_readmission_rate.py` | Readmission / comorbidity aggregation (optional) |

---

## 🛠️ Notes for Future Expansion

If you later install a `fhir.resources` version that supports:

- `bodyStructure`
- `recorder`
- `asserter`
- R4-style evidence `{ code, detail }`

those fields can be migrated from `Annotation.note` back into native FHIR fields **without breaking ETL or analytics logic**.
