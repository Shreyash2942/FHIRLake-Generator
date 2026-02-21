# FHIRLake Generator - Claim Resource Generator

This dataset defines the Claim resource contract and a minimal synthetic generator.

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
.. Claim    N        DomainResource    Claim, Pre-determination or Pre-authorization

Elements defined in Ancestors: id, meta, implicitRules, language, text, contained, extension, modifierExtension
... identifier        0..*    Identifier    Business Identifier for claim

... traceNumber        0..*    Identifier    Number for tracking

... status    ?!Σ    1..1    code    active | cancelled | draft | entered-in-error
Binding: Financial Resource Status Codes (Required)
... statusReason    Σ    0..1    string    Reason for status change
... type    Σ    1..1    CodeableConcept    Category or discipline
Binding: Claim Type Codes (Extensible)
... subType        0..1    CodeableConcept    More granular claim type
Binding: Example Claim SubType Codes (Example)
... use    Σ    1..1    code    claim | preauthorization | predetermination
Binding: Use (Required)
... subject    Σ    1..1    Reference(Patient | Group)    The recipient(s) of the products and services
... billablePeriod    Σ    0..1    Period    Relevant time frame for the claim
... created    Σ    1..1    dateTime    Resource creation date
... enterer        0..1    Reference(Practitioner | PractitionerRole | Patient | RelatedPerson)    Author of the claim
... insurer    Σ    0..1    Reference(Organization)    Target
... provider    Σ    0..1    Reference(Practitioner | PractitionerRole | Organization)    Party responsible for the claim
... priority    Σ    0..1    CodeableConcept    Desired processing urgency
Binding: Process Priority Codes (Preferred)
... fundsReserve        0..1    CodeableConcept    For whom to reserve funds
Binding: Funds Reservation Codes (Preferred)
... related        0..*    BackboneElement    Prior or corollary claims

.... claim        0..1    Reference(Claim)    Reference to the related claim
.... relationship        0..1    CodeableConcept    How the reference claim is related
Binding: Example Related Claim Relationship Codes (Example)
.... reference        0..1    Identifier    File or case reference
... prescription        0..1    Reference(DeviceRequest | MedicationRequest | ServiceRequest | VisionPrescription)    Prescription authorizing services and products
... originalPrescription        0..1    Reference(DeviceRequest | MedicationRequest | ServiceRequest | VisionPrescription)    Original prescription if superseded by fulfiller
... payee        0..1    BackboneElement    Recipient of benefits payable
.... type        1..1    CodeableConcept    Category of recipient
Binding: Claim Payee Type Codes (Example)
.... party        0..1    Reference(Practitioner | PractitionerRole | Organization | Patient | RelatedPerson)    Recipient reference
... referral        0..1    Reference(ServiceRequest)    Treatment referral
... encounter        0..*    Reference(Encounter)    Encounters associated with the listed treatments

... facility        0..1    Reference(Location | Organization)    Servicing facility
... diagnosisRelatedGroup        0..1    CodeableConcept    Package billing code
Binding: Example Diagnosis Related Group Codes (Example)
... event        0..*    BackboneElement    Event information

.... type        1..1    CodeableConcept    Specific event
Binding: Dates Type Codes (Example)
.... when[x]        1..1        Occurance date or period
..... whenDateTime            dateTime
..... whenPeriod            Period
... careTeam        0..*    BackboneElement    Members of the care team

.... sequence        1..1    positiveInt    Order of care team
.... provider        1..1    Reference(Practitioner | PractitionerRole | Organization)    Practitioner or organization
.... role        0..1    CodeableConcept    Function within the team
Binding: Claim Care Team Role Codes (Preferred)
.... specialty        0..1    CodeableConcept    Practitioner or provider specialization
Binding: Example Provider Qualification Codes (Example)
... supportingInfo        0..*    BackboneElement    Supporting information

