from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Procedure",
    bucket="procedures",
    generator="Datasets.FHIRLake_resources.clinical.Summary.Procedure.generate_fhir_procedure:generate",
    dependencies=["Patient", "Encounter"],          # Planning (required)
    optional_dependencies=["Practitioner", "Organization"],  # Planning (optional)
    required_inputs=["patient_id", "encounter_id"],  # Resolver required inputs
    optional_inputs=["practitioner_id", "organization_id"],  # Resolver optional inputs
    description="Synthetic Procedure linked to Patient and Encounter.",
)
