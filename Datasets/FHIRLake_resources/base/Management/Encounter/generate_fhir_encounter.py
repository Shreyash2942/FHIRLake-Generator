import json
import pprint
import uuid
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

from faker import Faker

from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.encounter import EncounterParticipant, EncounterLocation
from fhir.resources.period import Period
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.identifier import Identifier
from fhir.resources.duration import Duration

# Optional (depends on your fhir.resources build)
try:
    from fhir.resources.codeablereference import CodeableReference
except Exception:
    CodeableReference = None

# 🧱 Import shared config file
from Datasets.Configs.config_fhir import (
    ENCOUNTER_TYPES,
    ENCOUNTER_STATUSES,
    PARTICIPANT_ROLES,
    DEPARTMENTS,
    HOSPITALS,
    VERSION_INFO
)

fake = Faker()


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def format_fhir_datetime(dt: datetime) -> str:
    """Format datetime consistently with milliseconds and Z suffix."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def cc_text(
    text: str,
    system: str = None,
    code: str = None,
    display: str = None
) -> CodeableConcept:
    """Create CodeableConcept with optional Coding."""
    if system and code:
        return CodeableConcept(
            coding=[Coding(system=system, code=code, display=display or text)],
            text=text
        )
    return CodeableConcept(text=text)


def make_identifier(system: str, value: str, id_type_text: str) -> Identifier:
    return Identifier(
        use="usual",
        type=cc_text(id_type_text),
        system=system,
        value=value
    )


def make_ref(reference: str = None, display: str = None) -> Reference:
    return Reference(reference=reference, display=display)


def make_codeable_reference(display_text: str, ref: str = None):
    """
    For R5 fields that accept CodeableReference.
    If CodeableReference isn't available, fall back to CodeableConcept.
    """
    if CodeableReference:
        return CodeableReference(
            concept=cc_text(display_text),
            reference=make_ref(reference=ref) if ref else None
        )
    return cc_text(display_text)


# ---------------------------------------------------------------------
# Legacy single-resource builder (kept for reuse)
# ---------------------------------------------------------------------
def generate_encounter(patient_id: str) -> FHIREncounter:
    """
    Generates a FHIR R5 Encounter resource for a given patient.
    This is the legacy single-resource creator.

    The Core Engine will call the new-style generate(ctx, store, inputs, count)
    wrapper below.
    """

    # ----------------------------
    # Temporal fields
    # ----------------------------
    admission_dt = fake.date_time_this_decade(tzinfo=timezone.utc)
    los_days = random.randint(1, 7)
    discharge_dt = admission_dt + timedelta(days=los_days)

    admission = format_fhir_datetime(admission_dt)
    discharge = format_fhir_datetime(discharge_dt)

    # ----------------------------
    # Encounter attributes
    # ----------------------------
    encounter_type = random.choice(ENCOUNTER_TYPES)
    department = random.choice(DEPARTMENTS)
    selected_org = random.choice(HOSPITALS)
    status = random.choice(ENCOUNTER_STATUSES)

    # ----------------------------
    # Identifiers
    # ----------------------------
    encounter_number = f"ENC-{random.randint(100000, 999999)}"
    visit_number = f"V-{random.randint(10000, 99999)}"

    identifiers = [
        make_identifier("FHIRLake-ENC", encounter_number, "Encounter Number"),
        make_identifier("FHIRLake-VISIT", visit_number, "Visit Number"),
    ]

    # ----------------------------
    # Encounter class (R5 uses class_fhir)
    # ----------------------------
    enc_class = random.choice([
        ("inpatient", "IMP", "inpatient encounter"),
        ("outpatient", "AMB", "ambulatory"),
        ("emergency", "EMER", "emergency"),
        ("urgent care", "UC", "urgent care"),
    ])

    class_cc = [cc_text(
        enc_class[0],
        system="http://terminology.hl7.org/CodeSystem/v3-ActCode",
        code=enc_class[1],
        display=enc_class[2]
    )]

    # ----------------------------
    # Priority
    # ----------------------------
    priority_cc = cc_text(
        random.choice(["routine", "urgent", "asap", "stat"]),
        system="http://terminology.hl7.org/CodeSystem/v3-ActPriority",
        code=random.choice(["R", "UR", "ASAP", "STAT"]),
        display="priority"
    )

    # ----------------------------
    # Subject + Subject Status
    # ----------------------------
    subject_ref = make_ref(reference=f"Patient/{patient_id}")
    subject_status = cc_text(random.choice(["present", "absent", "unknown"]))

    # ----------------------------
    # Service Type
    # ----------------------------
    service_type = [make_codeable_reference(display_text=department, ref=f"HealthcareService/{uuid.uuid4()}")]

    # ----------------------------
    # Participant
    # ----------------------------
    participant = EncounterParticipant(
        type=[cc_text(random.choice(PARTICIPANT_ROLES))],
        period=Period(start=admission, end=discharge),
        actor=make_ref(reference=f"Practitioner/{uuid.uuid4()}")
    )

    # ----------------------------
    # Location
    # ----------------------------
    location = EncounterLocation(
        location=make_ref(reference=f"Location/{uuid.uuid4()}", display=department),
        status=random.choice(["planned", "active", "reserved", "completed"]),
        form=cc_text(random.choice(["bed", "room", "ward", "virtual"])),
        period=Period(start=admission, end=discharge)
    )

    # ----------------------------
    # Service Provider
    # ----------------------------
    service_provider = make_ref(
        reference=f"Organization/{selected_org['id']}",
        display=selected_org["name"]
    )

    # ----------------------------
    # Reason + Diagnosis
    # ----------------------------
    reason_text = random.choice([
        "chest pain", "fever", "shortness of breath", "routine follow-up",
        "hypertension management", "diabetes check", "post-op review"
    ])
    diag_text = random.choice([
        "hypertension", "type 2 diabetes", "acute bronchitis", "pneumonia",
        "UTI", "asthma", "migraine"
    ])

    reasons = [{
        "use": [cc_text("chief-complaint")],
        "value": [make_codeable_reference(display_text=reason_text, ref=f"Condition/{uuid.uuid4()}")]
    }]

    diagnosis = [{
        "condition": [make_codeable_reference(display_text=diag_text, ref=f"Condition/{uuid.uuid4()}")],
        "use": [cc_text(random.choice(["admission", "billing", "discharge"]))]
    }]

    # ----------------------------
    # Planned start/end + actualPeriod + length
    # ----------------------------
    planned_start = format_fhir_datetime(admission_dt - timedelta(hours=random.randint(1, 24)))
    planned_end = discharge

    duration = Duration(
        value=float(los_days),
        unit="days",
        system="http://unitsofmeasure.org",
        code="d"
    )

    # ----------------------------
    # Admission block
    # ----------------------------
    admission_block = {
        "preAdmissionIdentifier": make_identifier(
            "FHIRLake-PREADMIT",
            f"PA-{random.randint(10000, 99999)}",
            "Pre-Admission ID"
        ),
        "origin": make_ref(reference=f"Organization/{uuid.uuid4()}", display="Referral Source"),
        "admitSource": cc_text(random.choice(["physician referral", "transfer", "emergency", "clinic referral"])),
        "reAdmission": cc_text(random.choice(["yes", "no"])),
        "destination": make_ref(reference=f"Location/{uuid.uuid4()}", display="Discharge Destination"),
        "dischargeDisposition": cc_text(
            random.choice(["home", "skilled nursing", "rehab", "expired", "left against advice"])
        )
    }

    # ----------------------------
    # Optional fields
    # ----------------------------
    diet_preference = [cc_text(random.choice(["vegetarian", "diabetic", "low sodium", "regular"]))]
    special_arrangement = [cc_text(random.choice(["wheelchair", "translator", "stretcher", "none"]))]
    special_courtesy = [cc_text(random.choice(["vip", "staff", "board member", "none"]))]

    based_on = [make_ref(reference=f"ServiceRequest/{uuid.uuid4()}")]
    care_team = [make_ref(reference=f"CareTeam/{uuid.uuid4()}")]
    episode_of_care = [make_ref(reference=f"EpisodeOfCare/{uuid.uuid4()}")]

    part_of = make_ref(reference=f"Encounter/{uuid.uuid4()}") if random.random() < 0.25 else None
    appointment = [make_ref(reference=f"Appointment/{uuid.uuid4()}")] if random.random() < 0.60 else None
    account = [make_ref(reference=f"Account/{uuid.uuid4()}")]

    # ----------------------------
    # Virtual service (channelType must be Coding, not CodeableConcept)
    # ----------------------------
    virtual_service = None
    if random.random() < 0.40:
        channel = random.choice(["video", "phone"])
        virtual_service = [{
            "channelType": {
                "system": "http://terminology.hl7.org/CodeSystem/virtual-service-type",
                "code": channel,
                "display": channel
            },
            "addressUrl": "https://telehealth.example.org/room/" + str(uuid.uuid4())
        }]

    # ----------------------------
    # businessStatus + contained represented via extensions
    # ----------------------------
    granular_label = random.choice(["admitted", "under-evaluation", "awaiting-tests", "ready-for-discharge"])
    workflow_type = random.choice(["clinical-workflow", "billing-workflow", "admission-workflow"])

    extensions = [
        {
            "url": "http://fhirlake.io/fhir/StructureDefinition/encounter-businessStatus-code",
            "valueString": granular_label
        },
        {
            "url": "http://fhirlake.io/fhir/StructureDefinition/encounter-businessStatus-type",
            "valueString": workflow_type
        },
        {
            "url": "http://fhirlake.io/fhir/StructureDefinition/encounter-businessStatus-effectiveDate",
            "valueDateTime": admission
        },
        {
            "url": "http://fhirlake.io/fhir/StructureDefinition/encounter-contained-policy",
            "valueString": "No contained resources; related entities are referenced externally."
        }
    ]

    # ----------------------------
    # Build Encounter payload
    # ----------------------------
    payload = {
        "resourceType": "Encounter",
        "id": str(uuid.uuid4()),
        "meta": {
            "versionId": str(VERSION_INFO.get("versionId", "1")),
            "lastUpdated": format_fhir_datetime(fake.date_time_this_year(tzinfo=timezone.utc))
        },

        "identifier": identifiers,
        "status": status,

        "class_fhir": class_cc,
        "priority": priority_cc,

        "type": [cc_text(encounter_type)],
        "serviceType": service_type,

        "subject": subject_ref,
        "subjectStatus": subject_status,

        "basedOn": based_on,
        "careTeam": care_team,
        "episodeOfCare": episode_of_care,
        "partOf": part_of,

        "serviceProvider": service_provider,
        "participant": [participant],

        "appointment": appointment,
        "virtualService": virtual_service,

        "actualPeriod": {"start": admission, "end": discharge},
        "plannedStartDate": planned_start,
        "plannedEndDate": planned_end,
        "length": duration,

        "reason": reasons,
        "diagnosis": diagnosis,

        "account": account,

        "dietPreference": diet_preference,
        "specialArrangement": special_arrangement,
        "specialCourtesy": special_courtesy,

        "admission": admission_block,
        "location": [location],

        "contained": [],
        "extension": extensions,
    }

    # Remove Nones
    payload = {k: v for k, v in payload.items() if v is not None}

    return FHIREncounter(**payload)


# ---------------------------------------------------------------------
# ✅ NEW-STYLE ENTRYPOINT (REQUIRED BY CORE ENGINE)
# ---------------------------------------------------------------------
def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    """
    Core Engine contract:
      generate(ctx, store, inputs, count) -> list[dict]

    Required inputs:
      inputs["patient_id"]  # resolved by Resolver from ResourceStore pools

    - Generates `count` encounters
    - Converts FHIR object -> dict
    - Registers Encounter IDs into ResourceStore pools
    """
    resources: List[Dict[str, Any]] = []

    patient_id = inputs.get("patient_id")
    if not patient_id:
        raise ValueError(
            "Encounter generator requires inputs['patient_id']. "
            "Fix: registry spec.required_inputs must include 'patient_id' OR 'Patient' (if your Resolver supports mapping)."
        )

    for _ in range(int(count)):
        enc_obj = generate_encounter(patient_id)

        # Convert FHIR model -> dict safely
        if hasattr(enc_obj, "model_dump"):
            enc_dict = enc_obj.model_dump(exclude_none=True)
        else:
            enc_dict = enc_obj.dict(exclude_none=True)

        eid = enc_dict.get("id")
        if eid:
            store.register_id("Encounter", eid)

        resources.append(enc_dict)

    return resources


# ---------------------------------------------------------------------
# Standalone run
# ---------------------------------------------------------------------
if __name__ == "__main__":
    encounter = generate_encounter(str(uuid.uuid4()))
    print("✅ FHIR Encounter (R5, schema-aligned):\n")
    pprint.pprint(json.loads(encounter.model_dump_json(exclude_none=True)))
