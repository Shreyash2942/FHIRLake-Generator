# FHIRLake Generator - Observation Resource Generator

This dataset defines the Observation resource contract and a minimal synthetic generator.

## Dependencies

Required dependencies:
- Patient
- Encounter

Optional dependencies:
- Practitioner

Required inputs:
- patient_id
- encounter_id

Optional inputs:
- practitioner_id

## Structure

```
Name    Flags   Card.   Type    Description & Constraints    Filter:
 Filtersdoco
.. Observation    N        DomainResource    Measurements and simple assertions
+ Rule: Observation.dataAbsentReason SHALL only be present if Observation.value[x] is not present
+ Rule: If Observation.component.code is the same as Observation.code, then Observation.value SHALL NOT be present (the Observation.component.value[x] holds the value).
+ Rule: Observation.component.dataAbsentReason SHALL only be present if Observation.component.value[x] is not present
+ Rule: if organizer exists and organizer = true, then value[x], dataAbsentReason and component SHALL NOT be present
+ Warning: All observations SHOULD have a performer

Elements defined in Ancestors: id, meta, implicitRules, language, text, contained, extension, modifierExtension
... identifier    Σ    0..*    Identifier    Business Identifier for observation

... basedOn    Σ    0..*    Reference(CarePlan | DeviceRequest | MedicationRequest | NutritionOrder | ServiceRequest)    Fulfills plan, proposal or order

... triggeredBy        0..*    BackboneElement    Triggering observation(s)

.... observation    Σ    1..1    Reference(Observation)    Triggering observation
.... type    Σ    1..1    code    reflex | repeat | re-run
Binding: triggered Bytype (Required)
.... reason        0..1    string    Reason that the observation was triggered
... partOf    Σ    0..*    Reference(MedicationAdministration | MedicationDispense | MedicationStatement | Procedure | Immunization | ImagingStudy)    Part of referenced event

... status    ?!Σ    1..1    code    registered | specimen-in-process | preliminary | final | amended | corrected | appended | cancelled | entered-in-error | unknown | cannot-be-obtained
Binding: Observation Status (Required)
... category        0..*    CodeableConcept    Classification of type of observation
Binding: Observation Category Codes (Preferred)

... code    ΣC    1..1    CodeableConcept    Type of observation (code / type)
Binding: LOINC codes with Observation or Both (Example)
... subject    Σ    0..1    Reference(Patient | Group | Device | Location | Organization | Procedure | Practitioner | Medication | Substance | BiologicallyDerivedProduct | NutritionProduct)    Who and/or what the observation is about
... focus    ?!Σ    0..*    Reference(Any)    What the observation is about, when it is not about the subject of record

... organizer    ΣC    0..1    boolean    This observation organizes/groups a set of sub-observations
... encounter    Σ    0..1    Reference(Encounter)    Healthcare event during which this observation is made. If you need to place the observation within one or more episodes of care, use the workflow-episodeOfCare extension
... effective[x]    Σ    0..1        Clinically relevant time/time-period for observation
.... effectiveDateTime            dateTime
.... effectivePeriod            Period
.... effectiveTiming            Timing
.... effectiveInstant            instant
... issued    Σ    0..1    instant    Date/Time this version was made available
... performer    Σ    0..*    Reference(Practitioner | PractitionerRole | Organization | CareTeam | Patient | RelatedPerson | HealthcareService | Group)    Who is responsible for the observation

... value[x]    ΣC    0..1        Actual result
.... valueQuantity            Quantity
.... valueCodeableConcept            CodeableConcept
.... valueString            string
.... valueBoolean            boolean
.... valueInteger            integer
.... valueRange            Range
.... valueRatio            Ratio
.... valueSampledData            SampledData
.... valueTime            time
.... valueDateTime            dateTime
.... valuePeriod            Period
.... valueAttachment            Attachment
... dataAbsentReason    C    0..1    CodeableConcept    Why the result value is missing
Binding: Data Absent Reason (Extensible)
... interpretation        0..*    CodeableConcept    High, low, normal, etc
Binding: Observation Interpretation Codes (Extensible)

... interpretationContext        0..*    CodeableReference(Any)    Context for understanding the observation
Binding: Observation Interpretation Context Codes (Example)

... note        0..*    Annotation    Comments about the observation

... bodySite        0..1    CodeableConcept    DEPRECATED: Observed body part
Binding: SNOMED CT Body Structures (Example)
... bodyStructure        0..1    CodeableReference(BodyStructure)    Observed body structure
Binding: SNOMED CT Body Structures (Example)
... method        0..1    CodeableConcept    How it was done
Binding: Observation Methods (Example)
... specimen    C    0..1    Reference(Specimen | Group)    Specimen used for this observation
+ Rule: If Observation.specimen is a reference to Group, the group can only have specimens
... device        0..1    Reference(Device | DeviceMetric)    A reference to the device that generates the measurements or the device settings for the device
... referenceRange    C    0..*    BackboneElement    Provides guide for interpretation
+ Rule: Must have at least a low or a high or text

.... low    C    0..1    Quantity    Low Range, if relevant
+ Rule: If low.comparator exists, it must be '>=' or '>'.
.... high    C    0..1    Quantity    High Range, if relevant
+ Rule: If high.comparator exists, it must be '<=' or '<'.
.... normalValue        0..1    CodeableConcept    Normal value, if relevant
Binding: Observation Reference Range Normal Value Codes (Example)
.... type        0..1    CodeableConcept    Reference range qualifier
Binding: Observation Reference Range Meaning Codes (Preferred)
.... appliesTo        0..*    CodeableConcept    Reference range population
Binding: Observation Reference Range Applies To Codes (Example)

.... age        0..1    Range    Applicable age range, if relevant
.... text    C    0..1    markdown    Text based reference range in an observation
... hasMember    Σ    0..*    Reference(Observation | QuestionnaireResponse)    Related resource that belongs to the Observation group

... derivedFrom    Σ    0..*    Reference(DocumentReference | ImagingStudy | ImagingSelection | QuestionnaireResponse | Observation)    Related resource from which the observation is made

... component    ΣC    0..*    BackboneElement    Component results

.... code    ΣC    1..1    CodeableConcept    Type of component observation (code / type)
Binding: LOINC codes with Observation or Both (Example)
.... value[x]    ΣC    0..1        Actual component result
..... valueQuantity            Quantity
..... valueCodeableConcept            CodeableConcept
..... valueString            string
..... valueBoolean            boolean
..... valueInteger            integer
..... valueRange            Range
..... valueRatio            Ratio
..... valueSampledData            SampledData
..... valueTime            time
..... valueDateTime            dateTime
..... valuePeriod            Period
..... valueAttachment            Attachment
.... dataAbsentReason    C    0..1    CodeableConcept    Why the component result value is missing
Binding: Data Absent Reason (Extensible)
.... interpretation        0..*    CodeableConcept    High, low, normal, etc
Binding: Observation Interpretation Codes (Extensible)

.... referenceRange        0..*    see referenceRange    Provides guide for interpretation of component result value
```

## Usage

Install dependencies:

```bash
pip install fhir.resources faker
```

Run:

```bash
python generate_fhir_observation.py
```
