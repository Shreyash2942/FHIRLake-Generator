import json
import pprint
import uuid
import random
from faker import Faker
from datetime import datetime, timedelta, timezone, date

from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.address import Address
from fhir.resources.identifier import Identifier
from fhir.resources.meta import Meta
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.reference import Reference

# 🧱 Import shared config file
from Datasets.Configs.config_fhir import HOSPITALS, LANGUAGES, VERSION_INFO

fake = Faker()

DECEASED = [True, False, False]  # ~33% chance deceased
HAS_PHOTO = [True, False, False, False]  # ~25% chance
HAS_CONTACT = [True, True, False]  # ~66% chance
HAS_GP = [True, True, False]  # ~66% chance
HAS_LINK = [True, False, False, False]  # ~25% chance

GENDERS = ["male", "female", "other", "unknown"]

MARITAL = [
    ("M", "Married"),
    ("S", "Never Married"),
    ("D", "Divorced"),
    ("W", "Widowed"),
    ("U", "Unmarried"),
]

# Common relationship examples (very simplified)
CONTACT_REL = [
    ("parent", "Parent"),
    ("guardian", "Guardian"),
    ("partner", "Partner"),
    ("friend", "Friend"),
    ("emergency", "Emergency Contact"),
]

def _bcp47_language_code(lang_text: str) -> str:
    """
    FHIR Patient.communication.language is Required binding to BCP-47.
    Your LANGUAGES list might be names like 'English', 'Spanish'.
    This maps common ones; fallback = 'en'.
    """
    mapping = {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "Hindi": "hi",
        "Gujarati": "gu",
        "Punjabi": "pa",
        "Chinese": "zh",
        "Arabic": "ar",
        "Portuguese": "pt",
        "Russian": "ru",
    }
    return mapping.get(lang_text, "en")

def _make_marital_status() -> CodeableConcept:
    code, display = random.choice(MARITAL)
    # v3-MaritalStatus code system commonly used in examples
    return CodeableConcept(
        coding=[{
            "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
            "code": code,
            "display": display
        }],
        text=display
    )

def _make_telecom():
    # Add phone + email (0..* ContactPoint)
    phone = fake.phone_number()
    email = fake.email()

    return [
        {"system": "phone", "value": phone, "use": "mobile"},
        {"system": "email", "value": email, "use": "home"},
    ]

def _make_name():
    # HumanName 0..*
    given1 = fake.first_name()
    given2 = fake.first_name()
    family = fake.last_name()

    return [{
        "use": "official",
        "family": family,
        "given": [given1, given2]
    }]

def _make_photo(patient_id: str):
    # Attachment 0..* (use URL placeholder; no real PHI)
    return [{
        "contentType": "image/jpeg",
        "url": f"https://example.org/synthetic/patient-photo/{patient_id}.jpg",
        "title": "Synthetic Patient Photo"
    }]

def _make_contact():
    """
    Patient.contact 0..* (BackboneElement)
    Must satisfy pat-1: SHALL contain name or telecom or address or organization.
    We'll include name + telecom + relationship.
    """
    rel_code, rel_display = random.choice(CONTACT_REL)

    contact_obj = {
        "relationship": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                "code": rel_code,
                "display": rel_display
            }],
            "text": rel_display
        }],
        "name": {
            "use": "usual",
            "family": fake.last_name(),
            "given": [fake.first_name()]
        },
        "telecom": [
            {"system": "phone", "value": fake.phone_number(), "use": "mobile"}
        ],
        # Optional organization reference (use your hospitals)
        "organization": {
            "reference": f"Organization/{random.choice(HOSPITALS)['id']}",
            "display": random.choice(HOSPITALS)["name"]
        },
        "period": {
            "start": datetime.now(timezone.utc).date().isoformat()
        }
    }

    # Optional address for contact (sometimes)
    if random.choice([True, False]):
        contact_obj["address"] = {
            "use": "home",
            "line": [fake.street_address()],
            "city": fake.city(),
            "state": fake.state_abbr(),
            "country": "USA"
        }

    return [contact_obj]

def _make_general_practitioner():
    """
    Patient.generalPractitioner 0..* Reference(Organization|Practitioner|PractitionerRole)
    We’ll point to an Organization for simplicity (you can add Practitioner later).
    """
    org = random.choice(HOSPITALS)
    return [{
        "reference": f"Organization/{org['id']}",
        "display": f"{org['name']} Primary Care"
    }]

