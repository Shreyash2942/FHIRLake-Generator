import json
import pprint
import uuid
import random
from datetime import datetime, timedelta, timezone

from faker import Faker

from fhir.resources.condition import Condition
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.annotation import Annotation
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding
from fhir.resources.age import Age
from fhir.resources.period import Period
from fhir.resources.range import Range
from fhir.resources.quantity import Quantity
from fhir.resources.codeablereference import CodeableReference

# Config
from Datasets.Configs.config_fhir import (
    SNOMED_CODES,
    CLINICAL_STATUSES,
    SEVERITIES,
    VERSION_INFO,
)

fake = Faker()

FHIR_SNOMED = "http://snomed.info/sct"
FHIR_CONDITION_CATEGORY = "http://terminology.hl7.org/CodeSystem/condition-category"
FHIR_CLINICAL_STATUS = "http://terminology.hl7.org/CodeSystem/condition-clinical"
FHIR_VERIFICATION_STATUS = "http://terminology.hl7.org/CodeSystem/condition-ver-status"
UCUM_SYSTEM = "http://unitsofmeasure.org"


def fhir_datetime(dt: datetime) -> str:
    """Format datetime consistently with milliseconds and Z suffix."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def note_kv(key: str, value: str) -> Annotation:
    """
    Store non-supported/extra contract fields as structured Annotation.
    This keeps your dataset contract while remaining model-valid.
    """
    return Annotation(authorString=key, text=str(value))


# ----------------------------
# Helper: onset[x] (choose ONE)
# ----------------------------
def build_onset(onset_dt: datetime) -> dict:
    choice = random.choice(
        ["onsetDateTime", "onsetAge", "onsetPeriod", "onsetRange", "onsetString"]
    )

    if choice == "onsetDateTime":
        return {"onsetDateTime": fhir_datetime(onset_dt)}

    if choice == "onsetAge":
        return {
            "onsetAge": Age(
                value=random.randint(1, 90),
                unit="years",
                system=UCUM_SYSTEM,
                code="a",
            )
        }

    if choice == "onsetPeriod":
        return {"onsetPeriod": Period(start=fhir_datetime(onset_dt))}

    if choice == "onsetRange":
        return {
            "onsetRange": Range(
                low=Quantity(value=30, unit="years", system=UCUM_SYSTEM, code="a"),
                high=Quantity(value=50, unit="years", system=UCUM_SYSTEM, code="a"),
            )
        }

    return {"onsetString": "Onset occurred gradually"}


# ----------------------------
# Helper: abatement[x] (choose ONE)
# ----------------------------
def build_abatement(abatement_dt: datetime) -> dict:
    choice = random.choice(
        ["abatementDateTime", "abatementAge", "abatementPeriod", "abatementRange", "abatementString"]
    )

    if choice == "abatementDateTime":
        return {"abatementDateTime": fhir_datetime(abatement_dt)}

    if choice == "abatementAge":
        return {
            "abatementAge": Age(
                value=random.randint(1, 10),
                unit="years",
                system=UCUM_SYSTEM,
                code="a",
            )
        }

    if choice == "abatementPeriod":
        return {"abatementPeriod": Period(end=fhir_datetime(abatement_dt))}

    if choice == "abatementRange":
        return {
            "abatementRange": Range(
                low=Quantity(value=1, unit="years", system=UCUM_SYSTEM, code="a"),
                high=Quantity(value=5, unit="years", system=UCUM_SYSTEM, code="a"),
            )
        }

    return {"abatementString": "Condition resolved with treatment"}


def build_clinical_status() -> CodeableConcept:
    """
    Supports:
      - CLINICAL_STATUSES as list[str]
      - CLINICAL_STATUSES as list[dict] with keys {code, display}
    """
    choice = random.choice(CLINICAL_STATUSES)
    if isinstance(choice, dict) and "code" in choice:
        return CodeableConcept(
            coding=[
                Coding(
                    system=FHIR_CLINICAL_STATUS,
                    code=choice.get("code"),
                    display=choice.get("display") or choice.get("code"),
                )
            ],
            text=choice.get("display") or choice.get("code"),
        )
    return CodeableConcept(text=str(choice))


def build_severity() -> CodeableConcept:
    """
    Supports:
      - SEVERITIES as list[str]
      - SEVERITIES as list[dict] with keys {system, code, display}
    """
    choice = random.choice(SEVERITIES)
    if isinstance(choice, dict) and ("code" in choice or "display" in choice):
        return CodeableConcept(
            coding=[
                Coding(
                    system=choice.get("system"),
                    code=choice.get("code"),
                    display=choice.get("display"),
                )
            ],
            text=choice.get("display") or choice.get("code"),
        )
    return CodeableConcept(text=str(choice))


def generate_condition(patient_id: str, encounter_id: str) -> Condition:
    patient_id = str(patient_id)
    encounter_id = str(encounter_id)

    onset_dt = fake.date_time_this_year(tzinfo=timezone.utc)
    abatement_dt = onset_dt + timedelta(days=random.randint(1, 10))

    snomed_code, display = random.choice(list(SNOMED_CODES.items()))

    # Verification status
    ver_code, ver_display = random.choice(
        [
            ("unconfirmed", "Unconfirmed"),
            ("provisional", "Provisional"),
            ("differential", "Differential"),
            ("confirmed", "Confirmed"),
            ("refuted", "Refuted"),
            ("entered-in-error", "Entered in Error"),
        ]
    )

    # Category
    cat_code, cat_display = random.choice(
        [("problem-list-item", "Problem List Item"), ("encounter-diagnosis", "Encounter Diagnosis")]
    )

    # Supported FHIR evidence (your model expects CodeableReference)
    evidence = [
        CodeableReference(
            concept=CodeableConcept(text="Lab confirmation"),
            reference=Reference(reference="Observation/example"),
        )
    ]

    # ----------------------------
    # Notes: include schema + unsupported fields
    # ----------------------------
    notes = [
        # regular notes
        Annotation(text="Synthetic condition for analytics"),
        Annotation(text=f"Schema version {VERSION_INFO.get('schema_version', '1.0')}"),

        # ✅ Keep your dataset-contract / unsupported fields here:
        note_kv("unsupported.bodyStructure", "BodyStructure/example"),
        note_kv("unsupported.recorder", "Practitioner/example"),
        note_kv("unsupported.asserter", "Practitioner/example"),

        # ✅ Also store R4-style evidence shape as your contract expects (optional but useful)
        note_kv("contract.evidence.code.text", "Lab confirmation"),
        note_kv("contract.evidence.detail.0", "Observation/example"),
    ]

    # Build the condition payload
    condition_data = {
        "resourceType": "Condition",
        "id": str(uuid.uuid4()),

        "identifier": [
            Identifier(
                system="MetricCare-Condition",
                value=f"COND-{fake.random_number(digits=8, fix_len=True)}",
            )
        ],

        "clinicalStatus": build_clinical_status(),
        "verificationStatus": CodeableConcept(
            coding=[Coding(system=FHIR_VERIFICATION_STATUS, code=ver_code, display=ver_display)],
            text=ver_display,
        ),

        "category": [
            CodeableConcept(
                coding=[Coding(system=FHIR_CONDITION_CATEGORY, code=cat_code, display=cat_display)],
                text=cat_display,
            )
        ],

        "severity": build_severity(),

        "code": CodeableConcept(
            coding=[Coding(system=FHIR_SNOMED, code=snomed_code, display=display)],
            text=display,
        ),

        "bodySite": [
            CodeableConcept(text=random.choice(["Chest", "Abdomen", "Head", "Leg", "Arm"]))
        ],

        "subject": Reference(reference=f"Patient/{patient_id}"),
        "encounter": Reference(reference=f"Encounter/{encounter_id}"),

        "recordedDate": fhir_datetime(onset_dt),

        "stage": [
            {
                "summary": CodeableConcept(text=random.choice(["Stage I", "Stage II", "Stage III"])),
                "assessment": [Reference(reference="Observation/example")],
                "type": CodeableConcept(text="Clinical staging"),
            }
        ],

        "evidence": evidence,
        "note": notes,
    }

    # Add onset[x] and abatement[x] correctly (only one of each)
    condition_data.update(build_onset(onset_dt))
    condition_data.update(build_abatement(abatement_dt))

    return Condition(**condition_data)


if __name__ == "__main__":
    c = generate_condition(uuid.uuid4(), uuid.uuid4())
    print("Generated Condition FHIR Data:\n")
    pprint.pprint(json.loads(c.model_dump_json(exclude_none=True)))
