from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Patient",
    bucket="patients",
    generator="Datasets.FHIRLake_resources.base.Individuals.Patient.generate_fhir_patient:generate",
    dependencies=[],
    required_inputs=[],
    description="Synthetic Patient resource generator.",
)
