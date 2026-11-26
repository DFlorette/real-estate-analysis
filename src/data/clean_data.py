import numpy as np
import pandas as pd

HOUSING_TYPES = ["Maison", "Appartement"]

# DVF has no usable sale identifier: these columns together identify one sale.
MUTATION_KEY = [
    "Date mutation", "Nature mutation", "Valeur fonciere",
    "Code departement", "Code commune", "No disposition",
]

# A built unit is repeated once per land-use line of its parcel.
UNIT_KEY = MUTATION_KEY + [
    "Section", "No plan", "1er lot",
    "Code type local", "Surface reelle bati", "Nombre pieces principales",
]


def keep_single_housing_sales(df: pd.DataFrame) -> pd.DataFrame:
    """One row per sale of exactly one house or flat.

    DVF has one row per unit and per land-use line, and every row repeats the
    total value of the sale. Dividing that value by the surface of one row
    overstates the price of any sale bundling several units. Units are first
    deduplicated, then a sale is kept only if it holds a single dwelling:
    outbuildings (Dépendance) carry no living area and are allowed, while sales
    of several dwellings or of a dwelling with a commercial unit are dropped,
    since their value cannot be split between units.
    """
    units = df[df["Type local"].notna()].drop_duplicates(UNIT_KEY)

    is_housing = units["Type local"].isin(HOUSING_TYPES)
    is_other = ~is_housing & (units["Type local"] != "Dépendance")

    sale_id = units.groupby(MUTATION_KEY, dropna=False, observed=True, sort=False).ngroup()
    counts = (
        pd.DataFrame({"housing": is_housing, "other": is_other})
        .groupby(sale_id)
        .transform("sum")
    )

    return units[is_housing & (counts["housing"] == 1) & (counts["other"] == 0)]


def clean_dvf(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    ##
    # PARSING
    ##
    # Category
    for col in ["Nature mutation", "Commune", "Type local"]:
        df = clean_str_col(df, col, to_category=True)

    # Number
    df["Valeur fonciere"] = pd.to_numeric(
        df["Valeur fonciere"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )

    # Str
    for col in ["Type de voie", "Code voie", "Voie", "Code postal",
                "Code departement", "Section", "1er lot"]:
        if col in df.columns:
            df = clean_str_col(df, col)

    # Date
    df["Date mutation"] = pd.to_datetime(df["Date mutation"], format="%d/%m/%Y")

    ##
    # FILTER : market sales of a single dwelling
    ##
    # Exchanges, auctions, expropriations and off-plan sales (VEFA) do not
    # follow open-market prices.
    df = df[df["Nature mutation"] == "Vente"]
    df = df.dropna(subset=["Valeur fonciere"])

    df = keep_single_housing_sales(df)
    df = df.drop(columns=["No disposition", "1er lot"], errors="ignore")

    ##
    # HANDLE MISSING / CRITICAL VALUES
    ##
    df = df.dropna(subset=["Code postal"])
    df = df[
        df["Surface reelle bati"].notna() &
        (df["Surface reelle bati"] >= 1)
        ]
    df = df[df["Valeur fonciere"] >= 1]

    ##
    # ENGINEERED FEATURE
    # NEW VARIABLE
    ##
    df["prix_m2"] = (df["Valeur fonciere"] / df["Surface reelle bati"]).replace(
        [np.inf, -np.inf],
        np.nan
    )
    df = df.dropna(subset=["prix_m2"])

    ##
    # CLEAN UP CATEGORY
    ##
    for col in ["Nature mutation", "Type local", "Commune"]:
        if col in df.columns:
            df[col] = df[col].cat.remove_unused_categories()

    return df


def clean_appartenance_commune(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    ##
    # PARSING
    ##
    for col in ["LIBGEO", "REG", "EPCI", "DEP"]:
        if col in df.columns:
            df = clean_str_col(df, col)

    df = clean_str_col(df, "CODGEO")
    df["CODGEO"] = df["CODGEO"].str.zfill(5)

    df = clean_str_col(df, "ZE2020")
    df["ZE2020"] = df["ZE2020"].str.zfill(4)

    ##
    # HANDLE MISSING / CRITICAL VALUES
    ##
    df = df.drop_duplicates(subset=["CODGEO"])
    df = df.dropna(subset=["CODGEO"])

    return df


def clean_stats_commune(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.rename(columns={"Code": "CODGEO"})

    ##
    # PARSING
    ##
    df = clean_str_col(df, "CODGEO")
    df["CODGEO"] = df["CODGEO"].str.zfill(5)

    df = clean_str_col(df, "Libellé")

    int_col = [
        "Logements 2022",
        "Nb d'emplois au lieu de travail (LT) 2022",
        "Unités légales (en nombre) 2023",
        "Créations d'entreprises (en nombre) 2025",
        "Nombre d'établissements 2024",
        "Effectifs salariés 2024",
        "École maternelle, primaire, élémentaire (en nombre) 2024",
        "Collège (en nombre) 2024",
        "Lycée (en nombre) 2024",
        "Pharmacie (en nombre) 2024",
        "Médecin généraliste (en nombre) 2024"
    ]
    for col in int_col:
        if col in df.columns:
            df = clean_str_col(df, col, to_int64=True)

    for col in ["Médiane du niveau de vie 2023",
                "Évol. annuelle moy. de la population 2017 - 2023 (en %)",
                "Évol. annuelle moy. de la pop. due au solde apparent entrées/sorties 2016-2022"]:
        if col in df.columns:
            df = clean_str_col(df, col, to_float=True)

    ##
    # DUPLICATES
    ##
    df = df.drop_duplicates(subset=["CODGEO"])

    return df


def clean_stats_intercommunes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.rename(columns={"Code": "EPCI"})

    ##
    # PARSING
    ##
    df = clean_str_col(df, "EPCI")

    df = clean_str_col(df, "Libellé")

    for col in ["Salaire net EQTP mensuel moyen 2023", "Taux de pauvreté 2023"]:
        if col in df.columns:
            df = clean_str_col(df, col, to_float=True)

    ##
    # DUPLICATES
    ##
    df = df.drop_duplicates(subset=["EPCI"])

    return df


def clean_stats_chomage(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.rename(columns={"Code": "ZE2020"})

    ##
    # PARSING
    ##
    df = clean_str_col(df, "ZE2020")
    df["ZE2020"] = df["ZE2020"].str.zfill(4)

    df = clean_str_col(df, "Libellé")

    df = clean_str_col(df, col="Taux de chômage trimestriel 2025-T4", to_float=True)

    ##
    # DUPLICATES
    ##
    df = df.drop_duplicates(subset=["ZE2020"])

    return df


def clean_str_col(df: pd.DataFrame, col: str,
                  to_category: bool = False,
                  to_float: bool = False,
                  to_int64: bool = False) -> pd.DataFrame:
    df[col] = df[col].astype("string").str.strip()

    if to_category:
        df[col] = df[col].astype("category")
    elif to_int64:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    elif to_float:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    else:
        df[col] = df[col].fillna("")
    return df
