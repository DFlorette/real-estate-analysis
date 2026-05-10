import numpy as np
import pandas as pd


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
                "Code departement", "Section",
                "Nature culture", "Nature culture speciale"]:
        df = clean_str_col(df, col)

    # Date
    df["Date mutation"] = pd.to_datetime(df["Date mutation"], format="%d/%m/%Y")

    ##
    # FILTER : bâti only (exclude agricultural land)
    ##
    for col in ["Nature culture", "Nature culture speciale"]:
        if col in df.columns:
            df = df[df[col].fillna("") == ""]
            df = df.drop(columns=[col])

    if "Surface terrain" in df.columns:
        df = df.drop(columns=["Surface terrain"])

    ##
    # HANDLE MISSING / CRITICAL VALUES
    ##
    df = df.dropna(subset=["Valeur fonciere", "Code postal"])
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
    for col in ["Type local", "Commune"]:
        df[col] = df[col].cat.remove_unused_categories()

    return df


def clean_str_col(df: pd.DataFrame, col: str, to_category: bool = False) -> pd.DataFrame:
    df[col] = df[col].astype("string").str.strip()
    df[col].fillna("").astype(str)
    if to_category:
        df[col] = df[col].astype("category")
    return df