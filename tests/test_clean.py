import pandas as pd
import pytest

from src.data.clean_data import clean_dvf


def row(sale: int, type_local: str | None, surface: float | None, *,
        value: str = "200000,00", nature: str = "Vente", lot: str | None = None,
        plan: int = 1, culture: str = "S") -> dict:
    """One raw DVF line, typed as load_dvf reads it.

    `sale` sets the date, so rows sharing it belong to the same sale.
    `culture` is unused by clean_dvf but kept to mirror the raw file.
    """
    return {
        "No disposition": 1,
        "Date mutation": f"{sale:02d}/01/2025",
        "Nature mutation": nature,
        "Valeur fonciere": value,
        "No voie": 1.0,
        "Type de voie": "RUE",
        "Code voie": "0001",
        "Voie": "DE LA PAIX",
        "Code postal": "44000",
        "Commune": "NANTES",
        "Code departement": "44",
        "Code commune": 109,
        "Section": "AB",
        "No plan": plan,
        "1er lot": lot,
        "Code type local": {"Maison": 1.0, "Appartement": 2.0, "Dépendance": 3.0}.get(type_local, 4.0),
        "Type local": type_local,
        "Surface reelle bati": surface,
        "Nombre pieces principales": 3.0 if type_local in ("Maison", "Appartement") else 0.0,
        "Nature culture": culture,
    }


def clean(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows).drop(columns=["Nature culture"])
    for col in ["Nature mutation", "Type local", "Commune"]:
        df[col] = df[col].astype("category")
    return clean_dvf(df)


def test_house_on_built_land_is_kept():
    """Houses sit on land coded 'S' (sols): the old Nature culture filter dropped 95% of them."""
    out = clean([row(1, "Maison", 100.0, culture="S")])

    assert len(out) == 1
    assert out["prix_m2"].iloc[0] == 2000


def test_unit_repeated_per_land_line_counts_once():
    """A house on a parcel with a garden and built land appears twice in DVF."""
    out = clean([
        row(1, "Maison", 100.0, culture="S"),
        row(1, "Maison", 100.0, culture="J"),
    ])

    assert len(out) == 1
    assert out["prix_m2"].iloc[0] == 2000


def test_outbuilding_does_not_split_the_sale():
    """A flat sold with its cellar keeps the whole price on the flat's surface."""
    out = clean([
        row(1, "Appartement", 50.0, lot="12"),
        row(1, "Dépendance", None, lot="40"),
    ])

    assert len(out) == 1
    assert out["Type local"].iloc[0] == "Appartement"
    assert out["prix_m2"].iloc[0] == 4000


def test_sale_of_several_dwellings_is_dropped():
    """Each row repeats the total value: per-row price/m² would be overstated."""
    out = clean([
        row(1, "Appartement", 50.0, lot="1"),
        row(1, "Appartement", 50.0, lot="2"),
    ])

    assert out.empty


def test_dwelling_sold_with_a_shop_is_dropped():
    out = clean([
        row(1, "Maison", 100.0),
        row(1, "Local industriel. commercial ou assimilé", 80.0, plan=2),
    ])

    assert out.empty


def test_commercial_only_sale_is_dropped():
    assert clean([row(1, "Local industriel. commercial ou assimilé", 80.0)]).empty


@pytest.mark.parametrize("nature", [
    "Echange", "Adjudication", "Expropriation", "Vente en l'état futur d'achèvement",
])
def test_non_market_sales_are_dropped(nature):
    assert clean([row(1, "Maison", 100.0, nature=nature)]).empty


def test_separate_sales_stay_separate():
    """Same dwelling type, different dates: two sales, two rows."""
    out = clean([
        row(1, "Appartement", 50.0, lot="1"),
        row(2, "Appartement", 50.0, lot="1"),
    ])

    assert len(out) == 2


def test_helper_columns_do_not_leak():
    out = clean([row(1, "Maison", 100.0)])

    assert "No disposition" not in out.columns
    assert "1er lot" not in out.columns
