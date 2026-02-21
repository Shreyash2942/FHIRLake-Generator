from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Observation",
    bucket="observations",
    generator="Datasets.FHIRLake_resources.clinical.Diagnostics.Observation.generate_fhir_observation:generate",
    dependencies=["Patient", "Encounter"],      # Planning (required)
    optional_dependencies=["Practitioner"],     # Planning (optional)
    dependency_policy="AUTO_CREATE",            # Resolver / Orchestrator
    required_inputs=["patient_id", "encounter_id"],
    optional_inputs=["practitioner_id"],
    description="Synthetic Observation linked to Patient and Encounter.",
)