.... sequence        1..1    positiveInt    Information instance identifier
.... category        1..1    CodeableConcept    Classification of the supplied information
Binding: Claim Information Category Codes (Preferred)
.... subCategory        0..1    CodeableConcept    Finer-grained classification of the supplied information
Binding: InformationSubCategory (Example)
.... code        0..1    CodeableConcept    Type of information
Binding: Exception Codes (Example)
.... timing[x]        0..1        When it occurred
..... timingDateTime            dateTime
..... timingPeriod            Period
..... timingTiming            Timing
.... value[x]        0..1    *    Data to be provided
.... reason        0..1    CodeableConcept    Explanation for the information
Binding: Missing Tooth Reason Codes (Example)
... diagnosis        0..*    BackboneElement    Pertinent diagnosis information

.... sequence        1..1    positiveInt    Diagnosis instance identifier
.... diagnosis[x]        1..1        Nature of illness or problem
Binding: ICD-10 Codes (Example)
..... diagnosisCodeableConcept            CodeableConcept
..... diagnosisReference            Reference(Condition)
.... type        0..*    CodeableConcept    Timing or nature of the diagnosis
Binding: Example Diagnosis Type Codes (Preferred)

.... onAdmission        0..1    CodeableConcept    Present on admission
Binding: Example Diagnosis on Admission Codes (Preferred)
... procedure        0..*    BackboneElement    Clinical procedures performed

.... sequence        1..1    positiveInt    Procedure instance identifier
.... type        0..*    CodeableConcept    Category of Procedure
Binding: Example Procedure Type Codes (Preferred)

.... date        0..1    dateTime    When the procedure was performed
.... procedure[x]        1..1        Specific clinical procedure
Binding: ICD-10 Procedure Codes (Example)
..... procedureCodeableConcept            CodeableConcept
..... procedureReference            Reference(Procedure)
.... udi        0..*    Reference(Device)    Unique device identifier

... insurance    Σ    0..*    BackboneElement    Patient insurance information

.... sequence    Σ    1..1    positiveInt    Insurance instance identifier
.... focal    Σ    1..1    boolean    Coverage to be used for adjudication
.... identifier        0..1    Identifier    Pre-assigned Claim number
.... coverage    Σ    1..1    Reference(Coverage)    Insurance information
.... businessArrangement        0..1    string    Additional provider contract number
.... preAuthRef        0..*    string    Prior authorization reference number

.... claimResponse        0..1    Reference(ClaimResponse)    Adjudication results
... accident        0..1    BackboneElement    Details of the event
.... date        1..1    date    When the incident occurred
.... type        0..1    CodeableConcept    The nature of the accident
Binding: ActIncidentCode icon (Extensible)
.... location[x]        0..1        Where the event occurred
..... locationAddress            Address
..... locationReference            Reference(Location)
... patientPaid        0..1    Money    Paid by the patient
... item        0..*    BackboneElement    Product or service provided

.... sequence        1..1    positiveInt    Item instance identifier
.... traceNumber        0..*    Identifier    Number for tracking

.... subject        0..1    Reference(Patient | Group)    The recipient of the products and services
.... careTeamSequence        0..*    positiveInt    Applicable careTeam members

.... diagnosisSequence        0..*    positiveInt    Applicable diagnoses

.... procedureSequence        0..*    positiveInt    Applicable procedures

.... informationSequence        0..*    positiveInt    Applicable exception and supporting information

.... revenue        0..1    CodeableConcept    Revenue or cost center code
Binding: Example Revenue Center Codes (Example)
.... category        0..1    CodeableConcept    Benefit classification
Binding: Benefit Category Codes (Example)
.... productOrService        0..1    CodeableConcept    Billing, service, product, or drug code
Binding: USCLS Codes (Example)
.... productOrServiceEnd        0..1    CodeableConcept    End of a range of codes
Binding: USCLS Codes (Example)
.... request        0..*    Reference(DeviceRequest | MedicationRequest | NutritionOrder | ServiceRequest | VisionPrescription)    Request or Referral for Service

.... modifier        0..*    CodeableConcept    Product or service billing modifiers
Binding: Modifier type Codes (Example)

