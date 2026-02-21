from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Claim",
    bucket="claims",
    generator="Datasets.FHIRLake_resources.financial.Billing.claim.generate_fhir_claim:generate",
    dependencies=["Patient"],  # Planning (required)
    optional_dependencies=["Encounter", "Practitioner", "Organization"],  # Planning (optional)
    required_inputs=["patient_id"],  # Resolver required inputs
    optional_inputs=["encounter_id", "practitioner_id", "organization_id"],  # Resolver optional inputs
    description="Synthetic Claim linked to Patient.",
)