def _make_link():
    """
    Patient.link 0..*
    other: Reference(Patient|RelatedPerson)
    type: replaced-by | replaces | refer | seealso
    """
    link_type = random.choice(["seealso", "refer", "replaces", "replaced-by"])
    # synthetic "other" patient id
    other_id = str(uuid.uuid4())
    return [{
        "other": {"reference": f"Patient/{other_id}"},
        "type": link_type
    }]

def _make_multiple_birth():
    """
    multipleBirth[x] 0..1: boolean OR integer
    We'll randomly choose:
      - None
      - boolean True/False
      - integer birth order (2-4)
    """
    choice = random.choice(["none", "bool", "int"])
    if choice == "none":
        return {}
    if choice == "bool":
        return {"multipleBirthBoolean": random.choice([True, False])}
    return {"multipleBirthInteger": random.randint(2, 4)}

def generate_patient() -> FHIRPatient:
    patient_id = str(uuid.uuid4())
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)

    # Deceased[x]
    is_deceased = random.choice(DECEASED)
    deceased_date = None
    if is_deceased:
        max_life_span_days = (date.today() - birth_date).days
        if max_life_span_days > 0:
            death_offset = random.randint(1, max_life_span_days)
            death_date = birth_date + timedelta(days=death_offset)
            deceased_date = datetime.combine(
                death_date, datetime.min.time(), tzinfo=timezone.utc
            ).isoformat()

    selected_language = random.choice(LANGUAGES)
    selected_org = random.choice(HOSPITALS)

    # Patient.communication.language must be CodeableConcept; binding uses BCP-47 codes
    lang_code = _bcp47_language_code(selected_language)

    # Build base patient
    patient_dict = dict(
        resourceType="Patient",
        id=patient_id,
        active=True,
        meta=Meta(
            versionId=VERSION_INFO["schema_version"],
            lastUpdated=datetime.now(timezone.utc).isoformat(),
        ),
        identifier=[
            Identifier(
                use="usual",
                type=CodeableConcept(text="Medical Record Number"),
                system="MetricCare-MRN",
                value=f"MC-{random.randint(100000, 999999)}",
            )
        ],
        name=_make_name(),
        telecom=_make_telecom(),
        gender=random.choice(GENDERS),
        birthDate=birth_date.isoformat(),
        address=[
            Address(
                use="home",
                type="both",
                line=[fake.street_address()],
                city=fake.city(),
                state=fake.state_abbr(),
                postalCode=fake.postcode(),
                country="USA",
            )
        ],
        maritalStatus=_make_marital_status(),
        communication=[
            {
                "language": {
                    "coding": [{
                        "system": "urn:ietf:bcp:47",
                        "code": lang_code,
                        "display": selected_language
                    }],
                    "text": selected_language
                },
                "preferred": True,
            }
        ],
        managingOrganization=Reference(
            reference=f"Organization/{selected_org['id']}",
            display=selected_org["name"],
        ),
    )

    # deceased[x]
    if is_deceased and deceased_date:
        patient_dict["deceasedDateTime"] = deceased_date

    # multipleBirth[x]
    patient_dict.update(_make_multiple_birth())

    # photo 0..*
    if random.choice(HAS_PHOTO):
        patient_dict["photo"] = _make_photo(patient_id)

    # contact 0..* (satisfies pat-1)
    if random.choice(HAS_CONTACT):
        patient_dict["contact"] = _make_contact()

    # generalPractitioner 0..*
    if random.choice(HAS_GP):
        patient_dict["generalPractitioner"] = _make_general_practitioner()

    # link 0..*
    if random.choice(HAS_LINK):
        patient_dict["link"] = _make_link()

    # Create FHIR object
    patient = FHIRPatient(**patient_dict)
    return patient

if __name__ == "__main__":
    patient = generate_patient()
    print("✅ More-complete FHIR Patient Resource:\n")
    pprint.pprint(json.loads(patient.model_dump_json(exclude_none=True)))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"patient_{timestamp}.json"
    print(f"\nSuggested file path: s3://metriccare-dev/bronze/patient/{file_name}")
