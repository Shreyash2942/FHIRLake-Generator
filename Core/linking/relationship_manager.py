from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional

from Core.runtime import RunContext, ResourceStore
from .policies import LinkingPolicy, MissingDependencyAction


JsonDict = Dict[str, Any]

# Generator signatures you already follow:
GenerateEncounterFn = Callable[[str], Any]                 # generate_encounter(patient_id) -> model
GenerateConditionFn = Callable[[str, str], Any]            # generate_condition(patient_id, encounter_id) -> model


@dataclass
class RelationshipManager:
    """
    Centralized relationship manager.

    Responsibilities:
    - Select related IDs (pick encounter for patient)
    - Ensure required parents exist (AUTO_CREATE)
    - Register relationship indexes in ResourceStore
    """
    ctx: RunContext
    store: ResourceStore
    policy: LinkingPolicy = LinkingPolicy()

    def pick_or_ensure_encounter_id(
        self,
        patient_id: str,
        generate_encounter: GenerateEncounterFn,
        to_json: Callable[[Any], JsonDict],
    ) -> str:
        """
        Pick an existing encounter for the patient.
        If none exist, apply policy:
          - AUTO_CREATE: create one
          - ERROR: raise
          - FALLBACK: (later) allow missing + store fallback metadata
        """
        encounter_ids = self.store.get_patient_encounters(patient_id)
        if encounter_ids:
            return self.ctx.rng.choice(encounter_ids)

        action: MissingDependencyAction = self.policy.encounter_required_for_condition
        if action == "AUTO_CREATE":
            enc_model = generate_encounter(patient_id)
            enc_json = to_json(enc_model)

            enc_id = enc_json["id"]
            self.store.add("encounters", enc_json)
            self.store.link_patient_encounter(patient_id, enc_id)
            return enc_id

        if action == "ERROR":
            raise ValueError(
                f"Missing Encounter for Patient/{patient_id}. "
                f"Policy=ERROR. Generate encounters first or change policy."
            )

        # FALLBACK placeholder (we'll implement contract-preserving fallback later)
        # For now, behave like ERROR so we never create broken references.
        raise ValueError(
            f"Missing Encounter for Patient/{patient_id}. Policy=FALLBACK not implemented yet."
        )

    def register_condition_links(self, patient_id: str, encounter_id: str, condition_id: str) -> None:
        """Register condition relationship indexes."""
        self.store.link_patient_condition(patient_id, condition_id)
        self.store.link_encounter_condition(encounter_id, condition_id)
