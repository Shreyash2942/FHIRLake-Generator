from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Practitioner",
    bucket="practitioners",
    generator="Datasets.FHIRLake_resources.base.Individuals.Practitioner.generate_fhir_practitoner:generate",
    dependencies=[],
    required_inputs=[],
    description="Synthetic Practitioner resource generator.",
)
