# 🏢 FHIRLake Generator – Organization Resource Generator (FHIR R5+)

This module generates **FHIR R5 Organization** resources using the `fhir.resources` (Pydantic FHIR models) library and `Faker`.  
It produces **synthetic, HIPAA-safe JSON** that simulates real-world healthcare organizations (health systems, hospitals, departments, payers, insurers, government agencies).

---

## ✅ What this generator does

- Generates **FHIR R5 Organization** resources with realistic:
  - identifiers
  - organization types (provider, department, payer, etc.)
  - names + aliases
  - descriptions
  - contact details (best-effort)
  - parent/child org relationships (`partOf`)
  - endpoints (`endpoint`)
  - qualifications/accreditations (`qualification`)

- Supports **contract-preserving fallback** for fields/datatypes not supported by your installed `fhir.resources`:
  - If setting a field fails validation or the field doesn’t exist, it is stored in:
    - `Organization.extension[]`
    - `url = "https://fhirlake.dev/unsupported/<fieldPath>"`
    - `valueString = "<json/text>"`

This ensures your **dataset contract stays complete**, even if library support is missing.

---

## 📦 Output formats supported

This generator outputs a **FHIR Organization model** object, which you can export as:
- ✅ JSON (single resource)
- ✅ NDJSON (one resource per line)
- ✅ Bundles (if your orchestrator wraps resources)
- ✅ CSV (flattening handled by Exporter layer)

---

## 🧾 FHIR R5 Fields Covered (Target Schema)

This generator targets the following Organization fields:

- `identifier`
- `active`
- `type`
- `name`
- `alias`
- `description`
- `contact` *(ExtendedContactDetail – may be unsupported in some builds → stored in extension fallback)*
- `partOf`
- `endpoint`
- `qualification[]` *(may be unsupported in some builds → stored in extension fallback)*

---

## 🧩 Dataset Structure (Organization) with Comments

Below is the **analytics-friendly dataset structure** your generator produces.  
Use this as your **dataset contract reference**.

```jsonc
{
  "resourceType": "Organization",                 // FHIR resource type
  "id": "8d4e7c3d-77d1-4a1b-9f6a-0f6d4c0b3f7c",   // Unique organization UUID

  "meta": {                                       // Resource metadata
    "versionId": "1",
    "lastUpdated": "2026-02-02T16:45:10Z"
  },

  "identifier": [                                 // Identifies organization across systems
    {
      "use": "usual",                             // Identifier usage
      "type": { "text": "Facility / Organization Code" }, // Identifier category
      "system": "MetricCare-ORG",                 // Namespace/system
      "value": "ORG-104933"                       // Joinable organization key
    }
  ],

  "active": true,                                 // Whether record is active

  "type": [                                       // Kind of organization
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/organization-type",
          "code": "prov",
          "display": "Healthcare Provider"
        }
      ],
      "text": "Healthcare Provider"
    }
  ],

  "name": "MetricCare General Hospital",           // Display name

  "alias": [                                      // Alternative names (brand, abbreviation, legacy)
    "MC General",
    "MetricCare GH"
  ],

  "description": "Large acute-care hospital providing inpatient and outpatient services.", // Markdown description

  "contact": [                                    // ExtendedContactDetail (best-effort)
    {
      "purpose": { "text": "Official Organization Contact" }, // Contact purpose
      "name": { "text": "Main Office" },           // Contact label/name (if supported)
      "telecom": [                                 // Telecom list
        { "system": "phone", "value": "+1-704-555-0199", "use": "work" },
        { "system": "email", "value": "info@metriccare.example", "use": "work" },
        { "system": "url", "value": "https://metriccare.example", "use": "work" }
      ],
      "address": {                                 // Mailing address (if supported)
        "line": ["100 Healthcare Blvd"],
        "city": "Charlotte",
        "state": "NC",
        "postalCode": "28202",
        "country": "US"
      }
    }
  ],

  "partOf": {                                     // Parent organization reference
    "reference": "Organization/parent-org-uuid",
    "display": "MetricCare Health System"
  },

  "endpoint": [                                   // Technical endpoints (FHIR Endpoint)
    {
      "reference": "Endpoint/fhir-api-uuid",
      "display": "FHIR R5 API Endpoint"
    }
  ],

  "qualification": [                              // Accreditations / licenses / certs
    {
      "identifier": [
        {
          "use": "official",
          "type": { "text": "Qualification / Accreditation ID" },
          "system": "MetricCare-QUAL",
          "value": "QUAL-775120"
        }
      ],

      "code": {                                   // REQUIRED: coded representation
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
            "code": "HOS",
            "display": "Hospital Accreditation"
          }
        ],
        "text": "Hospital Accreditation"
      },

      "status": { "text": "Active" },             // Status/progress

      "period": {                                 // Validity period
        "start": "2024-01-01",
        "end": "2027-12-31"
      },

      "issuer": {                                 // Issuing organization
        "reference": "Organization/issuer-org-uuid",
        "display": "National Accreditation Board"
      }
    }
  ]
}
```
---
## 🧷 Contract-Preserving Fallback (Unsupported Fields)

