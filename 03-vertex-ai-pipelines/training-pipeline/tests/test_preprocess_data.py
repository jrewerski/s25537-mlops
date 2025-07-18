import pytest
import pandas as pd
from kfp.dsl import Dataset
from pathlib import Path
import os

# Dzięki plikowi conftest.py, ten import zadziała poprawnie,
# ponieważ katalog 'training-pipeline' został dodany do ścieżki systemowej.
from components.preprocess_data import preprocess_data

@pytest.fixture
def temp_dir(tmp_path):
    """Tworzy tymczasowe katalogi dla artefaktów wejściowych i wyjściowych."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    return input_dir, output_dir

@pytest.fixture
def sample_input_data(temp_dir):
    """Tworzy przykładowe dane wejściowe i zapisuje je do pliku CSV."""
    input_dir, _ = temp_dir
    data = {
        'species': ['Adelie', 'Adelie', 'Gentoo', 'Chinstrap'],
        'island': ['Torgersen', 'Biscoe', 'Biscoe', 'Dream'],
        'culmen_length_mm': [39.1, 40.3, 46.1, 50.0],
        'culmen_depth_mm': [18.7, 18.0, 13.2, 16.4],
        'flipper_length_mm': [181.0, 195.0, 211.0, None], # Brakująca wartość
        'body_mass_g': [3750.0, 3250.0, None, 3700.0], # Brakująca wartość
        'sex': ['MALE', 'FEMALE', 'FEMALE', None] # Brakująca wartość
    }
    df = pd.DataFrame(data)
    input_path = input_dir / "data.csv"
    df.to_csv(input_path, index=False)
    return str(input_path)

def test_preprocess_data_logic(temp_dir, sample_input_data):
    """
    Testuje logikę komponentu preprocess_data.
    Sprawdza, czy brakujące wartości są poprawnie uzupełniane
    i czy dane są prawidłowo kodowane.
    """
    input_dir, output_dir = temp_dir
    
    # POPRAWKA: Usunięto argument `path` z konstruktorów Dataset.
    # W nowszych wersjach KFP, atrybut .path jest automatycznie
    # zarządzany na podstawie .uri.
    input_dataset = Dataset(uri=sample_input_data)
    
    train_output_path = output_dir / "train.csv"
    test_output_path = output_dir / "test.csv"
    train_dataset = Dataset(uri=str(train_output_path))
    test_dataset = Dataset(uri=str(test_output_path))

    # Wywołanie funkcji komponentu
    preprocess_data.python_func(
        input_data=input_dataset,
        train_dataset=train_dataset,
        test_dataset=test_dataset,
        test_split_ratio=0.5
    )

    # Sprawdzenie wyników - odczytujemy pliki z atrybutu .path artefaktów wyjściowych
    assert os.path.exists(train_dataset.path)
    assert os.path.exists(test_dataset.path)

    train_df = pd.read_csv(train_dataset.path)
    test_df = pd.read_csv(test_dataset.path)
    
    combined_df = pd.concat([train_df, test_df])

    assert combined_df.isnull().sum().sum() == 0, "Powinny zostać uzupełnione wszystkie brakujące wartości"
    assert combined_df['sex'].dtype in ['int64', 'float64'], "Kolumna 'sex' powinna być numeryczna"
    assert 'island_Torgersen' in combined_df.columns
    assert 'island_Dream' in combined_df.columns
    assert 'island' not in combined_df.columns, "Oryginalna kolumna 'island' powinna zostać usunięta"
    assert len(train_df) > 0
    assert len(test_df) > 0
    assert len(combined_df) == 4
