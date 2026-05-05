from fastapi import FastAPI
import pandas as pd

app = FastAPI()
df = pd.read_csv("data/processed/dvf_clean.csv")

@app.get("/prix_m2")
def prix_m2(ville: str):
    subset = df[df["nom_commune"] == ville]
    return subset[["valeur_fonciere", "surface_reelle_bati", "prix_m2"]].to_dict()

# Run with:
# uvicorn api.app:app --reload