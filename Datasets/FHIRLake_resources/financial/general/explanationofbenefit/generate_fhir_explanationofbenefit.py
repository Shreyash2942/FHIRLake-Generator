from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from faker import Faker

try:
    from fhir.resources.explanationofbenefit import ExplanationOfBenefit
except Exception:  # pragma: no cover - optional dependency at runtime
    ExplanationOfBenefit = None

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


def _random_eob_type() -> Dict[str, Any]:
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


def _random_outcome() -> str:
    return random.choice(["queued", "complete", "error", "partial"])


def _random_status() -> str:
    return random.choice(["active", "cancelled", "draft", "entered-in-error"])


def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    resources: List[Dict[str, Any]] = []

    patient_id = inputs.get("patient_id")
    claim_id = inputs.get("claim_id")
    coverage_id = inputs.get("coverage_id")
    encounter_id = inputs.get("encounter_id")
    practitioner_id = inputs.get("practitioner_id")
    organization_id = inputs.get("organization_id")
    procedure_id = inputs.get("procedure_id")
    medication_request_id = inputs.get("medication_request_id")

    if not patient_id:
        raise ValueError("ExplanationOfBenefit generator requires inputs['patient_id'].")

    for _ in range(int(count)):
        eob_id = str(uuid.uuid4())

        payload: Dict[str, Any] = {
            "resourceType": "ExplanationOfBenefit",
            "id": eob_id,
            "identifier": [
                {
                    "system": "MetricCare-EOB",
                    "value": f"EOB-{fake.unique.random_int(100000, 999999)}",
                }
            ],
            "status": _random_status(),
            "type": _random_eob_type(),
            "use": random.choice(["claim", "preauthorization", "predetermination"]),
            "created": _now_iso(),
            "outcome": _random_outcome(),
        }

        subject_ref = {"reference": f"Patient/{patient_id}"}
        if _has_field(ExplanationOfBenefit, "subject"):
            payload["subject"] = subject_ref
        elif _has_field(ExplanationOfBenefit, "patient"):
            payload["patient"] = subject_ref

        if claim_id:
            _set_if(payload, ExplanationOfBenefit, "claim", {"reference": f"Claim/{claim_id}"})

        if encounter_id:
            _set_if(payload, ExplanationOfBenefit, "encounter", [{"reference": f"Encounter/{encounter_id}"}])

        if practitioner_id:
            _set_if(payload, ExplanationOfBenefit, "provider", {"reference": f"Practitioner/{practitioner_id}"})
        elif organization_id:
            _set_if(payload, ExplanationOfBenefit, "provider", {"reference": f"Organization/{organization_id}"})

        if organization_id:
            _set_if(payload, ExplanationOfBenefit, "insurer", {"reference": f"Organization/{organization_id}"})

        if coverage_id:
            insurance = {"focal": True, "coverage": {"reference": f"Coverage/{coverage_id}"}}
            _set_if(payload, ExplanationOfBenefit, "insurance", [insurance])

        if procedure_id:
            proc = {
                "sequence": 1,
                "procedureReference": {"reference": f"Procedure/{procedure_id}"},
            }
            _set_if(payload, ExplanationOfBenefit, "procedure", [proc])

        if medication_request_id:
            _set_if(
                payload,
                ExplanationOfBenefit,
                "prescription",
                {"reference": f"MedicationRequest/{medication_request_id}"},
            )

        # Basic line item with adjudication
        item = {
            "sequence": 1,
            "productOrService": _random_product_or_service(),
            "quantity": {"value": 1},
            "unitPrice": {"value": round(random.uniform(50, 500), 2), "currency": "USD"},
            "net": {"value": round(random.uniform(50, 500), 2), "currency": "USD"},
            "adjudication": [
                {
                    "category": _codeable_concept(
                        "http://terminology.hl7.org/CodeSystem/adjudication",
                        "eligible",
                        "Eligible Amount",
                    ),
                    "amount": {"value": round(random.uniform(30, 400), 2), "currency": "USD"},
                }
            ],
        }
        _set_if(payload, ExplanationOfBenefit, "item", [item])

        total = {
            "category": _codeable_concept(
                "http://terminology.hl7.org/CodeSystem/adjudication",
                "submitted",
                "Submitted Amount",
            ),
            "amount": {"value": round(random.uniform(100, 1000), 2), "currency": "USD"},
        }
        _set_if(payload, ExplanationOfBenefit, "total", [total])

        if ExplanationOfBenefit:
            if hasattr(ExplanationOfBenefit, "model_validate"):
                eob_obj = ExplanationOfBenefit.model_validate(payload)
            else:
                eob_obj = ExplanationOfBenefit(**payload)

            if hasattr(eob_obj, "model_dump"):
                eob_dict = eob_obj.model_dump(exclude_none=True)
            else:
                eob_dict = eob_obj.dict(exclude_none=True)
        else:
            eob_dict = payload

        rid = eob_dict.get("id")
        if rid:
            store.register_id("ExplanationOfBenefit", rid)

        resources.append(eob_dict)

    return resources


if __name__ == "__main__":
    class _DummyStore:
        def register_id(self, *_args, **_kwargs):
            return None

    sample = generate(None, _DummyStore(), {"patient_id": "pat-1"}, 1)
    print(sample[0])
