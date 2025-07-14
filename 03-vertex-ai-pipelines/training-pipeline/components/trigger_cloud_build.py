from kfp.dsl import component

@component(
    base_image="python:3.9",
    packages_to_install=["google-cloud-build==3.20.0"],
)
def trigger_cloud_build(
    project_id: str,
    trigger_id: str,
    model_resource_name: str,
) -> str:
    """
    Wywołuje trigger Cloud Build i przekazuje ID modelu jako podstawienie.
    """
    from google.cloud.devtools import cloudbuild_v1
    
    client = cloudbuild_v1.CloudBuildClient()
    
    # Definicja podstawień (substitutions) dla triggera
    # Zostaną one scalone z podstawieniami zdefiniowanymi w triggerze.
    substitutions = {
        "_MODEL_RESOURCE_NAME": model_resource_name,
    }
    
    request = cloudbuild_v1.RunBuildTriggerRequest(
        project_id=project_id,
        trigger_id=trigger_id,
        source=None,  
        substitutions=substitutions
    )

    operation = client.run_build_trigger(request=request)
    build_info = operation.metadata.build
    
    print(f"Pomyślnie uruchomiono Cloud Build. ID budowania: {build_info.id}")
    print(f"URL logów: {build_info.log_url}")
    
    return build_info.log_url