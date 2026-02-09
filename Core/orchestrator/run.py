# Core/orchestrator/run.py
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Set, List

from Core.runtime import RunContext, ResourceStore

# ✅ Planning + Linking (new scalable flow)
from Core.planning import UserRequest, build_plan, PlanningError
from Core.linking import RelationshipManager, LinkingPolicy

# Import your existing generators (keep them unchanged)
from Datasets.FHIRLake_resources.base.Individuals.Patient.generate_fhir_patient import generate_patient
from Datasets.FHIRLake_resources.base.Management.Encounter.generate_fhir_encounter import generate_encounter
from Datasets.FHIRLake_resources.clinical.Summary.Condition.generate_fhir_condition import generate_condition


JsonDict = Dict[str, Any]


def _to_json_dict(resource_model: Any) -> JsonDict:
    """
    Convert a fhir.resources pydantic model into a plain JSON dict.
    """
    return json.loads(resource_model.model_dump_json(exclude_none=True))


@dataclass(frozen=True)
class GenerationPlan:
    """
    Legacy/simple plan for v1 fixed generation (kept for backward compatibility).

    - num_patients: number of patients to generate
    - encounters_per_patient: fixed number of encounters per patient (e.g., 3)
    - conditions_per_patient: fixed number of conditions per patient (e.g., 2)

    Note: In v2 we use UserRequest -> build_plan() -> execute.
    """
    num_patients: int
    encounters_per_patient: int
    conditions_per_patient: int


def run_patient_encounter_condition_job(
    plan: GenerationPlan,
    ctx: Optional[RunContext] = None,
) -> Tuple[ResourceStore, Dict[str, Any]]:
    """
    CORE orchestrator v1 (no globals) — legacy function.

    Generates:
      - Patient
      - Encounter (linked to Patient)
      - Condition (linked to Patient + one of the Patient's Encounters)

    Returns:
      (store, summary)
    """
    if plan.num_patients <= 0:
        raise ValueError("num_patients must be > 0")
    if plan.encounters_per_patient < 0:
        raise ValueError("encounters_per_patient must be >= 0")
    if plan.conditions_per_patient < 0:
        raise ValueError("conditions_per_patient must be >= 0")

    ctx = ctx or RunContext()
    store = ResourceStore()

    for _ in range(plan.num_patients):
        # ----------------------------
        # 1) Patient
        # ----------------------------
        patient_model = generate_patient()
        patient_json = _to_json_dict(patient_model)
        patient_id = patient_json["id"]

        store.add("patients", patient_json)

        # ----------------------------
        # 2) Encounters (linked to patient)
        # ----------------------------
        encounter_ids: List[str] = []
        for _ in range(plan.encounters_per_patient):
            encounter_model = generate_encounter(patient_id)
            encounter_json = _to_json_dict(encounter_model)
            encounter_id = encounter_json["id"]

            encounter_ids.append(encounter_id)
            store.add("encounters", encounter_json)
            store.link_patient_encounter(patient_id, encounter_id)

        # ----------------------------
        # 3) Conditions (linked to patient + one encounter)
        # ----------------------------
        for _ in range(plan.conditions_per_patient):
            # Avoid broken references: if no encounter exists, create one.
            if not encounter_ids:
                encounter_model = generate_encounter(patient_id)
                encounter_json = _to_json_dict(encounter_model)
                encounter_id = encounter_json["id"]

                store.add("encounters", encounter_json)
                store.link_patient_encounter(patient_id, encounter_id)
                encounter_ids.append(encounter_id)

            selected_encounter_id = ctx.rng.choice(encounter_ids)

            condition_model = generate_condition(patient_id, selected_encounter_id)
            condition_json = _to_json_dict(condition_model)
            condition_id = condition_json["id"]

            store.add("conditions", condition_json)
            store.link_patient_condition(patient_id, condition_id)
            store.link_encounter_condition(selected_encounter_id, condition_id)

    summary: Dict[str, Any] = {
        "run_id": ctx.run_id,
        "timestamp_utc": ctx.timestamp_utc,
        "seed": ctx.seed,
        "counts": store.counts(),
        "mode": "legacy_v1",
    }

    return store, summary


# -------------------------------------------------------------------
# ✅ v2 Orchestrator: UserRequest -> Planning -> Linking -> Execution
# -------------------------------------------------------------------
def run_from_user_request(
    req: UserRequest,
    linking_policy: Optional[LinkingPolicy] = None,
) -> Tuple[ResourceStore, Dict[str, Any]]:
    """
    CORE orchestrator v2 (scalable).

    Flow:
      1) UserRequest (CLI/GUI selection)
      2) build_plan(req) expands dependencies + ordering + validates params
      3) RelationshipManager applies linking rules safely (no broken refs)
      4) Execute generation based on expanded plan

    Returns:
      (store, summary)
    """
    try:
        plan = build_plan(req)
    except PlanningError as e:
        raise ValueError(f"Planning failed: {e}") from e

    # Create run context using planned seed
    ctx = RunContext(seed=plan.seed)
    store = ResourceStore()

    rm = RelationshipManager(
        ctx=ctx,
        store=store,
        policy=linking_policy or LinkingPolicy(),
    )

    expanded: Set[str] = set(plan.expanded)

    # v2 currently uses Patient as the dataset driver (root)
    if "Patient" not in expanded:
        raise ValueError(
            "Invalid plan: Patient must be present. "
            "For now, v2 requires Patient as the dataset root driver."
        )

    num_patients = plan.run_params["num_patients"]
    encounters_per_patient = plan.run_params["encounters_per_patient"]
    conditions_per_patient = plan.run_params["conditions_per_patient"]

    for _ in range(num_patients):
        # ----------------------------
        # 1) Patient (always required in current driver model)
        # ----------------------------
        patient_model = generate_patient()
        patient_json = _to_json_dict(patient_model)
        patient_id = patient_json["id"]
        store.add("patients", patient_json)

        # ----------------------------
        # 2) Encounter (only if in expanded plan)
        # ----------------------------
        if "Encounter" in expanded:
            for _ in range(encounters_per_patient):
                enc_model = generate_encounter(patient_id)
                enc_json = _to_json_dict(enc_model)
                enc_id = enc_json["id"]

                store.add("encounters", enc_json)
                store.link_patient_encounter(patient_id, enc_id)

        # ----------------------------
        # 3) Condition (only if in expanded plan)
        # ----------------------------
        if "Condition" in expanded:
            for _ in range(conditions_per_patient):
                # Linking layer decides how to pick/ensure encounter
                enc_id = rm.pick_or_ensure_encounter_id(
                    patient_id=patient_id,
                    generate_encounter=generate_encounter,
                    to_json=_to_json_dict,
                )

                cond_model = generate_condition(patient_id, enc_id)
                cond_json = _to_json_dict(cond_model)
                cond_id = cond_json["id"]

                store.add("conditions", cond_json)
                rm.register_condition_links(patient_id, enc_id, cond_id)

    summary: Dict[str, Any] = {
        "run_id": ctx.run_id,
        "timestamp_utc": ctx.timestamp_utc,
        "seed": ctx.seed,
        "requested": plan.requested,
        "expanded": plan.expanded,
        "ordered": plan.ordered,
        "counts": store.counts(),
        "mode": "planned_v2",
    }

    return store, summary
