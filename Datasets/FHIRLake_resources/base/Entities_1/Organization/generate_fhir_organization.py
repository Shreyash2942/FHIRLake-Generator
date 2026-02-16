"""
FHIRLake Generator - Organization Resource Generator (FHIR R5+)

Generates synthetic FHIR Organization resources using:
- fhir.resources (pydantic FHIR models)
- Faker (realistic-ish names, contact data, addresses)
- Contract-preserving fallback: if a field/datatype is not supported by your installed fhir.resources,
  we store it under Organization.extension as:
    url = "https://fhirlake.dev/unsupported/<fieldPath>"
    valueString = "<json/text>"

FHIR Spec reference (fields):
- Organization.identifier, active, type, name, alias, description, contact, partOf, endpoint, qualification
"""

from __future__ import annotations

import json
import random
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

from faker import Faker

from fhir.resources.organization import Organization
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding
from fhir.resources.codeableconcept import CodeableConcept
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


def make_identifier(system: str, value: str, use: str = "usual", type_text: str = "Organization Identifier") -> Identifier:
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


# ------------------------------------
# Organization Generator Configuration
# ------------------------------------

@dataclass
class OrganizationGeneratorConfig:
    identifier_system: str = "MetricCare-ORG"
    allow_part_of: bool = True
    allow_endpoint_refs: bool = True
    allow_qualification: bool = True

    # Probability knobs
    probability_alias: float = 0.55
    probability_description: float = 0.70
    probability_part_of: float = 0.40
    probability_endpoint: float = 0.35
    probability_qualification: float = 0.45


# ----------------------------
# Organization Generator (Main)
# ----------------------------

