from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Encounter",
    bucket="encounters",
    generator="Datasets.FHIRLake_resources.base.Management.Encounter.generate_fhir_encounter:generate",
    dependencies=["Patient"],              # Planning (required)
    optional_dependencies=["Practitioner"],# Planning (optional)
    required_inputs=["patient_id"],        # Resolver required inputs
    optional_inputs=["practitioner_id"],   # Resolver optional inputs
    description="Synthetic Encounter linked to Patient.",
)
    
