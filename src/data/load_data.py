import pandas as pd

dvf_cols = [
    "Date mutation",
    "Nature mutation",
    "Valeur fonciere",
    "No voie",
    "Type de voie",
    "Code voie",
    "Voie",
    "Code postal",
    "Commune",
    "Code departement",
    "Code commune",
    "Section",
    "No plan",
    "Code type local",
    "Type local",
    "Surface reelle bati",
    "Nombre pieces principales",
    "Surface terrain",
    "Nature culture",
    "Nature culture speciale"
]

dvf_dtype_map = {
    "Code postal": "str",
    "Code departement": "str",
    "Nature mutation": "category",
    "Type local": "category",
    "Type de voie": "category",
    "Commune": "category",
    "Nature culture": "str",
    "Nature culture speciale": "str",
}


def load_dvf(file_path):
    return pd.read_csv(file_path, sep="|", usecols=dvf_cols, dtype=dvf_dtype_map, low_memory=False)


app_co_cols = [
    "CODGEO",
    "LIBGEO",
    "DEP",
    "REG",
    "EPCI",
    "ZE2020"
]

app_co_dtype_map = {
    "CODGEO": "str",
    "LIBGEO": "str",
    "DEP": "str",
    "REG": "str",
    "EPCI": "str",
    "ZE2020": "str"
}


def load_appartenance_commune(file_path) -> pd.DataFrame:
    return pd.read_excel(file_path, engine="calamine", header=5, usecols=app_co_cols, dtype=app_co_dtype_map)


stats_co_cols = [
    "Code",
    "Libellé",
    "Médiane du niveau de vie 2023",
    "Logements 2022",
    "Nb d'emplois au lieu de travail (LT) 2022",
    "Évol. annuelle moy. de la population 2017 - 2023 (en %)",
    "Évol. annuelle moy. de la pop. due au solde apparent entrées/sorties 2016-2022",
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

na_values = [
    "N/A - résultat non disponible",
    "N/A - secret statistique",
    "N/A - division par 0"
]


def load_stats_commune(file_path) -> pd.DataFrame:
    return pd.read_csv(file_path, sep=";", header=2, usecols=stats_co_cols, dtype=str, na_values=na_values)


stats_intercommunes_cols = [
    "Code",
    "Libellé",
    "Salaire net EQTP mensuel moyen 2023",
    "Taux de pauvreté 2023"
]


def load_stats_intercommunes(filepath) -> pd.DataFrame:
    return pd.read_csv(filepath, sep=";", usecols=stats_intercommunes_cols, dtype=str, na_values=na_values)


stats_chomage_cols = [
    "Code",
    "Libellé",
    "Taux de chômage trimestriel 2025-T4"
]


def load_stats_chomage(file_path) -> pd.DataFrame:
    return pd.read_csv(file_path, sep=";", usecols=stats_chomage_cols, dtype=str, na_values=na_values)