.... programCode        0..*    CodeableConcept    Program the product or service is provided under
Binding: Example Program Reason Codes (Example)

.... serviced[x]        0..1        Date or dates of service or product delivery
..... servicedDate            date
..... servicedPeriod            Period
.... location[x]        0..1        Place of service or where product was supplied
Binding: Example Service Place Codes (Example)
..... locationCodeableConcept            CodeableConcept
..... locationAddress            Address
..... locationReference            Reference(Location)
.... patientPaid        0..1    Money    Paid by the patient
.... quantity        0..1    SimpleQuantity    Count of products or services
.... unitPrice        0..1    Money    Fee, charge or cost per item
.... factor        0..1    decimal    Price scaling factor
.... tax        0..1    Money    Total tax
.... net        0..1    Money    Total item cost
.... udi        0..*    Reference(Device)    Unique device identifier

.... bodySite        0..*    BackboneElement    Anatomical location

..... site        1..*    CodeableReference(BodyStructure)    Location
Binding: Oral Site Codes (Example)

..... subSite        0..*    CodeableConcept    Sub-location
Binding: Surface Codes (Example)

.... encounter        0..*    Reference(Encounter)    Encounters associated with the listed treatments

.... detail        0..*    BackboneElement    Product or service provided

..... sequence        1..1    positiveInt    Item instance identifier
..... traceNumber        0..*    Identifier    Number for tracking

..... revenue        0..1    CodeableConcept    Revenue or cost center code
Binding: Example Revenue Center Codes (Example)
..... category        0..1    CodeableConcept    Benefit classification
Binding: Benefit Category Codes (Example)
..... productOrService        0..1    CodeableConcept    Billing, service, product, or drug code
Binding: USCLS Codes (Example)
..... productOrServiceEnd        0..1    CodeableConcept    End of a range of codes
Binding: USCLS Codes (Example)
..... modifier        0..*    CodeableConcept    Service/Product billing modifiers
Binding: Modifier type Codes (Example)

..... programCode        0..*    CodeableConcept    Program the product or service is provided under
Binding: Example Program Reason Codes (Example)

..... patientPaid        0..1    Money    Paid by the patient
..... quantity        0..1    SimpleQuantity    Count of products or services
..... unitPrice        0..1    Money    Fee, charge or cost per item
..... factor        0..1    decimal    Price scaling factor
..... tax        0..1    Money    Total tax
..... net        0..1    Money    Total item cost
..... udi        0..*    Reference(Device)    Unique device identifier

..... subDetail        0..*    BackboneElement    Product or service provided

...... sequence        1..1    positiveInt    Item instance identifier
...... traceNumber        0..*    Identifier    Number for tracking

...... revenue        0..1    CodeableConcept    Revenue or cost center code
Binding: Example Revenue Center Codes (Example)
...... category        0..1    CodeableConcept    Benefit classification
Binding: Benefit Category Codes (Example)
...... productOrService        0..1    CodeableConcept    Billing, service, product, or drug code
Binding: USCLS Codes (Example)
...... productOrServiceEnd        0..1    CodeableConcept    End of a range of codes
Binding: USCLS Codes (Example)
...... modifier        0..*    CodeableConcept    Service/Product billing modifiers
Binding: Modifier type Codes (Example)

...... programCode        0..*    CodeableConcept    Program the product or service is provided under
Binding: Example Program Reason Codes (Example)

...... patientPaid        0..1    Money    Paid by the patient
...... quantity        0..1    SimpleQuantity    Count of products or services
...... unitPrice        0..1    Money    Fee, charge or cost per item
...... factor        0..1    decimal    Price scaling factor
...... tax        0..1    Money    Total tax
...... net        0..1    Money    Total item cost
...... udi        0..*    Reference(Device)    Unique device identifier

... total        0..1    Money    Total claim cost
```

## Usage

Install dependencies:

```bash
pip install fhir.resources faker
```

Run:

```bash
python generate_fhir_claim.py
```