class OrganizationGenerator:
    """
    Generates synthetic Organization resources.

    Optional linking:
      - partOf: Reference("Organization/<id>")
      - endpoint: [Reference("Endpoint/<id>")]
      - qualification.issuer: Reference("Organization/<id>")

    If you do not have those resources yet, you can still generate references as strings.
    """

    def __init__(self, config: Optional[OrganizationGeneratorConfig] = None, seed: Optional[int] = None) -> None:
        self.config = config or OrganizationGeneratorConfig()
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)

    def generate_organization(
        self,
        *,
        organization_id: Optional[str] = None,
        part_of_ref: Optional[str] = None,
        endpoint_refs: Optional[List[str]] = None,
        qualification_issuer_ref: Optional[str] = None,
    ) -> Organization:
        org_id = organization_id or _uuid()

        org_kind = random.choice([
            ("prov", "Healthcare Provider"),
            ("dept", "Hospital Department"),
            ("pay", "Payer"),
            ("ins", "Insurance Company"),
            ("govt", "Government"),
            ("edu", "Education / Training"),
            ("other", "Other"),
        ])

        name = self._build_org_name(org_kind[0])

        # Base Organization (safe: common fields usually exist)
        org = Organization.model_validate({
            "resourceType": "Organization",
            "id": org_id,
            "active": True,
            "name": name,
            "identifier": [
                make_identifier(
                    system=self.config.identifier_system,
                    value=f"ORG-{fake.unique.random_int(min=100000, max=999999)}",
                    type_text="Facility / Organization Code"
                ).model_dump(exclude_none=True)
            ],
        })

        # type
        org_type_cc = make_codeable_concept(
            [make_coding("http://terminology.hl7.org/CodeSystem/organization-type", org_kind[0], org_kind[1])],
            text=org_kind[1]
        )
        safe_set(org, "type", [org_type_cc], unsupported_path="type")

        # alias
        if random.random() < self.config.probability_alias:
            safe_set(org, "alias", self._build_aliases(name), unsupported_path="alias")

        # description (markdown)
        if random.random() < self.config.probability_description:
            safe_set(org, "description", self._build_description(org_kind[0], name), unsupported_path="description")

        # contact (FHIR R5: ExtendedContactDetail) — often missing in python libs, so JSON-ish payload + fallback.
        contact_payload = self._build_contact_details()
        safe_set(org, "contact", contact_payload, unsupported_path="contact")

        # partOf
        if self.config.allow_part_of:
            final_part_of_ref = part_of_ref
            if not final_part_of_ref and random.random() < self.config.probability_part_of:
                final_part_of_ref = f"Organization/{_uuid()}"
            if final_part_of_ref:
                safe_set(org, "partOf", make_reference(final_part_of_ref, "Parent Organization"), unsupported_path="partOf")

        # endpoint
        if self.config.allow_endpoint_refs:
            refs = endpoint_refs or self._maybe_generate_endpoint_refs()
            if refs:
                safe_set(org, "endpoint", [make_reference(r) for r in refs], unsupported_path="endpoint")

        # qualification (BackboneElement array)
        if self.config.allow_qualification and random.random() < self.config.probability_qualification:
            qualification_payload = self._build_qualification_payload(qualification_issuer_ref)
            safe_set(org, "qualification", qualification_payload, unsupported_path="qualification")

        return org

    # ----------------------------
    # Field builders
    # ----------------------------

    def _build_org_name(self, org_kind_code: str) -> str:
        brand = random.choice(["MetricCare", "Harmony", "BlueRiver", "NorthStar", "Crescent", "Pinecrest"])
        if org_kind_code == "prov":
            return f"{brand} {random.choice(['General Hospital', 'Medical Center', 'Health'])}"
        if org_kind_code == "dept":
            return f"{brand} {random.choice(['Cardiology', 'Emergency', 'ICU', 'Radiology', 'Laboratory'])} Department"
        if org_kind_code in {"pay", "ins"}:
            return f"{brand} {random.choice(['Health Plan', 'Insurance', 'Payer Services'])}"
        if org_kind_code == "govt":
            return f"{random.choice(['State', 'County', 'City'])} Health Authority"
        if org_kind_code == "edu":
            return f"{brand} Clinical Training Institute"
        return f"{brand} Organization"

    def _build_aliases(self, name: str) -> List[str]:
        aliases: List[str] = []

        # Common abbreviations
        if "Medical Center" in name:
            aliases.append(name.replace("Medical Center", "MC"))
        if "General Hospital" in name:
            aliases.append(name.replace("General Hospital", "GH"))

        # Short brand alias
        aliases.append(name.split()[0])

        # Sometimes include legacy
        if random.random() < 0.30:
            aliases.append(f"{name} (Legacy)")

        # de-dup while keeping order
        seen = set()
        out = []
        for a in aliases:
            if a and a not in seen:
                out.append(a)
                seen.add(a)
        return out

    def _build_description(self, org_kind_code: str, name: str) -> str:
        templates = {
            "prov": f"{name} provides inpatient, outpatient, and emergency services.",
            "dept": f"{name} delivers specialty clinical services within a larger facility.",
            "pay": f"{name} manages coverage, claims, and member services for healthcare plans.",
            "ins": f"{name} provides insurance products and benefits administration.",
            "govt": f"{name} supports public health programs and regulatory oversight.",
            "edu": f"{name} provides clinical education, training, and accreditation support.",
            "other": f"{name} is an organization participating in healthcare operations and administration.",
        }
        return templates.get(org_kind_code, f"{name} organization record.")

    def _build_contact_details(self) -> List[Dict[str, Any]]:
        """
        ExtendedContactDetail may not exist in your local fhir.resources build.
        We emit best-effort JSON that safe_set() will either accept or push to unsupported extension.
        """
        telecom: List[Dict[str, Any]] = []

        if random.random() < 0.85:
            telecom.append({"system": "phone", "value": fake.phone_number(), "use": "work"})
        if random.random() < 0.55:
            telecom.append({"system": "email", "value": fake.company_email(), "use": "work"})
        if random.random() < 0.30:
            telecom.append({"system": "url", "value": f"https://{fake.domain_name()}", "use": "work"})

        address = {
            "line": [fake.street_address()],
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postalCode": fake.postcode(),
            "country": "US",
        }

        return [{
            "purpose": {"text": "Official Organization Contact"},
            "name": {"text": "Main Office"},
            "telecom": telecom,
            "address": address,
        }]

    def _build_qualification_payload(self, issuer_ref: Optional[str]) -> List[Dict[str, Any]]:
        """
        Organization.qualification is a backbone element list.

        Some fhir.resources builds may not include OrganizationQualification datatype explicitly.
        So we emit payload dicts and rely on safe_set fallback if unsupported.
        """
        # A tiny controlled set of "qualification codes" (replace later with your preferred terminology)
        qual = random.choice([
            ("HOS", "Hospital Accreditation"),
            ("LIC", "Facility License"),
            ("CERT", "Quality Certification"),
            ("LAB", "Laboratory Certification"),
        ])

        status_text = random.choice(["Active", "Pending", "Expired"])

        start_year = random.randint(2019, 2025)
        end_year = start_year + random.randint(1, 5)

        payload = [{
            "identifier": [{
                "use": "official",
                "type": {"text": "Qualification / Accreditation ID"},
                "system": "MetricCare-QUAL",
                "value": f"QUAL-{fake.unique.random_int(min=100000, max=999999)}"
            }],
            "code": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
                    "code": qual[0],
                    "display": qual[1]
                }],
                "text": qual[1]
            },
            "status": {"text": status_text},
            "period": {
                "start": str(date(start_year, 1, 1)),
                "end": str(date(end_year, 12, 31)),
            },
            "issuer": {
                "reference": issuer_ref or f"Organization/{_uuid()}",
                "display": random.choice([
                    "National Accreditation Board",
                    "State Health Licensing Agency",
                    "Clinical Standards Authority",
                ])
            }
        }]

        return payload

    def _maybe_generate_endpoint_refs(self) -> Optional[List[str]]:
        if random.random() < self.config.probability_endpoint:
            return [f"Endpoint/{_uuid()}"]
        return None


# -------------------------------------------------
# NEW-STYLE ENTRYPOINT (REQUIRED BY CORE ENGINE)
# -------------------------------------------------

def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    """
    Core Engine contract:
      generate(ctx, store, inputs, count) -> list[dict]

    - Generates 'count' organizations
    - Converts FHIR object -> dict
    - Registers IDs into ResourceStore pools
    """
    resources: List[Dict[str, Any]] = []
    gen = OrganizationGenerator(seed=getattr(ctx, "seed", None))

    for _ in range(int(count)):
        org_obj = gen.generate_organization()

        if hasattr(org_obj, "model_dump"):
            org_dict = org_obj.model_dump(exclude_none=True)
        else:
            org_dict = org_obj.dict(exclude_none=True)

        oid = org_dict.get("id")
        if oid:
            store.register_id("Organization", oid)

        resources.append(org_dict)

    return resources


# ----------------------------
# Example usage (quick test)
# ----------------------------

if __name__ == "__main__":
    gen = OrganizationGenerator(seed=42)

    org = gen.generate_organization(
        part_of_ref="Organization/metriccare-health-system",
        endpoint_refs=None,
        qualification_issuer_ref="Organization/national-accreditation-board"
    )

    print(json.dumps(org.model_dump(exclude_none=True), indent=2))
