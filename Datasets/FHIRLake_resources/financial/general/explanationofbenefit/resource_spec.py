from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="ExplanationOfBenefit",
    bucket="explanation_of_benefits",
    generator=(
        "Datasets.FHIRLake_resources.financial.general.explanationofbenefit."
        "generate_fhir_explanationofbenefit:generate"
    ),
    dependencies=["Patient"],  # Planning (required)
    optional_dependencies=[
        "Claim",
        "Coverage",
        "Encounter",
        "Practitioner",
        "Organization",
        "Procedure",
        "MedicationRequest",
    ],  # Planning (optional)
    required_inputs=["patient_id"],  # Resolver required inputs
    optional_inputs=[
        "claim_id",
        "coverage_id",
        "encounter_id",
        "practitioner_id",
        "organization_id",
        "procedure_id",
        "medication_request_id",
    ],  # Resolver optional inputs
    description="Synthetic ExplanationOfBenefit linked to Patient.",
)
