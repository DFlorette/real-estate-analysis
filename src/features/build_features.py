import numpy as np

def add_features(df):
    df["prix_m2"] = df["Valeur fonciere"] / df["Surface reelle bati"]
    return df