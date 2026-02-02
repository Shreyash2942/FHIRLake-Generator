FHIRLake – FHIR Patient Data Generator
=====================================

This module generates fully synthetic, FHIR-compliant Patient resources using
the fhir.resources library and Faker.

The generated data is HIPAA-safe and designed for healthcare analytics,
data engineering pipelines, and FHIR-based data lakehouse architectures.

This generator acts as the foundational entity for downstream resources
such as Encounter, Condition, and Observation.

--------------------------------------------------------------------

Overview
--------

The Patient generator produces FHIR R4–compliant Patient JSON objects with
realistic but non-identifiable administrative and demographic attributes.

Each Patient record is suitable for:
- Analytics testing
- ETL pipeline validation
- Master Patient Index (MPI) simulations
- Population health and CMS-style metrics
- Cloud data lake ingestion (S3 / Azure / GCS)

The script intentionally balances realism with performance by including
commonly used Patient attributes while keeping the JSON lightweight.

--------------------------------------------------------------------

Key Capabilities
----------------

- FHIR R4 Patient resource structure
- UUID-based immutable Patient.id
- Separate Medical Record Number (MRN) identifiers
- Synthetic demographic data (gender, birthDate)
- Address and telecom details for regional analytics
- Language preferences using BCP-47 codes
- Emergency and guardian contact modeling
- Deceased status simulation for mortality analytics
- Organization and primary care provider references
- Optional patient linking for MPI and duplicate scenarios

--------------------------------------------------------------------

FHIR Elements Generated
----------------------

This script may generate the following Patient elements depending on
randomized inclusion logic:

- identifier
- active
- name
- telecom
- gender
- birthDate
- deceasedDateTime
- address
- maritalStatus
- multipleBirthBoolean or multipleBirthInteger
- photo
- contact
- communication
- generalPractitioner
- managingOrganization
- link

All fields follow official FHIR cardinality and datatype rules.

--------------------------------------------------------------------

Folder Structure
----------------

ingestion/
    └── script/
         └── patient/
              ├── patient_generator.py
              ├── README.md
              └── sample_output/

--------------------------------------------------------------------

Dependencies
------------

The script depends on the following Python libraries:

- fhir.resources
  Used to construct and validate FHIR Patient resources
  according to the official HL7 schema.

- Faker
  Used to generate realistic synthetic names, addresses,
  phone numbers, and dates.

Install dependencies from the project root:

    python -m pip install -r requirements.txt

--------------------------------------------------------------------

How the Script Works
-------------------

1. Patient Identity Creation
   - Generates a UUID for Patient.id
   - Creates a synthetic MRN stored in Patient.identifier
   - Ensures resource IDs remain immutable

2. Demographic Generation
   - Random administrative gender
   - Adult birth dates
   - Optional deceasedDateTime with logical constraints

3. Contact & Address Modeling
   - Adds phone and email contact points
   - Generates structured postal addresses
   - Enables geographic and regional analysis

4. Language & Communication
   - Assigns patient communication language
   - Uses BCP-47 compliant language codes
   - Supports preferred language indicators

5. Administrative Attributes
   - Marital status
   - Multiple birth indicators
   - Patient photos (URL-based placeholder attachments)

6. Relationships & Providers
   - Emergency or guardian contacts
   - Managing organization (custodian of record)
   - Optional primary care provider reference

7. Patient Linking
   - Supports Patient.link for:
     - Duplicate records
     - Patient index references
     - Distributed patient records

--------------------------------------------------------------------

FHIR Compliance Notes
--------------------

- Patient.id is never reused or repurposed
- MRN is stored in Patient.identifier (FHIR best practice)
- Contact entries satisfy invariant pat-1
- Only one preferred language is assigned
- Null fields are excluded from output JSON
- Resource validates using fhir.resources models

--------------------------------------------------------------------

Running the Generator
---------------------

From the project root directory:

    python ingestion/script/patient/patient_generator.py

The script will:
- Generate a complete FHIR Patient JSON object
- Print formatted output to the console
- Exclude unused optional fields
- Suggest a cloud-style filename for storage

--------------------------------------------------------------------

Output Characteristics
----------------------

- Format: JSON
- Schema: FHIR R4 Patient
- Size: Lightweight, analytics-friendly
- Content: Fully synthetic, non-identifiable
- Usage: Safe for demos, portfolios, and public repos


---
Patient Dataset Structure (FHIR R4 – Synthetic)
==============================================

Below is the logical structure of a synthetic FHIR Patient resource generated
by this module. Inline comments explain the purpose of each field and how it
is used in analytics and data engineering pipelines.

This representation is for documentation only.

