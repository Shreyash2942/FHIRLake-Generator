from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from faker import Faker

try:
    from fhir.resources.claim import Claim
except Exception:  # pragma: no cover - optional dependency at runtime
    Claim = None

fake = Faker()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _has_field(model: Optional[Any], name: str) -> bool:
    if model is None:
        return True
    if hasattr(model, "model_fields"):
        return name in model.model_fields
    if hasattr(model, "__fields__"):
        return name in model.__fields__
    return True


def _set_if(payload: Dict[str, Any], model: Optional[Any], name: str, value: Any) -> None:
    if _has_field(model, name):
        payload[name] = value


def _codeable_concept(system: str, code: str, display: str) -> Dict[str, Any]:
    return {
        "coding": [{"system": system, "code": code, "display": display}],
        "text": display,
    }


def _random_claim_type() -> Dict[str, Any]:
    pool = [
        ("professional", "Professional"),
        ("institutional", "Institutional"),
        ("pharmacy", "Pharmacy"),
        ("oral", "Oral"),
    ]
    code, display = random.choice(pool)
    return _codeable_concept("http://terminology.hl7.org/CodeSystem/claim-type", code, display)


def _random_product_or_service() -> Dict[str, Any]:
    pool = [
        ("99213", "Office or other outpatient visit"),
        ("93000", "Electrocardiogram"),
        ("71020", "Chest x-ray"),
    ]
    code, display = random.choice(pool)
    return _codeable_concept("http://www.ama-assn.org/go/cpt", code, display)


def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    resources: List[Dict[str, Any]] = []

    patient_id = inputs.get("patient_id")
    encounter_id = inputs.get("encounter_id")
    practitioner_id = inputs.get("practitioner_id")
    organization_id = inputs.get("organization_id")

    if not patient_id:
        raise ValueError("Claim generator requires inputs['patient_id'].")

    for _ in range(int(count)):
        claim_id = str(uuid.uuid4())

        payload: Dict[str, Any] = {
            "resourceType": "Claim",
            "id": claim_id,
            "identifier": [
                {
                    "system": "MetricCare-Claim",
                    "value": f"CLM-{fake.unique.random_int(100000, 999999)}",
                }
            ],
            "status": random.choice(["active", "cancelled", "draft", "entered-in-error"]),
            "type": _random_claim_type(),
            "use": random.choice(["claim", "preauthorization", "predetermination"]),
            "subject": {"reference": f"Patient/{patient_id}"},
            "created": _now_iso(),
        }

        # provider / insurer
        if practitioner_id:
            _set_if(payload, Claim, "provider", {"reference": f"Practitioner/{practitioner_id}"})
        elif organization_id:
            _set_if(payload, Claim, "provider", {"reference": f"Organization/{organization_id}"})
            _set_if(payload, Claim, "insurer", {"reference": f"Organization/{organization_id}"})

        if encounter_id:
            _set_if(payload, Claim, "encounter", [{"reference": f"Encounter/{encounter_id}"}])

        if random.random() < 0.7:
            _set_if(payload, Claim, "priority", _codeable_concept(
                "http://terminology.hl7.org/CodeSystem/processpriority", "normal", "Normal"
            ))

        if random.random() < 0.8:
            item = {
                "sequence": 1,
                "productOrService": _random_product_or_service(),
                "quantity": {"value": 1},
                "unitPrice": {"value": round(random.uniform(50, 500), 2), "currency": "USD"},
            }
            _set_if(payload, Claim, "item", [item])

        if Claim:
            if hasattr(Claim, "model_validate"):
                claim_obj = Claim.model_validate(payload)
            else:
                claim_obj = Claim(**payload)

            if hasattr(claim_obj, "model_dump"):
                claim_dict = claim_obj.model_dump(exclude_none=True)
            else:
                claim_dict = claim_obj.dict(exclude_none=True)
        else:
            claim_dict = payload

        cid = claim_dict.get("id")
        if cid:
            store.register_id("Claim", cid)

        resources.append(claim_dict)

    return resources


if __name__ == "__main__":
    class _DummyStore:
        def register_id(self, *_args, **_kwargs):
            return None

    sample = generate(None, _DummyStore(), {"patient_id": "pat-1"}, 1)
    print(sample[0])
