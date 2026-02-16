"""
FHIRLake Generator - Location Resource Generator (FHIR R5+)

Generates synthetic FHIR Location resources using:
- fhir.resources (pydantic FHIR models)
- Faker (realistic-ish text, addresses)
- Contract-preserving fallback: if a field/datatype is not supported by your installed fhir.resources,
  we store it under Location.extension as:
    url = "https://fhirlake.dev/unsupported/<fieldPath>"
    valueString = "<json/text>"

FHIR Spec reference (fields):
- Location.status, operationalStatus, code, name, alias, description, mode, type, contact, address, form, position,
  managingOrganization, partOf, characteristic, hoursOfOperation, virtualService, endpoint
"""

from __future__ import annotations

import json
import random
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from faker import Faker

from fhir.resources.location import Location
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.address import Address
from fhir.resources.reference import Reference
from fhir.resources.extension import Extension


fake = Faker()


# ----------------------------
# Small helpers (FHIR builders)
# ----------------------------

def _uuid() -> str:
    return str(uuid.uuid4())


def _as_json_string(value: Any) -> str:
    """Safe JSON serialization for putting complex objects into valueString."""
    try:
        return json.dumps(value, ensure_ascii=False)
    except TypeError:
        return json.dumps(str(value), ensure_ascii=False)


def make_identifier(system: str, value: str, use: str = "usual", type_text: str = "Location Identifier") -> Identifier:
    return Identifier.model_validate({
        "use": use,
        "type": {"text": type_text},
        "system": system,
        "value": value
    })


def make_coding(system: str, code: str, display: Optional[str] = None) -> Coding:
    payload: Dict[str, Any] = {"system": system, "code": code}
    if display:
        payload["display"] = display
    return Coding.model_validate(payload)


def make_codeable_concept(codings: List[Coding], text: Optional[str] = None) -> CodeableConcept:
    payload: Dict[str, Any] = {"coding": [c.model_dump(exclude_none=True) for c in codings]}
    if text:
        payload["text"] = text
    return CodeableConcept.model_validate(payload)


def make_reference(ref: str, display: Optional[str] = None) -> Reference:
    payload: Dict[str, Any] = {"reference": ref}
    if display:
        payload["display"] = display
    return Reference.model_validate(payload)


def add_unsupported_extension(resource: Any, field_path: str, value: Any) -> None:
    """
    Store unsupported fields in extensions so your dataset contract stays complete.

    Example:
      field_path="contact"
      url="https://fhirlake.dev/unsupported/contact"
      valueString="[...]"
    """
    ext = Extension.model_validate({
        "url": f"https://fhirlake.dev/unsupported/{field_path}",
        "valueString": _as_json_string(value),
    })

    # Ensure extension list exists
    existing = getattr(resource, "extension", None)
    if existing is None:
        resource.extension = []
    resource.extension.append(ext)


def safe_set(resource: Any, field_name: str, value: Any, *, unsupported_path: Optional[str] = None) -> None:
    """
    Try to set a field on a FHIR model.
    If the field doesn't exist / validation fails, store it as an unsupported extension.
    """
    try:
        setattr(resource, field_name, value)
    except Exception:
        add_unsupported_extension(resource, unsupported_path or field_name, value)


# --------------------------------
# Location Generator Configuration
# --------------------------------

@dataclass
class LocationGeneratorConfig:
    identifier_system: str = "MetricCare-LOC"
    include_geo: bool = True
    allow_virtual_service: bool = True
    allow_hours_of_operation: bool = True
    allow_endpoint_refs: bool = True

    # If you want hierarchical location trees (Hospital -> Building -> Ward -> Room -> Bed),
    # set these probabilities higher.
    probability_part_of: float = 0.45


# ----------------------------
# Location Generator (Main)
# ----------------------------

