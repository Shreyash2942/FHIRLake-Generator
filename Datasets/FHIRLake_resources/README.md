# 📦 FHIRLake Dataset Grouping Reference

This document defines how **synthetic datasets** in the **FHIRLake Generator** project are organized.

The dataset structure strictly follows the **FHIR Resource Type categorization** as defined on the official HL7 FHIR website:

👉 https://build.fhir.org/resourcelist.html

This README serves as the **authoritative reference** for dataset modularization and must be followed for all current and future datasets.

This document is intended for **contributors, data engineers, and reviewers** who need to understand the dataset taxonomy *before* any implementation or pipeline logic is introduced.

---

## 🎯 Purpose

FHIR defines a large number of healthcare resources, grouped by functional domains such as Individuals, Organizations, Devices, Clinical data, Financial data, etc.

FHIRLake Generator mirrors this grouping in order to:

- Stay aligned with FHIR industry standards  
- Enable incremental dataset development  
- Keep datasets modular and scalable  
- Avoid refactoring when new resources are added  
- Improve clarity for contributors and portfolio reviewers  

This document focuses **only on datasets**, not code, storage formats, or pipelines.

---

## 🧬 FHIR Resource Dataset Grouping (FHIR-Aligned)

### Resource Type Index – Foundation

| **Terminology** | **Conformance** | **Security** | **Documents** | **Other** |
|:---------------:|:---------------:|:------------:|:-------------:|:---------:|
| CodeSystem | CapabilityStatement | Provenance | Composition | Basic |
| ValueSet | StructureDefinition | AuditEvent | DocumentReference | Binary |
| ConceptMap | ImplementationGuide | Consent | | Bundle |
| NamingSystem | SearchParameter | | | MessageHeader |
| TerminologyCapabilities | MessageDefinition | | | OperationOutcome |
| | OperationDefinition | | | Parameters |
| | CompartmentDefinition | | | Subscription |
| | StructureMap | | | SubscriptionStatus |
| | | | | SubscriptionTopic |

---

### Resource Type Index – Base

| **Individuals** | **Entities #1** | **Entities #2** | **Workflow** | **Management** |
|-----------------|----------------|----------------|--------------|----------------|
| Patient | Organization | Substance | Task | Encounter |
| Practitioner | OrganizationAffiliation | BiologicallyDerivedProduct | Appointment | EpisodeOfCare |
| PractitionerRole | HealthcareService | Device | AppointmentResponse | Flag |
| RelatedPerson | Endpoint | DeviceAlert | Schedule | List |
| Person | Location | DeviceMetric | Slot | Library |
| Group | | NutritionProduct | | |

---

### Resource Type Index – Clinical

| **Summary** | **Diagnostics** | **Medications** | **Care Provision** | **Request & Response** |
|-------------|----------------|-----------------|--------------------|------------------------|
| AllergyIntolerance | Observation | MedicationRequest | CarePlan | Communication |
| AdverseEvent | DiagnosticReport | MedicationAdministration | CareTeam | CommunicationRequest |
| Condition | Specimen | MedicationDispense | Goal | DeviceRequest |
| Procedure | BodyStructure | MedicationStatement | ServiceRequest | DeviceAssociation |
| FamilyMemberHistory | ImagingSelection | Medication | NutritionOrder | GuidanceResponse |
| DetectedIssue | ImagingStudy | Immunization | NutritionIntake | |
| | QuestionnaireResponse | | VisionPrescription | |
| | | | RiskAssessment | |
| | | | RequestOrchestration | |

---

### Resource Type Index – Financial

| **Support** | **Billing** | **Payment** | **General** |
|-------------|-------------|-------------|-------------|
| Coverage | Claim | PaymentNotice | Account |
| CoverageEligibilityRequest | ClaimResponse | PaymentReconciliation | Contract |
| CoverageEligibilityResponse | Invoice | | ExplanationOfBenefit |
| EnrollmentRequest | | | InsurancePlan |
| EnrollmentResponse | | | InsuranceProduct |

---

### Resource Type Index – Specialized

| **Public Health & Research** | **Evidence-Based Medicine** | **Quality Reporting & Testing** | **Definitional Artifacts** | **Medication Definition** |
|------------------------------|-----------------------------|---------------------------------|----------------------------|---------------------------|
| ResearchStudy | ArtifactAssessment | Measure | ActivityDefinition | MedicinalProductDefinition |
| ResearchSubject | Evidence | MeasureReport | DeviceDefinition | PackagedProductDefinition |
| | EvidenceVariable | | EventDefinition | AdministrableProductDefinition |
| | | | ObservationDefinition | ManufacturedItemDefinition |
| | | | PlanDefinition | Ingredient |
| | | | Questionnaire | ClinicalUseDefinition |
| | | | SpecimenDefinition | RegulatedAuthorization |
| | | | ExampleScenario | SubstanceDefinition |
| | | | ActorDefinition | |
| | | | Requirements | |

---

## 📂 Dataset Directory Structure (Top-Level Groups)

```text
dataset/
└── fhirlake_resources/
    ├── foundation/     # Conformance, terminology, security, documents, interoperability
    ├── base/           # Core reference datasets (people, orgs, locations, entities)
    ├── clinical/       # Clinical events, diagnoses, observations, procedures
    ├── financial/      # Coverage, claims, billing, payments
    └── specialized/    # Research, quality, and definitional artifacts
```

---

## 🧱 Dataset Design Principles

- Each FHIR resource maps to **one dataset folder**
- Dataset folders are grouped strictly by FHIR classification
- No custom or project-specific taxonomy is introduced
- Empty folders may exist for future datasets
- Dataset structure remains stable even if implementation changes

---

## 📐 Dataset Rules & Contribution Guidelines

All datasets are synthetic, de-identified, and non-production.
Dataset structure is treated as a **contract**, not an implementation detail.

---
