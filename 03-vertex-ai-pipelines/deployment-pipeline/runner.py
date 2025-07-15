import os
import kfp
from kfp import dsl
from kfp.dsl import (Artifact,
                        Dataset,
                        Input,
                        InputPath,
                        Model,
                        Output,
                        OutputPath,
                        component,
                        Metrics,
                        pipeline)
from kfp import compiler
from google.cloud import aiplatform
from typing import NamedTuple
from google_cloud_pipeline_components.v1.model import ModelGetOp
from google_cloud_pipeline_components.v1.endpoint import EndpointCreateOp, ModelDeployOp



@pipeline(
    name="deployment-pipeline",
    description="Potok tworzy endpoint i wdraża na nim podany model",
    pipeline_root="gs://vertex-ai-bucket-s25537/deployment-pipeline",
)
def deployment_pipeline(
    endpoint_name: str,
    model_resource_name: str,
    project_id: str = "mlops-on-gcp-s25537",
    region: str = "us-central1",
):
    """Tworzy endpoint i wdraża na nim podany model."""

    endpoint_create = EndpointCreateOp(
        project = project_id,
        display_name = endpoint_name
    )
    
    get_model_op = ModelGetOp(
        model_name=model_resource_name,
        location = region,
    )

    model_deploy = ModelDeployOp(
        model=get_model_op.outputs["model"],
        endpoint = endpoint_create.outputs["endpoint"],
        deployed_model_display_name = "Predict-Puffin", 
        dedicated_resources_machine_type="n1-standard-2",
        dedicated_resources_min_replica_count=1,
        dedicated_resources_max_replica_count=1
    )


if __name__ == '__main__':
    print("Kompilacja potoku")
    compiler.Compiler().compile(
        pipeline_func=deployment_pipeline,
        package_path="pipeline.json",
    )
