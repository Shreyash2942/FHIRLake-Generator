import json
import pprint
import uuid
import random
from faker import Faker
from datetime import datetime, timedelta, timezone, date

from fhir.resources.practitioner import Practitioner as FHIRPractitioner
from fhir.resources.address import Address
from fhir.resources.identifier import Identifier
from fhir.resources.meta import Meta
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.attachment import Attachment
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.period import Period
from fhir.resources.reference import Reference

# 🧱 Shared config
from Datasets.Configs.config_fhir import HOSPITALS, LANGUAGES, VERSION_INFO

fake = Faker()

DECEASED = [True, False, False]  # ~33% chance deceased
GENDERS = ["male", "female", "other", "unknown"]


def generate_practitioner() -> FHIRPractitioner:
    """Generate a FHIR-compliant Practitioner resource for analytics & workforce simulation."""

    practitioner_id = str(uuid.uuid4())
    birth_date = fake.date_of_birth(minimum_age=25, maximum_age=80)

    # ----------------------------
    # Deceased simulation
    # ----------------------------
    is_deceased = random.choice(DECEASED)
    deceased_datetime = None

    if is_deceased:
        max_life_days = (date.today() - birth_date).days
        if max_life_days > 0:
            death_offset = random.randint(1, max_life_days)
            death_date = birth_date + timedelta(days=death_offset)
            deceased_datetime = datetime.combine(
                death_date, datetime.min.time(), tzinfo=timezone.utc
            ).isoformat()

    # ----------------------------
    # Language & organization
    # ----------------------------
    selected_language = random.choice(LANGUAGES)
    selected_org = random.choice(HOSPITALS)

    # ----------------------------
    # Practitioner resource
    # ----------------------------
    practitioner = FHIRPractitioner(
        resourceType="Practitioner",
        id=practitioner_id,
        active=True,
        meta=Meta(
            versionId=VERSION_INFO["schema_version"],
            lastUpdated=datetime.now(timezone.utc).isoformat()
        ),
        identifier=[
            Identifier(
                use="official",
                type=CodeableConcept(text="Practitioner ID"),
                system="MetricCare-Provider-ID",
                value=f"PR-{random.randint(10000, 99999)}"
            )
        ],
        name=[
            HumanName(
                use="official",
                family=fake.last_name(),
                given=[fake.first_name()],
                prefix=["Dr"]
            )
        ],
        telecom=[
            ContactPoint(
                system="phone",
                value=fake.phone_number(),
                use="work"
            ),
            ContactPoint(
                system="email",
                value=fake.email(),
                use="work"
            )
        ],
        gender=random.choice(GENDERS),
        birthDate=birth_date.isoformat(),
        address=[
            Address(
                use="home",
                type="both",
                line=[fake.street_address()],
                city=fake.city(),
                state=fake.state_abbr(),
                country="USA"
            )
        ],
        photo=[
            Attachment(
                contentType="image/jpeg",
                url="https://example.org/practitioner/photo.jpg",
                title="Practitioner Photo"
            )
        ],
        qualification=[
            {
                "identifier": [
                    Identifier(
                        use="official",
                        system="MetricCare-License",
                        value=f"LIC-{random.randint(100000, 999999)}"
                    )
                ],
                "code": CodeableConcept(
                    text=random.choice(["MD", "DO", "RN", "NP", "PA", "PharmD"])
                ),

                # ✅ status is NOT supported by Practitioner.qualification in your model,
                # so we preserve it using an extension:
                "extension": [
                    {
                        "url": "https://fhirlake.dev/unsupported/qualification.status",
                        "valueCodeableConcept": CodeableConcept(
                            text=random.choice(["active", "suspended", "expired"])
                        ).model_dump(exclude_none=True)
                    }
                ],

                "period": Period(
                    start=fake.date_between(start_date="-20y", end_date="-5y").isoformat(),
                    end=None
                ),
                "issuer": Reference(
                    reference=f"Organization/{selected_org['id']}",
                    display=selected_org["name"]
                )
            }
        ],
        communication=[
            {
                "language": CodeableConcept(text=selected_language),
                "preferred": True
            }
        ],
        deceasedDateTime=deceased_datetime if is_deceased else None
    )

    return practitioner


# ----------------------------
# Example standalone execution
# ----------------------------
if __name__ == "__main__":
    practitioner = generate_practitioner()
    print("✅ FHIR Practitioner Resource:\n")
    pprint.pprint(json.loads(practitioner.model_dump_json(exclude_none=True)))

    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # file_name = f"practitioner_{timestamp}.json"
    # print(f"\nSuggested file path: s3://metriccare-dev/bronze/practitioner/{file_name}")
