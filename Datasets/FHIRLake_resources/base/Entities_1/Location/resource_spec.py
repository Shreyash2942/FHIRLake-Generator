from core.registry.models import ResourceSpec

RESOURCE_SPEC = ResourceSpec(
    resource_type="Location",
    bucket="locations",
    generator="Datasets.FHIRLake_resources.base.Entities_1.Location.generate_fhit_location:generate",
    dependencies=["Organization"],
    required_inputs=["organization_id"],
    description="Synthetic Location resource generator.",
)
