from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Organization",
    bucket="organizations",
    generator="Datasets.FHIRLake_resources.base.Entities_1.Organization.generate_fhir_organization:generate",
    dependencies=[],
    required_inputs=[],
    description="Synthetic Organization resource generator.",
)