Some `fhir.resources` builds may not fully support the following fields:

- `Organization.contact` (ExtendedContactDetail)
- `Organization.qualification` (backbone structure in some versions)

When this happens, the generator **preserves the data** under:

- `Organization.extension[]`
  - `url = "https://fhirlake.dev/unsupported/<fieldPath>"`
  - `valueString = "<json/text>"`

### Example: Unsupported fields stored as extensions

```jsonc
{
  "extension": [
    {
      "url": "https://fhirlake.dev/unsupported/contact",
      "valueString": "[{\"purpose\":{\"text\":\"Official Organization Contact\"},\"telecom\":[...]}]"
    },
    {
      "url": "https://fhirlake.dev/unsupported/qualification",
      "valueString": "[{\"code\":{\"text\":\"Hospital Accreditation\"},\"status\":{\"text\":\"Active\"},...}]"
    }
  ]
}
```
✅ This approach keeps your dataset contract stable for **ETL pipelines** and **analytics layers**, even when library support is incomplete.

---

## ⚙️ Configuration

The generator supports configuration via:

- `OrganizationGeneratorConfig`

### Key configuration knobs

- `identifier_system` (default: `MetricCare-ORG`)
- `probability_alias`
- `probability_description`
- `probability_part_of`
- `probability_endpoint`
- `probability_qualification`

---

## ▶️ Example Usage

```python
from your_module_path.organization_generator import OrganizationGenerator

gen = OrganizationGenerator(seed=42)

org = gen.generate_organization(
    part_of_ref="Organization/metriccare-health-system",
    endpoint_refs=None,
    qualification_issuer_ref="Organization/national-accreditation-board"
)

print(org.model_dump(exclude_none=True))
```
## 🔗 Linking Strategy (Recommended)

When generating multiple resources:

1. Generate **Organization** resources first (health system).
2. Generate child organizations (hospitals, departments).
3. Link them using:
   - `partOf = Reference("Organization/<parentId>")`

If you generate **Endpoint** resources, link them using:
- `endpoint = [Reference("Endpoint/<id>")]`

---

## 🧠 ETL / Analytics Notes

For analytics and lakehouse processing:

- Use `identifier[0].value` as a **stable join key** (e.g., `ORG-xxxxxx`)
- Use `type[0].coding[0].code` for **organization grouping** (provider, payer, etc.)
- Use `partOf.reference` for **hierarchy rollups**:
  - Health system → Facility → Department
- Parse fallback fields from `extension[]` where:
  - `url` starts with `https://fhirlake.dev/unsupported/`

---

## 📁 Suggested File Placement

Recommended module paths:

- `Core/generators/organization_generator.py`
- or `Generators/organization_generator.py`

Dataset contract documentation:

- `Datasets/FHIRLake_resources/base/Organization/README.md`
