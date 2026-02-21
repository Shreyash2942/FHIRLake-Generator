from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Coverage",
    bucket="coverages",
    generator="Datasets.FHIRLake_resources.financial.Support.coverage.generate_fhir_coverage:generate",
    dependencies=["Patient"],  # Planning (required)
    optional_dependencies=["Organization"],  # Planning (optional)
    required_inputs=["patient_id"],  # Resolver required inputs
    optional_inputs=["organization_id"],  # Resolver optional inputs
    description="Synthetic Coverage linked to Patient.",
)
