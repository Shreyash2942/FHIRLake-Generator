# 📍 FHIRLake Generator – Location Resource Generator (FHIR R5)

This module generates **FHIR R5 Location resources** using the `fhir.resources` Python library and `Faker`.  
It produces **synthetic, HIPAA-safe healthcare facility data** that represents physical and virtual care locations such as hospitals, buildings, wards, rooms, beds, clinics, labs, imaging centers, and telehealth locations.

The generated data is designed to be:
- **FHIR-compliant**
- **Analytics-ready**
- **Hierarchy-aware** (Location → partOf → Location)
- **Dataset-contract safe** for data lakes and warehouses

---

## 📌 Overview

The Location generator creates realistic healthcare location records that can be linked to:
- Patients (via Encounter / Service delivery)
- Organizations (facility ownership)
- Endpoints (technical access points)
- Other Locations (facility hierarchy)

Each Location resource supports:
- Facility metadata (name, type, form)
- Operational status (beds, rooms)
- Geographic positioning
- Contact and availability details
- Virtual service connectivity
- Enterprise analytics use cases

> ✅ Aligned with your **FHIRLake dataset-first design philosophy**  
> ⚠️ Unsupported FHIR datatypes are preserved using **contract-safe extensions**

---

## 🧬 Supported FHIR Resource

- **Location** (FHIR R5)

FHIR Reference:  
https://build.fhir.org/location.html

---

## 🧱 Dataset Structure (FHIR JSON with Comments)

Below is the **analytics-aligned dataset structure** produced by this generator.  
Comments explain **why each field exists** and **how it’s used downstream**.

```jsonc
{
  "resourceType": "Location",                 // FHIR resource type
  "id": "uuid",                               // Unique Location identifier

  "identifier": [
    {
      "use": "usual",                         // Primary identifier usage
      "type": { "text": "Facility Location Code" },
      "system": "MetricCare-LOC",              // Internal enterprise namespace
      "value": "LOC-839201"                    // Join key for analytics
    }
  ],

  "status": "active",                         // active | suspended | inactive
  "operationalStatus": {                      // Operational state (beds/rooms)
    "system": "https://fhirlake.dev/codes/bed-status",
    "code": "operational",
    "display": "Operational"
  },

  "name": "North Wing Ward 3",                 // Human-readable name
  "alias": ["NW Ward 3"],                      // Alternate or legacy names

  "description": "Inpatient ward for general care and monitoring",

  "mode": "instance",                         // instance | kind

  "code": [
    {
      "coding": [
        {
          "system": "https://fhirlake.dev/codes/location-code",
          "code": "NC",
          "display": "Administrative Code"
        }
      ],
      "text": "Administrative Location Code"
    }
  ],

  "type": [
    {
      "coding": [
        {
          "system": "https://fhirlake.dev/codes/service-type",
          "code": "inpatient",
          "display": "Inpatient Care"
        }
      ],
      "text": "Inpatient Care"
    }
  ],

  "contact": [
    {
      "purpose": { "text": "Official Location Contact" },
      "telecom": [
        { "system": "phone", "value": "+1-704-555-0192", "use": "work" },
        { "system": "email", "value": "ward3@hospital.org", "use": "work" }
      ]
    }
  ],

  "address": {
    "line": ["123 Health Ave"],
    "city": "Charlotte",
    "state": "NC",
    "postalCode": "28262",
    "country": "US"
  },

  "form": {
    "coding": [
      {
        "system": "https://fhirlake.dev/codes/location-form",
        "code": "ward",
        "display": "Ward"
      }
    ],
    "text": "Ward"
  },

  "position": {
    "latitude": 35.3074,                       // Geo latitude (WGS84)
    "longitude": -80.7357,                     // Geo longitude (WGS84)
    "altitude": 229.5                          // Optional altitude
  },

  "managingOrganization": {
    "reference": "Organization/metriccare-health"
  },

  "partOf": {
    "reference": "Location/building-a"         // Parent Location (hierarchy)
  },

  "characteristic": [
    {
      "coding": [
        {
          "system": "https://fhirlake.dev/codes/location-characteristic",
          "code": "wheelchair",
          "display": "Wheelchair Accessible"
        }
      ],
      "text": "Wheelchair Accessible"
    }
  ],

  "hoursOfOperation": {
    "availableTime": [
      {
        "daysOfWeek": ["mon","tue","wed","thu","fri"],
        "availableStartTime": "08:00",
        "availableEndTime": "17:00"
      }
    ]
  },

  "virtualService": [
    {
      "channelType": { "text": "video" },
      "addressUrl": "https://meet.example.org/839-201-4821",
      "additionalInfo": ["Join code: 839-201-4821"]
    }
  ],

  "endpoint": [
    { "reference": "Endpoint/telehealth-01" }
  ]
}
```

---

## 🧩 Contract-Preserving Strategy (Unsupported Fields)

Some FHIR datatypes may not exist in your installed `fhir.resources` build  
(e.g. `ExtendedContactDetail`, `Availability`, `VirtualServiceDetail`).

To **avoid breaking your dataset contract**, unsupported fields are stored as extensions:

```json
{
  "extension": [
    {
      "url": "https://fhirlake.dev/unsupported/contact",
      "valueString": "{...serialized JSON...}"
    }
  ]
}
```

✅ This guarantees:
- Schema stability
- Forward compatibility
- Safe analytics ingestion

---

## 🏗️ Location Hierarchy Support

This generator supports **real-world healthcare location hierarchies**:

```
Hospital
 └── Building
      └── Wing
           └── Ward
                └── Room
                     └── Bed
```

Hierarchy is modeled using:
- `Location.partOf`

---

## 📊 Analytics & Data Engineering Use Cases

The Location dataset enables:
- Bed occupancy analytics
- Ward-level utilization
- Facility capacity planning
- Telehealth vs in-person analysis
- CMS quality metrics alignment
- Geospatial reporting

---

## 🔌 Integration Points

This module integrates seamlessly with:
- **Encounter** (where care occurred)
- **Patient** (location of service)
- **Organization** (facility ownership)
- **Endpoint** (technical access)
- **FHIR Bundles / NDJSON / CSV exports**

---

## 🚀 Next Extensions (Planned)

- Bulk hierarchical location generation
- CSV / Parquet flattening mappings
- Snowflake / Redshift dimension modeling
- CMS facility-level metrics alignment

---

## ⚠️ Disclaimer

All generated data is **synthetic**, **HIPAA-safe**, and intended **only for testing, learning, and analytics development**.

No real patient, provider, or facility data is used.

---

## 👤 Author

**Shreyash Patel**  
FHIRLake Generator – Synthetic Healthcare Data Platform
