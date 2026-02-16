from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Condition",
    bucket="conditions",
    generator="Datasets.FHIRLake_resources.clinical.Summary.Condition.generate_fhir_condition:generate",
    dependencies=["Patient", "Encounter"],         # Planning (required)
    optional_dependencies=["Practitioner"],        # Planning (optional)
    dependency_policy="AUTO_CREATE",               # Resolver / Orchestrator
    required_inputs=["patient_id", "encounter_id"], # Resolver required inputs
    optional_inputs=["practitioner_id"],           # Resolver optional inputs
    description="Synthetic Condition linked to Patient and Encounter.",
)
