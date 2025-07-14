
from kfp.dsl import component
from typing import NamedTuple

@component(
    base_image="python:3.9"
    packages_to_install=["google-cloud-build==3.20.0", "gcsfs", "fsspec", "pyarrow"]
)
def trigger_cloud_build(
    project_id: str,
    trigger_id: str,
    model_resource_name: str,
    region: str = "us-central1", # Cloud Build API zazwyczaj nie używa regionu dla triggerów
) -> NamedTuple("Outputs", [("build_log_url", str)]):
    """
    Wywołuje trigger Cloud Build za pomocą biblioteki klienckiej Pythona.
    """
    from google.cloud.devtools import cloudbuild_v1
    from google.protobuf.json_format import MessageToDict

    try:
        print("Inicjalizowanie klienta Cloud Build...")
        client = cloudbuild_v1.CloudBuildClient()

        # Definicja podstawień (substitutions), które zostaną przekazane do triggera.
        substitutions = {
            "_MODEL_RESOURCE_NAME": model_resource_name,
        }

        print(f"Przygotowywanie żądania dla triggera: {trigger_id} w projekcie {project_id}")
        
        # Tworzymy obiekt Build, który zawiera nasze podstawienia.
        # To jest kluczowy krok, aby przekazać dynamiczne parametry.
        build = cloudbuild_v1.Build()
        build.substitutions.update(substitutions)

        # Tworzymy żądanie uruchomienia triggera.
        # Przekazujemy obiekt `build` jako szablon do nadpisania.
        request = cloudbuild_v1.RunBuildTriggerRequest(
            project_id=project_id,
            trigger_id=trigger_id,
            source=None,  # Używamy definicji z triggera
        )
        
        # Niestety, RunBuildTriggerRequest nie pozwala na proste nadpisanie `substitutions`.
        # Musimy użyć bardziej złożonej metody `create_build`, pobierając najpierw definicję triggera.
        
        print("Pobieranie definicji triggera...")
        trigger_definition = client.get_build_trigger(project_id=project_id, trigger_id=trigger_id)
        
        # Klonujemy szablon budowania z triggera
        build_template = trigger_definition.build_template
        
        # Łączymy predefiniowane podstawienia z triggera z naszymi nowymi
        merged_substitutions = build_template.substitutions
        merged_substitutions.update(substitutions)
        build_template.substitutions.clear()
        build_template.substitutions.update(merged_substitutions)

        print(f"Uruchamianie budowania z połączonymi podstawieniami: {merged_substitutions}")

        # Tworzymy nowe budowanie na podstawie szablonu z triggera i naszych podstawień
        operation = client.create_build(project_id=project_id, build=build_template)
        
        build_info = operation.metadata.build
        log_url = build_info.log_url

        print(f"Pomyślnie uruchomiono budowanie w Cloud Build. ID: {build_info.id}")
        print(f"URL logów: {log_url}")
        
        return (log_url,)

    except Exception as e:
        print("Wystąpił krytyczny błąd podczas próby uruchomienia triggera Cloud Build.")