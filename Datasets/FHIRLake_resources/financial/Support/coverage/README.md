# FHIRLake Generator - Coverage Resource Generator

This dataset defines the Coverage resource contract and a minimal synthetic generator.

## Dependencies

Required dependencies:
- Patient

Optional dependencies:
- Organization

Required inputs:
- patient_id

Optional inputs:
- organization_id

## Structure

```
Name    Flags   Card.   Type    Description & Constraints    Filter:
 Filtersdoco
.. Coverage    N        DomainResource    Insurance or medical plan or a payment agreement

Elements defined in Ancestors: id, meta, implicitRules, language, text, contained, extension, modifierExtension
... identifier    Σ    0..*    Identifier    Business identifier(s) for this coverage

... status    ?!Σ    1..1    code    active | cancelled | draft | entered-in-error
Binding: Financial Resource Status Codes (Required)
... statusReason    Σ    0..1    string    Reason for status change
... kind    ΣC    1..1    code    insurance | self-pay | other
Binding: Kind (Required)
+ Rule: When patient is insured, insurer must exist.
+ Rule: When patient is self-pay, paymentBy must exist.
... paymentBy    C    0..*    BackboneElement    Self-pay parties and responsibility

.... party    Σ    1..1    Reference(Patient | RelatedPerson | Organization)    Parties performing self-payment
.... responsibility    Σ    0..1    string    Party's responsibility
... type    Σ    0..1    CodeableConcept    Coverage category such as medical or accident
Binding: Coverage Type and Self-Pay Codes (Preferred)
... policyHolder    Σ    0..1    Reference(Patient | RelatedPerson | Organization)    Owner of the policy
... subscriber    Σ    0..1    Reference(Patient | RelatedPerson)    Subscriber to the policy
... subscriberId    Σ    0..*    Identifier    ID assigned to the subscriber

... beneficiary    Σ    1..1    Reference(Patient)    Plan beneficiary
... dependent    Σ    0..1    string    Dependent number
... relationship        0..1    CodeableConcept    Beneficiary relationship to the subscriber
Binding: SubscriberPolicyholder Relationship Codes (Extensible)
... period    Σ    0..1    Period    Coverage start and end dates
... insurer    ΣC    0..1    Reference(Organization)    Issuer of the policy
... class        0..*    BackboneElement    Additional coverage classifications

.... type    Σ    1..1    CodeableConcept    Type of class such as 'group' or 'plan'
Binding: Coverage Class Codes (Extensible)
.... value    Σ    1..1    Identifier    Value associated with the type
.... name    Σ    0..1    string    Human readable description of the type and value
... order    Σ    0..1    positiveInt    Relative order of the coverage
... network    Σ    0..1    string    Insurer network
... costToBeneficiary        0..*    BackboneElement    Patient payments for services/products

.... type    Σ    0..1    CodeableConcept    Cost category
Binding: Coverage Copay Type Codes (Extensible)
.... category        0..1    CodeableConcept    Benefit classification
Binding: Benefit Category Codes (Example)
.... network        0..1    CodeableConcept    In or out of network
Binding: Network Type Codes (Preferred)
.... unit        0..1    CodeableConcept    Individual or family
Binding: Unit Type Codes (Preferred)
.... term        0..1    CodeableConcept    Annual or lifetime
Binding: Benefit Term Codes (Preferred)
.... value[x]    Σ    0..1        The amount or percentage due from the beneficiary
..... valueQuantity            SimpleQuantity
..... valueMoney            Money
.... exception        0..*    BackboneElement    Exceptions for patient payments

..... type    Σ    1..1    CodeableConcept    Exception category
Binding: Example Coverage Financial Exception Codes (Example)
..... period    Σ    0..1    Period    The effective period of the exception
... subrogation        0..1    boolean    Reimbursement to insurer
... contract        0..*    Reference(Contract)    Contract details

... insurancePlan        0..1    Reference(InsurancePlan)    Insurance plan details
```

## Usage

Install dependencies:

```bash
pip install fhir.resources faker
```

Run:

```bash
python generate_fhir_coverage.py
```