```text
{
  "resourceType": "Patient",          # FHIR resource type identifier

  "id": "d4058000-1077-4de6-94ae-a29518310063",
                                      # Immutable UUID for the patient record
                                      # Used as the primary join key across resources
                                      # (Encounter, Condition, Observation)

  "active": true,                     # Indicates whether the patient record
                                      # is currently in active use

  "meta": {
    "versionId": "1",                 # Resource version for audit and tracking
    "lastUpdated": "2025-10-13T02:22:22.245910Z"
                                      # Timestamp when the resource was generated
                                      # or last modified
  },

  "identifier": [
    {
      "use": "usual",                 # Commonly used identifier
      "type": {
        "text": "Medical Record Number"
      },                              # Identifier type description

      "system": "MetricCare-MRN",     # Internal identifier namespace
                                      # Allows differentiation from other systems

      "value": "MC-479336"             # Synthetic MRN value
                                      # Used for human-facing identification
    }
  ],

  "name": [
    {
      "use": "official",              # Official legal name
      "family": "Patel",               # Family (last) name
      "given": ["Shreyas", "Ramesh"]   # Given (first and middle) names
    }
  ],

  "telecom": [
    {
      "system": "phone",              # Contact method type
      "value": "+1-704-555-0198",      # Synthetic phone number
      "use": "mobile"                 # Preferred phone usage
    },
    {
      "system": "email",
      "value": "patient@example.org", # Synthetic email address
      "use": "home"
    }
  ],

  "gender": "male",                   # Administrative gender
                                      # Used for demographic segmentation

  "birthDate": "1985-11-25",           # Date of birth
                                      # Used to derive age groups for analytics

  "address": [
    {
      "use": "home",                  # Address usage type
      "line": ["742 Evergreen Terrace"],
                                      # Street address
      "city": "Rossfort",              # City for regional analysis
      "state": "MP",                   # State or province
      "postalCode": "28105",           # Postal or ZIP code
      "country": "USA"                 # Country
    }
  ],

  "maritalStatus": {
    "text": "Married"                 # Marital or civil status
                                      # Optional administrative attribute
  },

  "multipleBirthBoolean": false,       # Indicates whether the patient
                                      # was part of a multiple birth
                                      # (can also be an integer birth order)

  "communication": [
    {
      "language": {
        "coding": [
          {
            "system": "urn:ietf:bcp:47",
            "code": "ar",              # BCP-47 language code
            "display": "Arabic"
          }
        ],
        "text": "Arabic"               # Human-readable language
      },
      "preferred": true                # Preferred language indicator
    }
  ],

  "contact": [
    {
      "relationship": [
        {
          "text": "Emergency Contact" # Relationship to the patient
        }
      ],
      "name": {
        "family": "Patel",
        "given": ["Anita"]
      },
      "telecom": [
        {
          "system": "phone",
          "value": "+1-704-555-0123",
          "use": "mobile"
        }
      ],
      "organization": {
        "reference": "Organization/org-mountainview",
        "display": "MountainView Healthcare"
      }
    }
  ],

  "generalPractitioner": [
    {
      "reference": "Organization/org-mountainview",
      "display": "MountainView Healthcare Primary Care"
    }
  ],

  "managingOrganization": {
    "reference": "Organization/org-mountainview",
                                      # Organization that owns and maintains
                                      # the patient record
    "display": "MountainView Healthcare"
  },

  "deceasedDateTime": "2006-11-20T00:00:00Z"
                                      # Indicates patient is deceased
                                      # Used directly in mortality analytics
                                      # and CMS-style outcome measures
}
```

--------------------------------------------------------------------

Notes
-----

- All values shown are synthetic and non-identifiable
- Optional fields may be omitted depending on random generation logic
- Null or unused fields are excluded from final JSON output
- Structure follows FHIR R4 Patient resource specification


--------------------------------------------------------------------

Analytics & Data Engineering Use Cases
--------------------------------------

Generated Patient records can be used for:

- Population health analysis
- Mortality rate calculations
- Regional healthcare trends
- Patient-provider attribution
- CMS-style quality metrics
- Joining with Encounter and Condition data

--------------------------------------------------------------------

Future Enhancements
-------------------

- Profile-based generation (Minimal / Full / US Core-like)
- Batch patient generation
- Referential integrity enforcement
- Export to CSV and NDJSON
- Automated schema validation tests
- Cloud storage integration

--------------------------------------------------------------------

License
-------

This module generates synthetic healthcare data only.
No real patient information is included.

--------------------------------------------------------------------

Author
------

Shreyas Patel
Data Engineer | Healthcare Analytics | AWS | Python | FHIR
