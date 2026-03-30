# FHIRLake Generator - ExplanationOfBenefit Resource Generator

This dataset defines the ExplanationOfBenefit resource contract and a minimal synthetic generator.

## Dependencies

Required dependencies:
- Patient

Optional dependencies:
- Claim
- Coverage
- Encounter
- Practitioner
- Organization
- Procedure
- MedicationRequest

Required inputs:
- patient_id

Optional inputs:
- claim_id
- coverage_id
- encounter_id
- practitioner_id
- organization_id
- procedure_id
- medication_request_id

## Structure

```
Name    Flags   Card.   Type    Description & Constraints    Filter:
 Filtersdoco
.. ExplanationOfBenefit    N        DomainResource    Explanation of Benefit resource

Elements defined in Ancestors: id, meta, implicitRules, language, text, contained, extension, modifierExtension
... identifier        0..*    Identifier    Business Identifier for the resource

... traceNumber        0..*    Identifier    Number for tracking

... status    ?!S    1..1    code    active | cancelled | draft | entered-in-error
Binding: Explanation Of Benefit Status (Required)
... statusReason    S    0..1    string    Reason for status change
... type    S    1..1    CodeableConcept    Category or discipline
Binding: Claim Type Codes (Extensible)
... subType        0..1    CodeableConcept    More granular claim type
Binding: Example Claim SubType Codes (Example)
... use    S    1..1    code    claim | preauthorization | predetermination
Binding: Use (Required)
... subject    S    1..1    Reference(Patient | Group)    The recipient(s) of the products and services
... billablePeriod    S    0..1    Period    Relevant time frame for the claim
... created    S    1..1    dateTime    Response creation date
... enterer        0..1    Reference(Practitioner | PractitionerRole | Patient | RelatedPerson)    Author of the claim
... insurer    S    0..1    Reference(Organization)    Party responsible for reimbursement
... provider    S    0..1    Reference(Practitioner | PractitionerRole | Organization)    Party responsible for the claim
... priority        0..1    CodeableConcept    Desired processing urgency
Binding: Process Priority Codes (Preferred)
... fundsReserveRequested        0..1    CodeableConcept    For whom to reserve funds
Binding: Funds Reservation Codes (Preferred)
... fundsReserve        0..1    CodeableConcept    Funds reserved status
Binding: Funds Reservation Codes (Preferred)
... related        0..*    BackboneElement    Prior or corollary claims

.... claim        0..1    Reference(Claim | ExplanationOfBenefit)    Reference to the related claim
.... relationship        0..1    CodeableConcept    How the reference claim is related
Binding: Example Related Claim Relationship Codes (Example)
.... reference        0..1    Identifier    File or case reference
... prescription        0..1    Reference(DeviceRequest | MedicationRequest | ServiceRequest | VisionPrescription)    Prescription authorizing services or products
... originalPrescription        0..1    Reference(DeviceRequest | MedicationRequest | ServiceRequest | VisionPrescription)    Original prescription if superceded by fulfiller
... event        0..*    BackboneElement    Event information

.... type        1..1    CodeableConcept    Specific event
Binding: Dates Type Codes (Example)
.... when[x]        1..1        Occurance date or period
..... whenDateTime            dateTime
..... whenPeriod            Period
... payee        0..1    BackboneElement    Recipient of benefits payable
.... type        0..1    CodeableConcept    Category of recipient
Binding: Claim Payee Type Codes (Example)
.... party        0..1    Reference(Practitioner | PractitionerRole | Organization | Patient | RelatedPerson)    Recipient reference
... referral        0..1    Reference(ServiceRequest)    Treatment Referral
... encounter        0..*    Reference(Encounter)    Encounters associated with the listed treatments

... facility        0..1    Reference(Location | Organization)    Servicing Facility
... claim        0..1    Reference(Claim)    Claim reference
... claimResponse        0..1    Reference(ClaimResponse)    Claim response reference
... outcome    S    1..1    code    queued | complete | error | partial
Binding: Claim Processing Codes (Required)
... decision    S    0..1    CodeableConcept    Result of the adjudication
Binding: Claim Adjudication Decision Codes (Preferred)
... disposition        0..1    string    Disposition Message
... preAuthRef        0..*    string    Preauthorization reference

... preAuthRefPeriod        0..*    Period    Preauthorization in-effect period

... diagnosisRelatedGroup        0..1    CodeableConcept    Package billing code
Binding: Example Diagnosis Related Group Codes (Example)
... careTeam        0..*    BackboneElement    Care Team members

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
.... code        0..1    CodeableConcept    Type of information
Binding: Exception Codes (Example)
.... timing[x]        0..1        When it occurred
..... timingDateTime            dateTime
..... timingPeriod            Period
..... timingTiming            Timing
.... value[x]        0..1    *    Data to be provided
.... reason        0..1    Coding    Explanation for the information
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

... precedence        0..1    positiveInt    Precedence (primary, secondary, etc.)
... insurance    S    0..*    BackboneElement    Patient insurance information

.... focal    S    1..1    boolean    Coverage to be used for adjudication
.... coverage    S    1..1    Reference(Coverage)    Insurance information
.... preAuthRef        0..*    string    Prior authorization reference number

... accident        0..1    BackboneElement    Details of the event
.... date        0..1    date    When the incident occurred
.... type        0..1    CodeableConcept    The nature of the accident
Binding: ActIncidentCode icon (Extensible)
.... location[x]        0..1        Where the event occurred
..... locationAddress            Address
..... locationReference            Reference(Location)
... patientPaid        0..1    Money    Paid by the patient
... item        0..*    BackboneElement    Product or service provided

.... sequence        1..1    positiveInt    Item instance identifier
.... careTeamSequence        0..*    positiveInt    Applicable care team members

.... diagnosisSequence        0..*    positiveInt    Applicable diagnoses

.... procedureSequence        0..*    positiveInt    Applicable procedures

.... informationSequence        0..*    positiveInt    Applicable exception and supporting information

.... traceNumber        0..*    Identifier    Number for tracking

.... subject        0..1    Reference(Patient | Group)    The recipient of the products and services
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

.... noteNumber        0..*    positiveInt    Applicable note numbers

.... reviewOutcome        0..1    BackboneElement    Adjudication results
..... decision        0..1    CodeableConcept    Result of the adjudication
Binding: Claim Adjudication Decision Codes (Preferred)
..... reason        0..*    CodeableConcept    Reason for result of the adjudication
Binding: Claim Adjudication Decision Reason Codes (Example)

..... preAuthRef        0..1    string    Preauthorization reference
..... preAuthPeriod        0..1    Period    Preauthorization reference effective period
.... adjudication        0..*    BackboneElement    Adjudication details

..... category        1..1    CodeableConcept    Type of adjudication information
Binding: Adjudication Value Codes (Preferred)
..... reason        0..1    CodeableConcept    Explanation of adjudication outcome
Binding: Adjudication Reason Codes (Example)
..... amount        0..1    Money    Monetary amount
..... quantity        0..1    Quantity    Non-monitary value
..... decisionDate        0..1    dateTime    When was adjudication performed
.... detail        0..*    BackboneElement    Additional items

..... sequence        1..1    positiveInt    Product or service provided
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

..... noteNumber        0..*    positiveInt    Applicable note numbers

..... reviewOutcome        0..1    see reviewOutcome    Detail level adjudication results
..... adjudication        0..*    see adjudication    Detail level adjudication details

..... subDetail        0..*    BackboneElement    Additional items

...... sequence        1..1    positiveInt    Product or service provided
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

...... noteNumber        0..*    positiveInt    Applicable note numbers

...... reviewOutcome        0..1    see reviewOutcome    Subdetail level adjudication results
...... adjudication        0..*    see adjudication    Subdetail level adjudication details

... addItem        0..*    BackboneElement    Insurer added line items

.... itemSequence        0..*    positiveInt    Item sequence number

.... detailSequence        0..*    positiveInt    Detail sequence number

.... subDetailSequence        0..*    positiveInt    Subdetail sequence number

.... traceNumber        0..*    Identifier    Number for tracking

.... subject        0..1    Reference(Patient | Group)    The recipient of the products and services
.... informationSequence        0..*    positiveInt    Applicable exception and supporting information

.... provider        0..*    Reference(Practitioner | PractitionerRole | Organization)    Authorized providers

.... revenue        0..1    CodeableConcept    Revenue or cost center code
Binding: Example Revenue Center Codes (Example)
.... category        0..1    CodeableConcept    Benefit classification
Binding: Benefit Category Codes (Example)
.... productOrService        0..1    CodeableConcept    Billing, service, product, or drug code
Binding: USCLS Codes (Example)
.... productOrServiceEnd        0..1    CodeableConcept    End of a range of codes
Binding: USCLS Codes (Example)
.... request        0..*    Reference(DeviceRequest | MedicationRequest | NutritionOrder | ServiceRequest | VisionPrescription)    Request or Referral for Service

.... modifier        0..*    CodeableConcept    Service/Product billing modifiers
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
.... bodySite        0..*    BackboneElement    Anatomical location

..... site        1..*    CodeableReference(BodyStructure)    Location
Binding: Oral Site Codes (Example)

..... subSite        0..*    CodeableConcept    Sub-location
Binding: Surface Codes (Example)

.... noteNumber        0..*    positiveInt    Applicable note numbers

.... reviewOutcome        0..1    see reviewOutcome    Additem level adjudication results
.... adjudication        0..*    see adjudication    Added items adjudication

.... detail        0..*    BackboneElement    Insurer added line items

..... traceNumber        0..*    Identifier    Number for tracking

..... revenue        0..1    CodeableConcept    Revenue or cost center code
Binding: Example Revenue Center Codes (Example)
..... productOrService        0..1    CodeableConcept    Billing, service, product, or drug code
Binding: USCLS Codes (Example)
..... productOrServiceEnd        0..1    CodeableConcept    End of a range of codes
Binding: USCLS Codes (Example)
..... modifier        0..*    CodeableConcept    Service/Product billing modifiers
Binding: Modifier type Codes (Example)

..... patientPaid        0..1    Money    Paid by the patient
..... quantity        0..1    SimpleQuantity    Count of products or services
..... unitPrice        0..1    Money    Fee, charge or cost per item
..... factor        0..1    decimal    Price scaling factor
..... tax        0..1    Money    Total tax
..... net        0..1    Money    Total item cost
..... noteNumber        0..*    positiveInt    Applicable note numbers

..... reviewOutcome        0..1    see reviewOutcome    Additem detail level adjudication results
..... adjudication        0..*    see adjudication    Added items adjudication

..... subDetail        0..*    BackboneElement    Insurer added line items

...... traceNumber        0..*    Identifier    Number for tracking

...... revenue        0..1    CodeableConcept    Revenue or cost center code
Binding: Example Revenue Center Codes (Example)
...... productOrService        0..1    CodeableConcept    Billing, service, product, or drug code
Binding: USCLS Codes (Example)
...... productOrServiceEnd        0..1    CodeableConcept    End of a range of codes
Binding: USCLS Codes (Example)
...... modifier        0..*    CodeableConcept    Service/Product billing modifiers
Binding: Modifier type Codes (Example)

...... patientPaid        0..1    Money    Paid by the patient
...... quantity        0..1    SimpleQuantity    Count of products or services
...... unitPrice        0..1    Money    Fee, charge or cost per item
...... factor        0..1    decimal    Price scaling factor
...... tax        0..1    Money    Total tax
...... net        0..1    Money    Total item cost
...... noteNumber        0..*    positiveInt    Applicable note numbers

...... reviewOutcome        0..1    see reviewOutcome    Additem subdetail level adjudication results
...... adjudication        0..*    see adjudication    Added items adjudication

... adjudication        0..*    see adjudication    Header-level adjudication

... total    S    0..*    BackboneElement    Adjudication totals

.... category    S    1..1    CodeableConcept    Type of adjudication information
Binding: Adjudication Value Codes (Example)
.... amount    S    1..1    Money    Financial total for the category
... payment        0..1    BackboneElement    Payment Details
.... type        0..1    CodeableConcept    Partial or complete payment
Binding: Example Payment Type Codes (Preferred)
.... adjustment        0..1    Money    Payment adjustment for non-claim issues
.... adjustmentReason        0..1    CodeableConcept    Explanation for the variance
Binding: Payment Adjustment Reason Codes (Preferred)
.... date        0..1    date    Expected date of payment
.... amount        0..1    Money    Payable amount after adjustment
.... identifier        0..1    Identifier    Business identifier for the payment
... formCode        0..1    CodeableConcept    Printed form identifier
Binding: Form Codes (Example)
... form        0..1    Attachment    Printed reference or actual form
... processNote        0..*    BackboneElement    Note concerning adjudication

.... class        0..1    CodeableConcept    Business kind of note
Binding: ProcessNoteClass (Example)
.... number        0..1    positiveInt    Note instance identifier
.... type        0..1    CodeableConcept    Note purpose
Binding: NoteType (Extensible)
.... text        0..1    markdown    Note explanatory text
.... language        0..1    CodeableConcept    Language of the text
Binding: All Languages (Required)
Additional Bindings    Purpose
Common Languages    Starter

... benefitPeriod        0..1    Period    When the benefits are applicable
... benefitBalance        0..*    BackboneElement    Balance by Benefit Category

.... category        1..1    CodeableConcept    Benefit classification
Binding: Benefit Category Codes (Example)
.... excluded        0..1    boolean    Excluded from the plan
.... name        0..1    string    Short name for the benefit
.... description        0..1    string    Description of the benefit or services covered
.... network        0..1    CodeableConcept    In or out of network
Binding: Network Type Codes (Example)
.... unit        0..1    CodeableConcept    Individual or family
Binding: Unit Type Codes (Example)
.... term        0..1    CodeableConcept    Annual or lifetime
Binding: Benefit Term Codes (Example)
.... financial        0..*    BackboneElement    Benefit Summary

..... type        1..1    CodeableConcept    Benefit classification
Binding: Benefit Type Codes (Example)
..... allowed[x]        0..1        Benefits allowed
...... allowedUnsignedInt            unsignedInt
...... allowedString            string
...... allowedMoney            Money
..... used[x]        0..1        Benefits used
...... usedUnsignedInt            unsignedInt
...... usedMoney            Money
```

## Usage

Install dependencies:

```bash
pip install fhir.resources faker
```

Run:

```bash
python generate_fhir_explanationofbenefit.py
```
