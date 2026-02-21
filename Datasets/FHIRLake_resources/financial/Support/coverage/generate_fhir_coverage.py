from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from faker import Faker

try:
    from fhir.resources.coverage import Coverage
except Exception:  # pragma: no cover - optional dependency at runtime
    Coverage = None

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


def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    resources: List[Dict[str, Any]] = []

    patient_id = inputs.get("patient_id")
    organization_id = inputs.get("organization_id")

    if not patient_id:
        raise ValueError("Coverage generator requires inputs['patient_id'].")

    for _ in range(int(count)):
        coverage_id = str(uuid.uuid4())

        payload: Dict[str, Any] = {
            "resourceType": "Coverage",
            "id": coverage_id,
            "identifier": [
                {
                    "system": "MetricCare-Coverage",
                    "value": f"COV-{fake.unique.random_int(100000, 999999)}",
                }
            ],
            "status": random.choice(["active", "cancelled", "draft", "entered-in-error"]),
            "beneficiary": {"reference": f"Patient/{patient_id}"},
            "period": {"start": _now_iso()},
        }

        # Apply kind and required fields per rule
        if organization_id:
            _set_if(payload, Coverage, "kind", "insurance")
            _set_if(payload, Coverage, "insurer", {"reference": f"Organization/{organization_id}"})
        else:
            _set_if(payload, Coverage, "kind", "self-pay")
            payment_by = [{"party": {"reference": f"Patient/{patient_id}"}, "responsibility": "Self-pay"}]
            _set_if(payload, Coverage, "paymentBy", payment_by)

        if random.random() < 0.6:
            _set_if(
                payload,
                Coverage,
                "type",
                _codeable_concept(
                    "http://terminology.hl7.org/CodeSystem/coverage-type",
                    "medical",
                    "Medical",
                ),
            )

        if random.random() < 0.5:
            _set_if(payload, Coverage, "policyHolder", {"reference": f"Patient/{patient_id}"})
            _set_if(payload, Coverage, "subscriber", {"reference": f"Patient/{patient_id}"})

        if random.random() < 0.5:
            _set_if(payload, Coverage, "subscriberId", [{"value": f"SUB-{fake.random_int(10000, 99999)}"}])

        if Coverage:
            if hasattr(Coverage, "model_validate"):
                cov_obj = Coverage.model_validate(payload)
            else:
                cov_obj = Coverage(**payload)

            if hasattr(cov_obj, "model_dump"):
                cov_dict = cov_obj.model_dump(exclude_none=True)
            else:
                cov_dict = cov_obj.dict(exclude_none=True)
        else:
            cov_dict = payload

        cid = cov_dict.get("id")
        if cid:
            store.register_id("Coverage", cid)

        resources.append(cov_dict)

    return resources


if __name__ == "__main__":
    class _DummyStore:
        def register_id(self, *_args, **_kwargs):
            return None

    sample = generate(None, _DummyStore(), {"patient_id": "pat-1"}, 1)
    print(sample[0])
