import subprocess
import sys
from kfp.dsl import component

@component(
    # --- KLUCZOWA ZMIANA ---
    # Zmieniamy obraz na jego starszą, stabilną wersję, która nie ma problemu
    # z "externally-managed-environment".
    base_image="google/cloud-sdk:slim",
)
def trigger_cloud_build(
    project_id: str,
    trigger_id: str,
    model_resource_name: str,
    region: str = "global",
):
    """
    Wywołuje trigger Cloud Build z dodatkowymi krokami diagnostycznymi.
    """
    
    def run_command(cmd_args):
        """Funkcja pomocnicza do uruchamiania poleceń i drukowania ich wyjścia."""
        print(f"\n--- Uruchamiam polecenie: {' '.join(cmd_args)} ---")
        process = subprocess.run(cmd_args, capture_output=True, text=True)
        
        if process.stdout:
            print("--- stdout ---")
            print(process.stdout)
        
        if process.stderr:
            print("--- stderr ---")
            print(process.stderr)
        
        if process.returncode == 0:
            print("Polecenie zakończone sukcesem.")
        else:
            print(f"BŁĄD: Polecenie zakończone z kodem wyjścia {process.returncode}")
            
        return process

    # --- Krok 1: Sprawdzenie, czy gcloud jest dostępne ---
    print("--- KROK DIAGNOSTYCZNY 1: Sprawdzanie wersji gcloud ---")
    version_check = run_command(["gcloud", "--version"])
    if version_check.returncode != 0:
        print("Krytyczny błąd: Nie można uruchomić 'gcloud --version'.")
        sys.exit(version_check.returncode)

    # --- Krok 2: Sprawdzenie, na jakim koncie serwisowym działa komponent ---
    print("\n--- KROK DIAGNOSTYCZNY 2: Sprawdzanie uwierzytelnienia ---")
    auth_check = run_command(["gcloud", "auth", "list"])
    if auth_check.returncode != 0:
        print("Krytyczny błąd: Nie można sprawdzić uwierzytelnienia 'gcloud auth list'.")
        sys.exit(auth_check.returncode)

    # --- Krok 3: Próba uruchomienia triggera ---
    print("\n--- KROK GŁÓWNY 3: Uruchamianie triggera Cloud Build ---")
    trigger_cmd = [
        "gcloud", "builds", "triggers", "run", trigger_id,
        f"--project={project_id}",
        f"--region={region}",
        f"--substitutions=_MODEL_RESOURCE_NAME={model_resource_name}"
    ]
    trigger_run = run_command(trigger_cmd)
    
    # Zakończ z kodem błędu, jeśli ostatnie polecenie zawiodło
    if trigger_run.returncode != 0:
        print("\nFinalne polecenie uruchomienia triggera nie powiodło się.")
        sys.exit(trigger_run.returncode)