class LocationGenerator:
    """
    Generates synthetic Location resources.

    Optional linking:
      - managingOrganization: Reference("Organization/<id>")
      - partOf: Reference("Location/<id>")
      - endpoint: [Reference("Endpoint/<id>")]

    If you do not have those resources yet, you can still generate references as strings.
    """

    def __init__(self, config: Optional[LocationGeneratorConfig] = None, seed: Optional[int] = None) -> None:
        self.config = config or LocationGeneratorConfig()
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)

    def generate_location(
        self,
        *,
        location_id: Optional[str] = None,
        managing_org_ref: Optional[str] = None,
        part_of_ref: Optional[str] = None,
        endpoint_refs: Optional[List[str]] = None
    ) -> Location:
        loc_id = location_id or _uuid()

        # Choose a location “form” + human name pattern
        location_forms = [
            ("building", "Building"),
            ("wing", "Wing"),
            ("ward", "Ward"),
            ("room", "Room"),
            ("bed", "Bed"),
            ("clinic", "Clinic"),
            ("lab", "Laboratory"),
            ("imaging", "Imaging"),
            ("virtual", "Virtual")
        ]
        form_code, form_label = random.choice(location_forms)

        base_name = fake.company() if form_code in {"building", "clinic"} else fake.word().title()
        human_name = self._build_location_name(form_code, base_name)

        status = random.choice(["active", "suspended", "inactive"])
        mode = random.choice(["instance", "kind"])

        # Build Location
        location = Location.model_validate({
            "resourceType": "Location",
            "id": loc_id,
            "status": status,
            "mode": mode,
            "name": human_name,
            "description": self._build_description(form_code, human_name),
            "alias": self._build_aliases(human_name),
            "identifier": [
                make_identifier(
                    system=self.config.identifier_system,
                    value=f"LOC-{fake.unique.random_int(min=100000, max=999999)}",
                    type_text="Facility Location Code"
                ).model_dump(exclude_none=True)
            ],
        })

        # operationalStatus (typically bed/room)
        operational_status = self._build_operational_status(form_code)
        if operational_status:
            safe_set(location, "operationalStatus", operational_status, unsupported_path="operationalStatus")

        # code (geo/admin code set placeholder)
        # Note: In real systems you might use ISO region codes or internal geo codes.
        code_cc = make_codeable_concept(
            [make_coding("https://fhirlake.dev/codes/location-code", fake.state_abbr(), "Administrative Code")],
            text="Administrative Location Code"
        )
        safe_set(location, "code", [code_cc], unsupported_path="code")

        # type (service type)
        loc_type = self._build_location_type(form_code)
        safe_set(location, "type", [loc_type], unsupported_path="type")

        # contact (ExtendedContactDetail in newer specs; may not exist in your fhir.resources)
        contact_payload = self._build_contact_details()
        safe_set(location, "contact", contact_payload, unsupported_path="contact")

        # address
        address = Address.model_validate({
            "line": [fake.street_address()],
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postalCode": fake.postcode(),
            "country": "US"
        })
        safe_set(location, "address", address, unsupported_path="address")

        # form (physical form) - v6 uses Location.form
        form_cc = make_codeable_concept(
            [make_coding("https://fhirlake.dev/codes/location-form", form_code, form_label)],
            text=form_label
        )
        safe_set(location, "form", form_cc, unsupported_path="form")

        # position (geo)
        if self.config.include_geo:
            position_obj = self._build_position()
            safe_set(location, "position", position_obj, unsupported_path="position")

        # managingOrganization
        if managing_org_ref:
            safe_set(location, "managingOrganization", make_reference(managing_org_ref), unsupported_path="managingOrganization")

        # partOf (hierarchy)
        final_part_of_ref = part_of_ref
        if not final_part_of_ref and random.random() < self.config.probability_part_of and form_code not in {"building"}:
            # If caller didn't pass parent, create a placeholder reference (still valid string)
            final_part_of_ref = f"Location/{_uuid()}"

        if final_part_of_ref:
            safe_set(location, "partOf", make_reference(final_part_of_ref), unsupported_path="partOf")

        # characteristic
        characteristic = self._build_characteristics(form_code)
        if characteristic:
            safe_set(location, "characteristic", characteristic, unsupported_path="characteristic")

        # hoursOfOperation (Availability in newer specs)
        if self.config.allow_hours_of_operation:
            hours_payload = self._build_hours_of_operation(form_code)
            if hours_payload:
                safe_set(location, "hoursOfOperation", hours_payload, unsupported_path="hoursOfOperation")

        # virtualService (VirtualServiceDetail)
        if self.config.allow_virtual_service:
            vs_payload = self._build_virtual_service(form_code)
            if vs_payload:
                safe_set(location, "virtualService", vs_payload, unsupported_path="virtualService")

        # endpoint references
        if self.config.allow_endpoint_refs:
            refs = endpoint_refs or self._maybe_generate_endpoint_refs(form_code)
            if refs:
                safe_set(location, "endpoint", [make_reference(r) for r in refs], unsupported_path="endpoint")

        return location

    # ----------------------------
    # Field builders
    # ----------------------------

    def _build_location_name(self, form_code: str, base: str) -> str:
        if form_code == "building":
            return f"{base} Medical Center"
        if form_code == "wing":
            return f"{base} Wing"
        if form_code == "ward":
            return f"Ward {random.randint(1, 12)}"
        if form_code == "room":
            return f"Room {random.randint(100, 599)}"
        if form_code == "bed":
            return f"Bed {random.choice(['A', 'B', 'C'])}{random.randint(1, 9)}"
        if form_code == "clinic":
            return f"{base} Outpatient Clinic"
        if form_code == "lab":
            return f"{base} Lab"
        if form_code == "imaging":
            return f"{base} Imaging"
        if form_code == "virtual":
            return f"{base} Virtual Visit"
        return f"{base} Location"

    def _build_aliases(self, name: str) -> List[str]:
        aliases = []
        if random.random() < 0.35:
            aliases.append(name.replace("Medical Center", "MC"))
        if random.random() < 0.25:
            aliases.append(f"{name} (Legacy)")
        return aliases

    def _build_description(self, form_code: str, name: str) -> str:
        templates = {
            "building": f"{name} main facility providing inpatient and outpatient services.",
            "ward": f"{name} inpatient ward for general care and monitoring.",
            "room": f"{name} patient room used for short stay and observation.",
            "bed": f"{name} bed space used for patient accommodation.",
            "clinic": f"{name} outpatient clinic supporting scheduled visits.",
            "lab": f"{name} diagnostic laboratory supporting specimen processing.",
            "imaging": f"{name} radiology/imaging department supporting scans and procedures.",
            "virtual": f"{name} virtual service location for telehealth appointments.",
        }
        return templates.get(form_code, f"{name} service location.")

    def _build_operational_status(self, form_code: str) -> Optional[Coding]:
        # Spec notes operationalStatus is often relevant for bed/room states (e.g., housekeeping, isolation).
        if form_code not in {"bed", "room", "ward"}:
            return None

        # Placeholder coding system (your project can replace with real terminology later)
        choices = [
            ("operational", "Operational"),
            ("housekeeping", "Housekeeping"),
            ("isolated", "Isolation"),
            ("maintenance", "Maintenance"),
            ("closed", "Closed Temporarily"),
        ]
        code, display = random.choice(choices)
        return make_coding("https://fhirlake.dev/codes/bed-status", code, display)

    def _build_location_type(self, form_code: str) -> CodeableConcept:
        # Real binding is “Service type”; we keep a stable local system for synthetic output.
        mapping = {
            "building": ("facility", "Facility"),
            "ward": ("inpatient", "Inpatient Care"),
            "room": ("inpatient", "Inpatient Care"),
            "bed": ("inpatient", "Inpatient Care"),
            "clinic": ("outpatient", "Outpatient Care"),
            "lab": ("laboratory", "Laboratory"),
            "imaging": ("radiology", "Radiology"),
            "virtual": ("telehealth", "Telehealth"),
            "wing": ("facility", "Facility"),
        }
        code, display = mapping.get(form_code, ("facility", "Facility"))
        return make_codeable_concept(
            [make_coding("https://fhirlake.dev/codes/service-type", code, display)],
            text=display
        )

    def _build_contact_details(self) -> List[Dict[str, Any]]:
        """
        ExtendedContactDetail may not exist in your local fhir.resources build.
        So we construct a JSON-ish payload and safe_set() will either accept it or push to unsupported extension.

        You can later replace this with real fhir.resources datatypes if available.
        """
        telecom = []
        if random.random() < 0.85:
            telecom.append({"system": "phone", "value": fake.phone_number(), "use": "work"})
        if random.random() < 0.50:
            telecom.append({"system": "email", "value": fake.company_email(), "use": "work"})
        if random.random() < 0.30:
            telecom.append({"system": "url", "value": f"https://{fake.domain_name()}/locations", "use": "work"})

        # ExtendedContactDetail-like structure (best-effort)
        return [{
            "purpose": {"text": "Official Location Contact"},
            "telecom": telecom,
        }]

    def _build_position(self) -> Dict[str, Any]:
        # Roughly US-ish lat/long ranges (you can localize later)
        lat = round(random.uniform(25.0, 49.0), 6)
        lon = round(random.uniform(-124.0, -66.0), 6)
        alt = round(random.uniform(0, 350), 2) if random.random() < 0.35 else None

        payload: Dict[str, Any] = {
            "latitude": lat,
            "longitude": lon,
        }
        if alt is not None:
            payload["altitude"] = alt
        return payload

    def _build_characteristics(self, form_code: str) -> Optional[List[CodeableConcept]]:
        """
        characteristic is a list of CodeableConcept attributes (e.g., isolation-capable, wheelchair-accessible).
        """
        pool = [
            ("wheelchair", "Wheelchair Accessible"),
            ("isolation", "Isolation Capable"),
            ("pediatric", "Pediatric Friendly"),
            ("icu", "ICU Capable"),
            ("negative-pressure", "Negative Pressure Room"),
        ]

        # More likely for rooms/wards
        probability = 0.55 if form_code in {"ward", "room", "bed"} else 0.20
        if random.random() > probability:
            return None

        chosen = random.sample(pool, k=random.randint(1, 2))
        return [
            make_codeable_concept(
                [make_coding("https://fhirlake.dev/codes/location-characteristic", c, d)],
                text=d
            )
            for c, d in chosen
        ]

    def _build_hours_of_operation(self, form_code: str) -> Optional[Dict[str, Any]]:
        """
        Newer specs use Availability datatype.
        Many python FHIR libs may not have it implemented the same way yet.
        So we emit a best-effort JSON payload and rely on safe_set fallback if unsupported.
        """
        if form_code in {"bed", "room", "ward", "building"}:
            # typically always open
            return {
                "availableTime": [
                    {"daysOfWeek": ["mon","tue","wed","thu","fri","sat","sun"], "allDay": True}
                ],
                "notAvailableTime": []
            }

        if random.random() < 0.40:
            return {
                "availableTime": [
                    {"daysOfWeek": ["mon","tue","wed","thu","fri"], "availableStartTime": "08:00", "availableEndTime": "17:00"}
                ],
                "notAvailableTime": []
            }

        return None

    def _build_virtual_service(self, form_code: str) -> Optional[List[Dict[str, Any]]]:
        """
        Only meaningful for virtual locations, but can exist for others too.
        Uses VirtualServiceDetail datatype in newer specs; fallback to extension if unsupported.
        """
        if form_code != "virtual" and random.random() > 0.12:
            return None

        meeting_id = fake.bothify(text="###-###-####")
        return [{
            "channelType": {"text": "video"},
            "addressUrl": f"https://meet.example.org/{meeting_id}",
            "additionalInfo": [f"Join code: {meeting_id}"]
        }]

    def _maybe_generate_endpoint_refs(self, form_code: str) -> Optional[List[str]]:
        if form_code == "virtual" and random.random() < 0.60:
            return [f"Endpoint/{_uuid()}"]
        if random.random() < 0.10:
            return [f"Endpoint/{_uuid()}"]
        return None


