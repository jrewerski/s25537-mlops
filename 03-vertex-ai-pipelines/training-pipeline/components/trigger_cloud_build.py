from kfp.dsl import component

@component(
    # Używamy oficjalnego obrazu z Google Cloud SDK, który zawiera gcloud
    base_image="google/cloud-sdk:slim",
)
def trigger_cloud_build(
    project_id: str,
    trigger_id: str,
    model_resource_name: str,
    region: str
):
    """
    Wywołuje trigger Cloud Build za pomocą polecenia gcloud.
    """
    import subprocess
    import sys

    # Budujemy polecenie gcloud
    cmd = [
        "gcloud", "builds", "triggers", "run", trigger_id,
        f"--project={project_id}",
        f"--region={region}",
        f"--substitutions=_MODEL_RESOURCE_NAME={model_resource_name}"
    ]
    
    print(f"Uruchamiam polecenie: {' '.join(cmd)}")

    # Uruchamiamy proces i przechwytujemy jego wyjście
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    # Drukujemy logi z gcloud, co jest bardzo pomocne przy debugowaniu
    print("--- gcloud stdout ---")
    print(process.stdout)
    
    if process.stderr:
        print("--- gcloud stderr ---")
        print(process.stderr)
    
    # Sprawdzamy, czy polecenie zakończyło się sukcesem
    if process.returncode != 0:
        print("Błąd podczas uruchamiania triggera Cloud Build.", file=sys.stderr)
        sys.exit(process.returncode)
