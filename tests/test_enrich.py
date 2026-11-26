import pandas as pd
import pytest

from src.data.enrich_data import build_geo_code


def codgeo(dept: str, commune: int) -> str:
    df = pd.DataFrame({"Code departement": [dept], "Code commune": [commune]})
    return build_geo_code(df)["CODGEO"].iloc[0]


@pytest.mark.parametrize(
    ("dept", "commune", "expected"),
    [
        ("44", 109, "44109"),   # Nantes
        ("01", 4, "01004"),     # commune number padded to 3 digits
        ("2A", 4, "2A004"),     # Corsica keeps its letter
    ],
)
def test_metropolitan_codes(dept, commune, expected):
    assert codgeo(dept, commune) == expected


@pytest.mark.parametrize(
    ("dept", "commune", "expected"),
    [
        ("971", 1, "97101"),    # Les Abymes
        ("974", 11, "97411"),   # Saint-Denis (La Réunion)
        ("973", 2, "97302"),    # Cayenne
    ],
)
def test_overseas_codes_stay_five_characters(dept, commune, expected):
    """A 3-character department leaves 2 digits for the commune, not 3."""
    assert codgeo(dept, commune) == expected


@pytest.mark.parametrize(
    ("dept", "commune", "expected"),
    [
        ("75", 101, "75056"),
        ("75", 120, "75056"),
        ("69", 381, "69123"),
        ("69", 389, "69123"),
        ("13", 201, "13055"),
        ("13", 216, "13055"),
    ],
)
def test_arrondissements_fold_into_their_city(dept, commune, expected):
    """INSEE commune-level stats only exist for Paris, Lyon and Marseille as a whole."""
    assert codgeo(dept, commune) == expected


def test_neighbouring_codes_are_not_folded():
    """Only the arrondissement ranges are remapped, not their neighbours."""
    assert codgeo("75", 121) == "75121"
    assert codgeo("69", 380) == "69380"
    assert codgeo("13", 200) == "13200"