# -------------------------------------------------
# NEW-STYLE ENTRYPOINT (REQUIRED BY CORE ENGINE)
# -------------------------------------------------

def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    """
    Core Engine contract:
      generate(ctx, store, inputs, count) -> list[dict]

    - Generates 'count' locations
    - Converts FHIR object -> dict
    - Registers IDs into ResourceStore pools
    """
    resources: List[Dict[str, Any]] = []
    gen = LocationGenerator(seed=getattr(ctx, "seed", None))

    org_id = inputs.get("organization_id")
    if not org_id:
        raise ValueError(
            "Location generator requires inputs['organization_id']. "
            "Fix: registry spec.required_inputs must include 'organization_id' "
            "and Planning dependencies must include 'Organization'."
        )

    for _ in range(int(count)):
        loc_obj = gen.generate_location(
            managing_org_ref=f"Organization/{org_id}"
        )

        if hasattr(loc_obj, "model_dump"):
            loc_dict = loc_obj.model_dump(exclude_none=True)
        else:
            loc_dict = loc_obj.dict(exclude_none=True)

        lid = loc_dict.get("id")
        if lid:
            store.register_id("Location", lid)

        resources.append(loc_dict)

    return resources


# ----------------------------
# Example usage (quick test)
# ----------------------------

if __name__ == "__main__":
    gen = LocationGenerator(seed=42)

    # Example: link to managing organization + optional parent location
    loc = gen.generate_location(
        managing_org_ref="Organization/metriccare-health",
        part_of_ref=None,  # generator may create placeholder parent
        endpoint_refs=None
    )

    print(json.dumps(loc.model_dump(exclude_none=True), indent=2))
