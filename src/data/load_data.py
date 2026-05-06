import pandas as pd

cols = [
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

dtype_map = {
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
    return pd.read_csv(file_path, sep="|", usecols=cols, dtype=dtype_map, parse_dates=["Date mutation"])