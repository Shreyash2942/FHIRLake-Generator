# FHIRLake Generator - MedicationRequest Resource Generator

This dataset defines the MedicationRequest resource contract and a minimal synthetic generator.

## Dependencies

Required dependencies:
- Patient

Optional dependencies:
- Encounter
- Practitioner
- Organization

Required inputs:
- patient_id

Optional inputs:
- encounter_id
- practitioner_id
- organization_id

## Structure

```
Name    Flags   Card.   Type    Description & Constraints    Filter:
 Filtersdoco
.. MedicationRequest    N        DomainResource    Ordering of medication for patient or group

Elements defined in Ancestors: id, meta, implicitRules, language, text, contained, extension, modifierExtension
... identifier        0..*    Identifier    External ids for this request

... basedOn    Σ    0..*    Reference(CarePlan | MedicationRequest | ServiceRequest | RequestOrchestration)    A plan or request that is fulfilled in whole or in part by this medication request

... priorPrescription        0..1    Reference(MedicationRequest)    Reference to an order/prescription that is being replaced by this MedicationRequest
... groupIdentifier    Σ    0..1    Identifier    Composite request this is part of
... status    ?!Σ    1..1    code    active | on-hold | ended | stopped | completed | cancelled | entered-in-error | draft | unknown
Binding: medicationrequest Status (Required)
... statusReason        0..1    CodeableConcept    Reason for current status
Binding: medicationRequest Status Reason Codes (Example)
... statusChanged        0..1    dateTime    When the status was changed
... intent    ?!Σ    1..1    code    proposal | plan | order | original-order | reflex-order | filler-order | instance-order | option (immutable)
Binding: medicationRequest Intent (Required)
... category        0..*    CodeableConcept    Grouping or category of medication request
Binding: MedicationRequest Category Codes (Example)

... priority    Σ    0..1    code    routine | urgent | asap | stat
Binding: RequestPriority (Required)
... doNotPerform    ?!Σ    0..1    boolean    If true, indicates the provider is ordering a patient should not take the specified medication
... medication    Σ    1..1    CodeableReference(Medication)    Medication to be taken
Binding: SNOMED CT Medication Codes (Example)
... subject    Σ    1..1    Reference(Patient | Group)    Individual or group for whom the medication has been requested
... informationSource        0..*    Reference(Patient | Practitioner | PractitionerRole | RelatedPerson | Organization | Group)    The person or organization who provided the information about this request, if the source is someone other than the requestor

... encounter        0..1    Reference(Encounter)    Encounter created as part of encounter/admission/stay
... supportingInformation        0..*    Reference(Any)    Information to support fulfilling of the medication

... authoredOn    Σ    0..1    dateTime    When request was initially authored
... requester    Σ    0..1    Reference(Practitioner | PractitionerRole | Organization | Patient | RelatedPerson | Device)    Who/What requested the Request
... isRecordOfRequest    Σ    0..1    boolean    Whether this is record of a Medication Request or the actual request itself
... performerType    Σ    0..1    CodeableConcept    Desired kind of performer of the medication administration
Binding: Medication Intended Performer Role (Extensible)
... performer        0..*    Reference(Practitioner | PractitionerRole | Organization | Patient | DeviceDefinition | RelatedPerson | CareTeam | HealthcareService | Group)    Intended performer of administration

... device        0..*    CodeableReference(DeviceDefinition)    Intended type of device for the administration

... recorder        0..1    Reference(Practitioner | PractitionerRole)    Person who entered the request
... reason    Σ    0..*    CodeableReference(Condition | Observation | DiagnosticReport | Procedure | AllergyIntolerance)    Reason or indication for ordering or not ordering the medication
Binding: Condition/Problem/Diagnosis Codes (Example)

... courseOfTherapyType        0..1    CodeableConcept    Overall pattern of medication administration
Binding: medicationRequest Course of Therapy Codes (Extensible)
... insurance        0..*    Reference(Coverage | ClaimResponse)    Associated insurance coverage

... note        0..*    Annotation    Information about the prescription

... effectiveTiming[x]        0..1        Period over which the medication is to be taken, can be specified as a duration or a range
.... effectiveTimingDuration            Duration
.... effectiveTimingRange            Range
.... effectiveTimingPeriod            Period
... dosageInstruction        0..1    DosageDetails    Specific instructions for how the medication should be taken
... dispenseRequest        0..1    BackboneElement    Medication supply authorization
.... initialFill        0..1    BackboneElement    First fill details
..... quantity        0..1    SimpleQuantity    First fill quantity
..... duration        0..1    Duration    First fill duration
.... dispenseInterval        0..1    Duration    Minimum period of time between dispenses
.... validityPeriod        0..1    Period    Time period supply is authorized for
.... numberOfRepeatsAllowed        0..1    unsignedInt    Number of refills authorized
.... quantity        0..1    SimpleQuantity    Amount of medication to supply per dispense
.... expectedSupplyDuration        0..1    Duration    Number of days supply per dispense
.... dispenser        0..1    Reference(Organization)    Intended performer of dispense
.... dispenserInstruction        0..*    CodeableConcept    Additional information for the dispenser
Binding: medicationrequest dispenser-instructions (Example)

.... doseAdministrationAid        0..1    CodeableConcept    Type of adherence packaging to use for the dispense
Binding: Medication Dose Aids (Example)
.... destination        0..1    Reference(Location)    Where the medication is expected to be delivered
... substitution        0..1    BackboneElement    Any restrictions on medication substitution
.... allowed[x]        1..1        Whether substitution is allowed or not
Binding: ActSubstanceAdminSubstitutionCode icon (Preferred)
..... allowedBoolean            boolean
..... allowedCodeableConcept            CodeableConcept
.... reason        0..1    CodeableConcept    Why should (not) substitution be made
Binding: SubstanceAdminSubstitutionReason icon (Example)
... eventHistory        0..*    Reference(Provenance)    A list of events of interest in the lifecycle
```

## Usage

Install dependencies:

```bash
pip install fhir.resources faker
```

Run:

```bash
python generate_fhir_medication_request.py
```
