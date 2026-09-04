import pandas as pd


def add_features(df):
    df = df.copy()
    df["prix_m2"] = df["Valeur fonciere"] / df["Surface reelle bati"]
    return df

COLUMN_RENAME = {
    "Médiane du niveau de vie 2023": "MED_SL",
    "Logements 2022": "LOG",
    "Nb d'emplois au lieu de travail (LT) 2022": "NB_EMPLT",
    "Évol. annuelle moy. de la population 2017 - 2023 (en %)": "EVOL_POP",
    "Évol. annuelle moy. de la pop. due au solde apparent entrées/sorties 2016-2022": "EVOL_POP_E_S",
    "Unités légales (en nombre) 2023": "LEGAL_UNIT",
    "Créations d'entreprises (en nombre) 2025": "LEGAL_UNIT_NEW",
    "Nombre d'établissements 2024": "UNIT_LOC",
    "Effectifs salariés 2024": "NB_EMPL",
    "École maternelle, primaire, élémentaire (en nombre) 2024": "ECOLE",
    "Collège (en nombre) 2024": "COLLEGE",
    "Lycée (en nombre) 2024": "LYCEE",
    "Pharmacie (en nombre) 2024": "PHARMACIE",
    "Médecin généraliste (en nombre) 2024": "MEDECIN",
    "Taux de chômage trimestriel 2025-T4": "CHOMAGE",
    "Salaire net EQTP mensuel moyen 2023": "SL",
    "Taux de pauvreté 2023": "PR_MD60",
}

def rename_features(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=COLUMN_RENAME)

def prepare_rf_features(df: pd.DataFrame, features: list[str], target: str):
    data = df[features + [target]].dropna()
    x = data[features]
    y = data[target]

    print(f"  Rows kept   : {len(x):,} / {len(df):,}")
    print(f"  Rows dropped: {len(df) - len(x):,} (NaN)")

    return x, y
