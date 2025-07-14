import subprocess
import sys
from kfp.dsl import component

@component(
    # Używamy tego samego obrazu, aby przetestować go do granic możliwości
    base_image="google/cloud-sdk:slim",
)
def trigger_cloud_build(
    project_id: str,
    trigger_id: str,
    model_resource_name: str,
    region: str = "global",
):
    """
    ULTRA-PROSTA WERSJA DIAGNOSTYCZNA.
    Sprawdza, czy w ogóle można uruchomić jakiekolwiek polecenie systemowe.
    """
    print("--- ROZPOCZYNAM TEST ŚRODOWISKA ---")
    
    try:
        print("\n--- TEST 1: Sprawdzanie bieżącego katalogu (pwd) ---")
        # Używamy check=True, aby komponent zakończył się błędem, jeśli polecenie zawiedzie
        subprocess.run(["pwd"], check=True, capture_output=True, text=True)
        print("Test 1 ZAKOŃCZONY SUKCESEM.")

        print("\n--- TEST 2: Listowanie zawartości katalogu głównego (ls -la /) ---")
        subprocess.run(["ls", "-la", "/"], check=True, capture_output=True, text=True)
        print("Test 2 ZAKOŃCZONY SUKCESEM.")
        
        print("\n--- TEST 3: Listowanie zawartości bieżącego katalogu (ls -la .) ---")
        subprocess.run(["ls", "-la", "."], check=True, capture_output=True, text=True)
        print("Test 3 ZAKOŃCZONY SUKCESEM.")

        print("\n--- TEST ŚRODOWISKA ZAKOŃCZONY SUKCESEM ---")
        
        # Celowo powodujemy błąd, aby zatrzymać potok tutaj i nie iść dalej.
        # Chcemy tylko zobaczyć logi z powyższych testów.
        print("\nCelowe zatrzymanie potoku, aby sprawdzić logi. To nie jest prawdziwy błąd.")
        sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"\n--- KRYTYCZNY BŁĄD PODCZAS TESTU ŚRODOWISKA ---")
        print(f"Polecenie: {e.cmd}")
        print(f"Kod wyjścia: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"\n--- KRYTYCZNY BŁĄD OGÓLNY ---")
        print(e)
        sys.exit(1)
