def clean_dvf(df, min_surface=10, min_price=1000):
    df = df[df["valeur_fonciere"] > min_price]
    df = df[df["surface_reelle_bati"] > min_surface]
    df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]
    return df