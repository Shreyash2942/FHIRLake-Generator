from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="MedicationRequest",
    bucket="medicationrequests",
    generator="Datasets.FHIRLake_resources.clinical.Medications.MedicationRequest.generate_fhir_medication_request:generate",
    dependencies=["Patient"],  # Planning (required)
    optional_dependencies=["Encounter", "Practitioner", "Organization"],  # Planning (optional)
    required_inputs=["patient_id"],  # Resolver required inputs
    optional_inputs=["encounter_id", "practitioner_id", "organization_id"],  # Resolver optional inputs
    description="Synthetic MedicationRequest linked to Patient.",
)
