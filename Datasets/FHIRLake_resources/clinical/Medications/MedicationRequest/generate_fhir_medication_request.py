from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from faker import Faker

try:
    from fhir.resources.medicationrequest import MedicationRequest
except Exception:  # pragma: no cover - optional dependency at runtime
    MedicationRequest = None

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


def _random_medication_concept() -> Dict[str, Any]:
    pool = [
        ("313782", "Acetaminophen 325 MG Oral Tablet"),
        ("1049630", "Amoxicillin 500 MG Capsule"),
        ("860975", "Atorvastatin 20 MG Tablet"),
        ("855332", "Lisinopril 10 MG Tablet"),
    ]
    code, display = random.choice(pool)
    return _codeable_concept("http://www.nlm.nih.gov/research/umls/rxnorm", code, display)


def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    resources: List[Dict[str, Any]] = []

    patient_id = inputs.get("patient_id")
    encounter_id = inputs.get("encounter_id")
    practitioner_id = inputs.get("practitioner_id")
    organization_id = inputs.get("organization_id")

    if not patient_id:
        raise ValueError("MedicationRequest generator requires inputs['patient_id'].")

    for _ in range(int(count)):
        med_id = str(uuid.uuid4())

        payload: Dict[str, Any] = {
            "resourceType": "MedicationRequest",
            "id": med_id,
            "identifier": [
                {
                    "system": "MetricCare-MedicationRequest",
                    "value": f"MRX-{fake.unique.random_int(100000, 999999)}",
                }
            ],
            "status": random.choice(
                [
                    "active",
                    "on-hold",
                    "ended",
                    "stopped",
                    "completed",
                    "cancelled",
                    "entered-in-error",
                    "draft",
                    "unknown",
                ]
            ),
            "intent": random.choice(
                [
                    "proposal",
                    "plan",
                    "order",
                    "original-order",
                    "reflex-order",
                    "filler-order",
                    "instance-order",
                    "option",
                ]
            ),
            "subject": {"reference": f"Patient/{patient_id}"},
            "authoredOn": _now_iso(),
        }

        med_concept = _random_medication_concept()
        if _has_field(MedicationRequest, "medication"):
            payload["medication"] = {"concept": med_concept}
        elif _has_field(MedicationRequest, "medicationCodeableConcept"):
            payload["medicationCodeableConcept"] = med_concept
        else:
            payload["medicationReference"] = {"reference": "Medication/example"}

        if encounter_id:
            _set_if(payload, MedicationRequest, "encounter", {"reference": f"Encounter/{encounter_id}"})

        # requester (practitioner or organization)
        requester_ref: Optional[Dict[str, Any]] = None
        if practitioner_id:
            requester_ref = {"reference": f"Practitioner/{practitioner_id}"}
        elif organization_id:
            requester_ref = {"reference": f"Organization/{organization_id}"}
        if requester_ref:
            _set_if(payload, MedicationRequest, "requester", requester_ref)

        if random.random() < 0.5:
            _set_if(
                payload,
                MedicationRequest,
                "dosageInstruction",
                [{"text": "Take one tablet by mouth once daily"}],
            )

        if MedicationRequest:
            if hasattr(MedicationRequest, "model_validate"):
                med_obj = MedicationRequest.model_validate(payload)
            else:
                med_obj = MedicationRequest(**payload)

            if hasattr(med_obj, "model_dump"):
                med_dict = med_obj.model_dump(exclude_none=True)
            else:
                med_dict = med_obj.dict(exclude_none=True)
        else:
            med_dict = payload

        mid = med_dict.get("id")
        if mid:
            store.register_id("MedicationRequest", mid)

        resources.append(med_dict)

    return resources


if __name__ == "__main__":
    class _DummyStore:
        def register_id(self, *_args, **_kwargs):
            return None

    sample = generate(None, _DummyStore(), {"patient_id": "pat-1"}, 1)
    print(sample[0])
