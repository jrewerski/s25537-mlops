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
import logging

from components.get_data import get_data
from components.preprocess_data import preprocess_data
from components.train_svc_model import train_svc_model
from components.evaluate_svc_model import evaluate_svc_model
from components.register_model import register_model



# --- Definicja głównego potoku Vertex AI ---
@pipeline(
    name="penguin-svc-classification-with-registry",
    description="Potok trenujący i rejestrujący model SVC.",
    pipeline_root="gs://vertex-ai-bucket-s25537",
)
def penguin_pipeline(
    gcs_data_path: str = "gs://data-s25537/penguins.csv",
    project_id: str = "mlops-on-gcp-s25537",
    region: str = "us-central1",
    model_name: str = "puffin",
    test_split_ratio: float = 0.3,
    min_accuracy_threshold: float = 95.0,
):
    """Definiuje przepływ pracy w potoku z warunkową rejestracją."""
    get_data_task = get_data(gcs_input_path=gcs_data_path)
    
    transform_data_task = preprocess_data(
        input_data=get_data_task.outputs["input_data"],
        test_split_ratio=test_split_ratio
    )
    
    train_task = train_svc_model(
        train_dataset=transform_data_task.outputs["train_dataset"]
    )
    
    evaluate_task = evaluate_svc_model(
        test_dataset=transform_data_task.outputs["test_dataset"],
        model=train_task.outputs["model"],
    )

    # Warunek: zarejestruj model tylko, jeśli dokładność jest wystarczająco wysoka
    with dsl.If(
        evaluate_task.outputs["accuracy"] >= min_accuracy_threshold,
        name="accuracy-check",
    ):
        register_model(
            project_id=project_id,
            region=region,
            model_display_name=model_name,
            model=train_task.outputs["model"],
        )

if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=penguin_pipeline,
        package_path="penguin_svc_pipeline_with_registry2.json",
    )

    aiplatform.init(project="mlops-on-gcp-s25537", location='us-central1')

    job = aiplatform.PipelineJob(
            display_name="penguin-svc-with-registry-run",
            template_path="penguin_svc_pipeline_with_registry2.json",
            pipeline_root="gs://vertex-ai-bucket-s25537",
            enable_caching=True,
        )

    print("Uruchamianie potoku w Vertex AI...")
    job.run()