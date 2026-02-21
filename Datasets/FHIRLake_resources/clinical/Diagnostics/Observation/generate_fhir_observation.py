"""
FHIRLake Generator - Observation Resource Generator

Generates synthetic FHIR Observation resources using:
- fhir.resources (pydantic FHIR models)
- Faker

Notes:
- Only one value[x] is set at a time.
- dataAbsentReason is only set when value[x] is missing.
- If component is present, Observation.value[x] is omitted.
- If organizer is true, value[x], dataAbsentReason, and component are omitted.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from faker import Faker

from fhir.resources.observation import Observation
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference


fake = Faker()


def _uuid() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_identifier(system: str, value: str, use: str = "usual") -> Identifier:
    return Identifier.model_validate({
        "system": system,
        "value": value,
        "use": use,
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


def make_reference(ref: str) -> Reference:
    return Reference.model_validate({"reference": ref})


def _random_observation_code() -> CodeableConcept:
    pool = [
        ("718-7", "Hemoglobin"),
        ("8462-4", "Diastolic blood pressure"),
        ("8480-6", "Systolic blood pressure"),
        ("8867-4", "Heart rate"),
        ("8310-5", "Body temperature"),
        ("8302-2", "Body height"),
        ("29463-7", "Body weight"),
    ]
    code, display = random.choice(pool)
    return make_codeable_concept(
        [make_coding("http://loinc.org", code, display)],
        text=display,
    )


def _random_value_choice(code_display: str) -> Dict[str, Any]:
    choice = random.choice(["quantity", "string", "boolean", "integer", "codeable"])

    if choice == "quantity":
        unit_pool = [
            ("mm[Hg]", "mmHg"),
            ("bpm", "beats/min"),
            ("degF", "F"),
            ("kg", "kg"),
            ("cm", "cm"),
        ]
        unit_code, unit_display = random.choice(unit_pool)
        qty = Quantity.model_validate({
            "value": round(random.uniform(50, 180), 1),
            "unit": unit_display,
            "system": "http://unitsofmeasure.org",
            "code": unit_code,
        })
        return {"valueQuantity": qty.model_dump(exclude_none=True)}

    if choice == "string":
        return {"valueString": f"{code_display} measured"}

    if choice == "boolean":
        return {"valueBoolean": random.choice([True, False])}

    if choice == "integer":
        return {"valueInteger": random.randint(1, 10)}

    code = make_codeable_concept(
        [make_coding("https://fhirlake.dev/codes/observation-result", "normal", "Normal")],
        text="Normal",
    )
    return {"valueCodeableConcept": code.model_dump(exclude_none=True)}


def _random_component() -> Dict[str, Any]:
    code = make_codeable_concept(
        [make_coding("http://loinc.org", "2951-2", "Sodium" )],
        text="Sodium",
    )
    value = Quantity.model_validate({
        "value": round(random.uniform(130, 150), 1),
        "unit": "mmol/L",
        "system": "http://unitsofmeasure.org",
        "code": "mmol/L",
    })

    return {
        "code": code.model_dump(exclude_none=True),
        "valueQuantity": value.model_dump(exclude_none=True),
    }


def generate(ctx, store, inputs: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
    resources: List[Dict[str, Any]] = []

    patient_id = inputs.get("patient_id")
    encounter_id = inputs.get("encounter_id")
    practitioner_id = inputs.get("practitioner_id")

    if not patient_id:
        raise ValueError(
            "Observation generator requires inputs['patient_id']."
        )
    if not encounter_id:
        raise ValueError(
            "Observation generator requires inputs['encounter_id']."
        )

    for _ in range(int(count)):
        obs_id = _uuid()
        code_cc = _random_observation_code()
        status = random.choice([
            "registered",
            "preliminary",
            "final",
            "amended",
        ])

        payload: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": obs_id,
            "identifier": [
                make_identifier("MetricCare-Observation", f"OBS-{fake.unique.random_int(100000, 999999)}").model_dump(exclude_none=True)
            ],
            "status": status,
            "code": code_cc.model_dump(exclude_none=True),
            "subject": make_reference(f"Patient/{patient_id}").model_dump(exclude_none=True),
            "encounter": make_reference(f"Encounter/{encounter_id}").model_dump(exclude_none=True),
            "effectiveDateTime": _now_iso(),
            "issued": _now_iso(),
        }

        if practitioner_id:
            payload["performer"] = [
                make_reference(f"Practitioner/{practitioner_id}").model_dump(exclude_none=True)
            ]

        # organizer rules (not a native field in some fhir.resources versions)
        organizer = random.random() < 0.05
        if organizer:
            payload["extension"] = [{
                "url": "https://fhirlake.dev/unsupported/organizer",
                "valueBoolean": True,
            }]

        # optional category
        if random.random() < 0.6:
            category = make_codeable_concept(
                [make_coding("http://terminology.hl7.org/CodeSystem/observation-category", "vital-signs", "Vital Signs")],
                text="Vital Signs",
            )
            payload["category"] = [category.model_dump(exclude_none=True)]

        if not organizer:
            add_component = random.random() < 0.25
            if add_component:
                payload["component"] = [_random_component()]
            else:
                payload.update(_random_value_choice(code_cc.text or "Observation"))

            if "value" not in "".join(payload.keys()) and random.random() < 0.2:
                data_absent = make_codeable_concept(
                    [make_coding("http://terminology.hl7.org/CodeSystem/data-absent-reason", "unknown", "Unknown")],
                    text="Unknown",
                )
                payload["dataAbsentReason"] = data_absent.model_dump(exclude_none=True)

        obs_obj = Observation.model_validate(payload)
        obs_dict = obs_obj.model_dump(exclude_none=True)

        obs_id_final = obs_dict.get("id")
        if obs_id_final:
            store.register_id("Observation", obs_id_final)

        resources.append(obs_dict)

    return resources


if __name__ == "__main__":
    class _DummyStore:
        def register_id(self, *_args, **_kwargs):
            return None

    data = generate(None, _DummyStore(), {"patient_id": "pat-1", "encounter_id": "enc-1"}, 2)
    for item in data:
        print(item)
