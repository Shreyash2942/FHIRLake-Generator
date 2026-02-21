from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from faker import Faker

try:
    from fhir.resources.procedure import Procedure
except Exception:  # pragma: no cover - optional dependency at runtime
    Procedure = None

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


def _random_procedure_code() -> Dict[str, Any]:
    pool = [
        ("80146002", "Appendectomy"),
        ("387713003", "Surgical procedure"),
        ("23426006", "Appendectomy (procedure)"),
        ("172043006", "Physical examination procedure"),
    ]
    code, display = random.choice(pool)
    return _codeable_concept("http://snomed.info/sct", code, display)


def _random_category() -> Dict[str, Any]:
    pool = [
        ("387713003", "Surgical procedure"),
        ("103693007", "Diagnostic procedure"),
        ("108252007", "Laboratory procedure"),
    ]
    code, display = random.choice(pool)
    return _codeable_concept("http://snomed.info/sct", code, display)


def _random_body_site() -> Dict[str, Any]:
    pool = [
        ("49521004", "Upper arm structure"),
        ("45048000", "Hip structure"),
        ("51185008", "Chest structure"),
        ("69536005", "Head structure"),
    ]
    code, display = random.choice(pool)
    return _codeable_concept("http://snomed.info/sct", code, display)


def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    resources: List[Dict[str, Any]] = []

    patient_id = inputs.get("patient_id")
    encounter_id = inputs.get("encounter_id")
    practitioner_id = inputs.get("practitioner_id")
    organization_id = inputs.get("organization_id")

    if not patient_id or not encounter_id:
        raise ValueError(
            "Procedure generator requires inputs['patient_id'] and inputs['encounter_id']."
        )

    for _ in range(int(count)):
        proc_id = str(uuid.uuid4())
        status = random.choice(
            [
                "preparation",
                "in-progress",
                "not-done",
                "on-hold",
                "stopped",
                "completed",
                "entered-in-error",
                "unknown",
            ]
        )

        payload: Dict[str, Any] = {
            "resourceType": "Procedure",
            "id": proc_id,
            "identifier": [
                {
                    "system": "MetricCare-Procedure",
                    "value": f"PROC-{fake.unique.random_int(100000, 999999)}",
                }
            ],
            "status": status,
            "category": [_random_category()],
            "code": _random_procedure_code(),
            "subject": {"reference": f"Patient/{patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
        }

        occurrence_field = "occurrenceDateTime"
        if _has_field(Procedure, "performedDateTime"):
            occurrence_field = "performedDateTime"
        _set_if(payload, Procedure, occurrence_field, _now_iso())
        _set_if(payload, Procedure, "recorded", _now_iso())

        # Performer
        performer_actor: Optional[Dict[str, Any]] = None
        if practitioner_id:
            performer_actor = {"reference": f"Practitioner/{practitioner_id}"}
        elif organization_id:
            performer_actor = {"reference": f"Organization/{organization_id}"}

        if performer_actor:
            payload["performer"] = [{"actor": performer_actor}]

        # bodySite vs bodyStructure rule: never both
        if random.random() < 0.7:
            _set_if(payload, Procedure, "bodySite", [_random_body_site()])
        else:
            if _has_field(Procedure, "bodyStructure"):
                _set_if(payload, Procedure, "bodyStructure", {"reference": "BodyStructure/example"})

        # Optional note
        if random.random() < 0.3:
            _set_if(payload, Procedure, "note", [{"text": "Synthetic procedure record"}])

        if Procedure:
            if hasattr(Procedure, "model_validate"):
                proc_obj = Procedure.model_validate(payload)
            else:
                proc_obj = Procedure(**payload)

            if hasattr(proc_obj, "model_dump"):
                proc_dict = proc_obj.model_dump(exclude_none=True)
            else:
                proc_dict = proc_obj.dict(exclude_none=True)
        else:
            proc_dict = payload

        pid = proc_dict.get("id")
        if pid:
            store.register_id("Procedure", pid)

        resources.append(proc_dict)

    return resources


if __name__ == "__main__":
    class _DummyStore:
        def register_id(self, *_args, **_kwargs):
            return None

    sample = generate(
        None,
        _DummyStore(),
        {"patient_id": "pat-1", "encounter_id": "enc-1"},
        1,
    )
    print(sample[0])
