# 🏥 FHIRLake Generator – Encounter Resource Generator (FHIR R5)

This module generates **FHIR R5 Encounter resources** using the `fhir.resources` library and `Faker`.  
It produces **synthetic, HIPAA-safe JSON** that simulates hospital visits and supports downstream analytics in a data lake / lakehouse.

---

## 📌 Overview

The Encounter generator creates realistic visit records tied to a specific **FHIR Patient** via `subject.reference`.  
Each record includes:

- Admission + discharge timestamps (`actualPeriod`)
- Encounter classification (`class_fhir`) and visit type (`type`)
- Department/service line (`serviceType`)
- Staff participation (`participant`)
- Facility responsibility (`serviceProvider`)
- Location history (`location`)
- Virtual visit details (`virtualService`) when applicable
- Admission workflow details (`admission`)
- Billing/account linkage (`account`)
- Clinical context (`reason`, `diagnosis`)
- Patient logistics/preferences (`dietPreference`, `specialArrangement`, `specialCourtesy`)

> ✅ This implementation is **schema-aligned to your installed Encounter fields** (FHIR R5 build).  
> ❌ `businessStatus` is **not supported** by your installed model, so we store the same concept via **custom extensions**.

---

## ⚙️ Features

| Feature | Description |
|--------|-------------|
| ✅ **FHIR R5 Encounter structure** | Uses `actualPeriod`, `plannedStartDate`, `plannedEndDate`, `subjectStatus`, etc. |
| 🏥 **Realistic visit scenarios** | Inpatient / outpatient / emergency / urgent care categories |
| 🧑‍⚕️ **Participants included** | Encounter participants reference a Practitioner UUID |
| 📍 **Location tracking** | Includes unit/department and location period |
| 💻 **Virtual visits supported** | `virtualService` populated for video/phone encounters |
| 🧾 **Admission and billing-ready** | `admission` and `account` populated |
| 🔗 **Analytics-friendly references** | Links to Patient, Condition, Organization, Location, CareTeam, EpisodeOfCare |
| 🧩 **Safe “business status” mapping** | Stored using custom `extension` fields (since `businessStatus` is unsupported) |

---

## 🧩 Field Coverage (What This Generator Populates)

This generator intentionally targets the Encounter fields available in your environment:

- `identifier`, `status`, `class_fhir`, `priority`, `type`
- `serviceType`, `subject`, `subjectStatus`
- `episodeOfCare`, `basedOn`, `careTeam`, `partOf`
- `serviceProvider`, `participant`
- `appointment`, `virtualService`
- `actualPeriod`, `plannedStartDate`, `plannedEndDate`, `length`
- `reason`, `diagnosis`
- `account`, `dietPreference`, `specialArrangement`, `specialCourtesy`
- `admission`, `location`
- `contained` (present as empty list by design)
- `extension`

---

## 🧠 “businessStatus” Compatibility Note

The HL7 reference structure includes:

- `businessStatus.code`
- `businessStatus.type`
- `businessStatus.effectiveDate`

Your installed Encounter model does **not** accept the top-level field `businessStatus`, so this generator stores these values using **FHIR extensions**:

- `encounter-businessStatus-code`
- `encounter-businessStatus-type`
- `encounter-businessStatus-effectiveDate`

This keeps the dataset:
- ✅ valid under your schema
- ✅ searchable in analytics pipelines
- ✅ consistent across environments

---

## 🧮 Metric / Analytics Alignment

This Encounter dataset supports analytics metrics such as:

| Metric | Derived From | Example Use |
|--------|--------------|-------------|
| Average Length of Stay (ALOS) | `actualPeriod.start/end` or `length` | avg LOS by facility/department |
| Encounter Volume | `type`, `class_fhir`, `serviceType` | utilization by service line |
| Bed/Unit Utilization | `status`, `location.status` | active encounters per unit |
| Readmission (logic downstream) | `subject`, `actualPeriod.end` | re-encounter within N days |
| Virtual Visit Share | `virtualService` | percent telehealth visits |

---

## 🧾 Example Output (Simplified)

```json
{
  "resourceType": "Encounter",
  "id": "3f2e2a3a-1f1b-4bf8-8f0c-3d2e87a75a22",
  "status": "completed",
  "identifier": [
    { "system": "FHIRLake-ENC", "value": "ENC-348221" },
    { "system": "FHIRLake-VISIT", "value": "V-59382" }
  ],
  "class": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
          "code": "IMP",
          "display": "inpatient encounter"
        }
      ],
      "text": "inpatient"
    }
  ],
  "type": [{ "text": "Inpatient" }],
  "subject": { "reference": "Patient/9d8d8d7c-3b7b-4f10-9e72-0f9c1f84b3a1" },
  "actualPeriod": {
    "start": "2025-05-08T11:17:26.000Z",
    "end": "2025-05-12T11:17:26.000Z"
  },
  "serviceProvider": {
    "reference": "Organization/org-001",
    "display": "MetricCare Hospital - Charlotte"
  },
  "location": [
    {
      "location": {
        "reference": "Location/6a1fb4d1-2c9a-4be0-9d1e-aaaa1111bbbb",
        "display": "ICU"
      },
      "status": "active",
      "form": { "text": "ward" },
      "period": {
        "start": "2025-05-08T11:17:26.000Z",
        "end": "2025-05-12T11:17:26.000Z"
      }
    }
  ],
  "extension": [
    {
      "url": "http://fhirlake.io/fhir/StructureDefinition/encounter-businessStatus-code",
      "valueString": "awaiting-tests"
    },
    {
      "url": "http://fhirlake.io/fhir/StructureDefinition/encounter-contained-policy",
      "valueString": "No contained resources; related entities are referenced externally."
    }
  ]
}
```
---
## 🚀 Usage

python generate_fhir_encounter.py

---

## 🪶 Data Lake / Lakehouse Flow

FHIR Generators → S3 (Bronze) → Glue → Hudi/Iceberg → Athena/Redshift → BI Dashboards

---

## 🧱 Integration Points

| Module | Linkage |
|--------|---------|
| Patient Generator | `subject.reference` |
| Condition Generator | `reason.value[]` and `diagnosis.condition[]` reference Conditions |
| Organization Dataset | `serviceProvider.reference` |
| Location Dataset | `location.location.reference` |
| Glue / ETL Jobs | Read JSON → flatten → load analytics tables |

---

## 🧰 Dependencies

pip install faker fhir.resources

---

## 📦 Deliverables

| File | Purpose |
|------|---------|
| `generate_fhir_encounter.py` | Encounter resource generator |
| `README.md` | Module documentation |
| `sample_output.json` | Optional sample output |

---

## ✅ Outcome

- Generates **FHIR R5 schema-aligned Encounter records**
- Includes realistic admission/discharge, participants, locations, services, and virtual visits
- Stores business workflow details safely via **FHIR extensions**
- Ready for analytics pipelines and data warehouse ingestion

---
🧬 Part of the FHIRLake Generator – Synthetic Healthcare Data Framework