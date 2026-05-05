import numpy as np
import pandas as pd

def clean_dvf(df):
    ##
    # PARSING
    ##
    # Category
    df["Nature mutation"] = (
        df["Nature mutation"].astype(str).str.strip().astype("category")
    )

    df["Commune"] = (
        df["Commune"].astype(str).str.strip().astype("category")
    )

    df["Type local"] = (
        df["Type local"].astype(str).str.strip().astype("category")
    )

    # Int
    df["Valeur fonciere"] = (
        df["Valeur fonciere"].astype("str").str.replace(",", ".", regex=False)
    )
    df["Valeur fonciere"] = pd.to_numeric(df["Valeur fonciere"], errors="coerce")

    # Str
    df["Type de voie"] = (
        df["Type de voie"].astype(str).str.strip().astype("str")
    )

    df["Code voie"] = (
        df["Code voie"].astype(str).str.strip().astype("str")
    )

    df["Voie"] = (
        df["Voie"].astype(str).str.strip().astype("str")
    )

    df["Code postal"] = (
        df["Code postal"].astype(str).str.strip().astype("str")
    )

    df["Code departement"] = (
        df["Code departement"].astype(str).str.strip().astype("str")
    )

    df["Section"] = (
        df["Section"].astype(str).str.strip().astype("str")
    )

    df["Nature culture"] = (
        df["Nature culture"].astype(str).str.strip().astype("str")
    )

    df["Nature culture speciale"] = (
        df["Nature culture speciale"].astype(str).str.strip().astype("str")
    )

    # Date
    df["Date mutation"] = pd.to_datetime(df["Date mutation"], format="%d/%m/%Y")

    ##
    # HANDLE NA VALUES
    ##
    df = df.dropna(subset=["Valeur fonciere"])
    df = df.dropna(subset=["Surface reelle bati"])
    df = df[df["Surface reelle bati"] != 0]
    df = df.dropna(subset=["Code postal"])

    ##
    # CLEAN CATEGORY
    ##
    df["Type local"] = df["Type local"].cat.remove_unused_categories()
    df["Commune"] = df["Commune"].cat.remove_unused_categories()

    ##
    # FILTER
    ##
    df = df[
        df["Nature culture"].isna() |
        (df["Nature culture"].astype(str).str.strip() == "")
        ]

    df = df[
        df["Nature culture speciale"].isna() |
        (df["Nature culture speciale"].astype(str).str.strip() == "")
        ]

    df.drop(labels=["Nature culture", "Nature culture speciale", "Surface terrain"], axis="columns", inplace=True)

    ##
    # ANOMALIES
    ##
    df = df[
        df["Valeur fonciere"].notna() &
        (df["Valeur fonciere"] >= 1)
        ]

    df = df[
        df["Surface reelle bati"].notna() &
        (df["Surface reelle bati"] >= 1)
        ]

    ##
    # NEW VARIABLE
    ##
    df["prix_m2"] = df["Valeur fonciere"] / df["Surface reelle bati"]
    df["prix_m2"] = df["prix_m2"].replace(
        [np.inf, -np.inf],
        np.nan
    )
    df = df[
        (df["prix_m2"] > df["prix_m2"].quantile(0.01)) &
        (df["prix_m2"] < df["prix_m2"].quantile(0.99))
        ]

    df = df.dropna(subset=["prix_m2"])

    ##
    # HANDLE OUTLIERS
    # CORE MARKET
    ##
    q10 = df["prix_m2"].quantile(0.1)
    q90 = df["prix_m2"].quantile(0.9)

    df_core = df[
        (df["prix_m2"] >= q10) &
        (df["prix_m2"] <= q90)
        ]

    return df
