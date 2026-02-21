# FHIRLake Generator - Procedure Resource Generator

This dataset defines the Procedure resource contract and a minimal synthetic generator.

## Dependencies

Required dependencies:
- Patient
- Encounter

Optional dependencies:
- Practitioner
- Organization

Required inputs:
- patient_id
- encounter_id

Optional inputs:
- practitioner_id
- organization_id

## Structure

```
Name    Flags   Card.   Type    Description & Constraints    Filter:
 Filtersdoco
.. Procedure    N        DomainResource    An action that is being or was performed on an individual or entity
+ Rule: bodyStructure SHALL only be present if Procedure.bodySite is not present

Elements defined in Ancestors: id, meta, implicitRules, language, text, contained, extension, modifierExtension
... identifier    Σ    0..*    Identifier    External Identifiers for this procedure

... basedOn    Σ    0..*    Reference(CarePlan | ServiceRequest | MedicationRequest)    A request for this procedure

... partOf    Σ    0..*    Reference(Procedure | Observation | MedicationAdministration)    Part of referenced event

... status    ?!Σ    1..1    code    preparation | in-progress | not-done | on-hold | stopped | completed | entered-in-error | unknown
Binding: EventStatus (Required)
... statusReason    Σ    0..1    CodeableConcept    Reason for current status
Binding: Procedure Not Performed Reason (SNOMED-CT) (Example)
... category    Σ    0..*    CodeableConcept    Classification of the procedure
Binding: Procedure Category Codes (SNOMED CT) (Example)

... code    Σ    0..1    CodeableConcept    Identification of the procedure
Binding: Procedure Codes (SNOMED CT) (Example)
... subject    Σ    1..1    Reference(Patient | Group | Device | Practitioner | Organization | Location)    Individual or entity the procedure was performed on
... focus    ?!Σ    0..1    Reference(Patient | Group | RelatedPerson | Practitioner | Organization | CareTeam | PractitionerRole | Specimen)    Who is the target of the procedure when it is not the subject of record only
... encounter    Σ    0..1    Reference(Encounter)    The Encounter during which this Procedure was created
... occurrence[x]    Σ    0..1        When the procedure occurred or is occurring
.... occurrenceDateTime            dateTime
.... occurrencePeriod            Period
.... occurrenceString            string
.... occurrenceAge            Age
.... occurrenceRange            Range
.... occurrenceTiming            Timing
... recorded    Σ    0..1    dateTime    When the procedure was first captured in the subject's record
... recorder    Σ    0..1    Reference(Patient | RelatedPerson | Practitioner | PractitionerRole)    Who recorded the procedure
... reported[x]    Σ    0..1        Reported rather than primary record
.... reportedBoolean            boolean
.... reportedReference            Reference(Patient | RelatedPerson | Practitioner | PractitionerRole | Organization)
... performer    ΣC    0..*    BackboneElement    Who performed the procedure and what they did
+ Rule: Procedure.performer.onBehalfOf can only be populated when performer.actor isn't Practitioner or PractitionerRole

.... function    Σ    0..1    CodeableConcept    Type of performance
Binding: Participant Roles (Example)
.... actor    ΣC    1..1    Reference(Practitioner | PractitionerRole | Organization | Patient | RelatedPerson | Device | CareTeam | HealthcareService)    Who performed the procedure
.... onBehalfOf    C    0..1    Reference(Organization)    Organization the device or practitioner was acting for
.... period        0..1    Period    When the performer performed the procedure
... location    Σ    0..1    Reference(Location)    Where the procedure happened
... reason    Σ    0..*    CodeableReference(Condition | Observation | Procedure | DiagnosticReport | DocumentReference)    The justification that the procedure was performed
Binding: Procedure Reason Codes (Example)

... bodySite    ΣC    0..*    CodeableConcept    Target body sites
Binding: SNOMED CT Body Structures (Example)

... bodyStructure        0..1    Reference(BodyStructure)    Target body structure
... outcome    Σ    0..*    CodeableReference(Observation)    The result of procedure
Binding: Procedure Outcome Codes (SNOMED CT) (Example)

... report        0..*    Reference(DiagnosticReport | DocumentReference | Composition | Bundle)    Any report resulting from the procedure

... complication    Σ    0..*    CodeableReference(Condition)    Complication following the procedure
Binding: Condition/Problem/Diagnosis Codes (Example)

... followUp        0..*    CodeableReference(ServiceRequest | PlanDefinition)    Instructions for follow up
Binding: Procedure Follow up Codes (SNOMED CT) (Example)

... note        0..*    Annotation    Additional information about the procedure

... focalDevice        0..*    BackboneElement    Manipulated, implanted, or removed device

.... action        0..1    CodeableConcept    Kind of change to device
Binding: Procedure Device Action Codes (Preferred)
.... manipulated        1..1    Reference(Device)    Device that was changed
... used        0..*    CodeableReference(Device | Medication | Substance | BiologicallyDerivedProduct)    Items used during procedure
Binding: Device Type (Example)

... supportingInfo        0..*    Reference(Any)    Extra information relevant to the procedure
```

## Usage

Install dependencies:

```bash
pip install fhir.resources faker
```

Run:

```bash
python generate_fhir_procedure.py
```
