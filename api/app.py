import calendar
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "dvf_processed.parquet"

MONTH_NAMES = {i: calendar.month_name[i] for i in range(1, 13)}

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Parquet file not found at {DATA_PATH}. Did you run run_pipeline.py?"
    )

df = pd.read_parquet(DATA_PATH)

REQUIRED_COLS = ["prix_m2", "cluster_name", "longitude", "latitude", "MED_SL"]
missing = [col for col in REQUIRED_COLS if col not in df.columns]
if missing:
    raise ValueError(f"Missing columns in dataset: {missing}")

app = FastAPI(
    title="Real Estate API",
    description="French real estate market analysis - DVF 2025",
    version="1.0.0",
)


##
# MODELS
##
class StatsResponse(BaseModel):
    median_price_m2: float
    mean_price_m2: float
    median_standard_living: float
    median_unemployment: float
    nb_transactions: int


class CityResponse(BaseModel):
    city: str
    median_price_m2: float
    nb_transactions: int


##
# ROOT
##
@app.get("/", tags=["Root"])
def root():
    return {"message": "Real Estate API is running"}

##
# OVERALL STATS
##
@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
def get_stats():
    return StatsResponse(
        median_price_m2=float(df["prix_m2"].median()),
        mean_price_m2=float(df["prix_m2"].mean()),
        median_standard_living=float(df["MED_SL"].median()),
        median_unemployment=float(df["CHOMAGE"].median()),
        nb_transactions=int(len(df)),
    )

##
# PRICES
##
@app.get("/prices/cities", summary="Median price/m² by city", tags=["Prices"])
def prices_by_city(
        top_n: int = Query(default=10, ge=1, le=100),
        min_transactions: int = Query(default=100, ge=1),
):

    city_stats = df.groupby("Commune").agg(
        median_price_m2 = ("prix_m2", "median"),
        nb_transactions = ("prix_m2", "count"),
    )

    return (
        city_stats[city_stats["nb_transactions"] >= min_transactions]["median_price_m2"]
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
        .rename(columns={"Commune": "city"})
        .to_dict(orient="records")
    )

@app.get("/prices/departments", summary="Median price/m² by department", tags=["Prices"])
def prices_by_dept():
    return (
        df.groupby("Code departement")["prix_m2"]
        .median()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Code departement": "department", "prix_m2": "median_price_m2"})
        .to_dict(orient="records")
    )


@app.get("/prices/types", summary="Median price/m² by property type", tags=["Prices"])
def prices_by_type():
    return (
        df.groupby("Type local")["prix_m2"]
        .median()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Type local": "type", "prix_m2": "median_price_m2"})
        .to_dict(orient="records")
    )


##
# CITIES
##
@app.get("/city/{city_name}", response_model=CityResponse, tags=["Cities"])
def get_city_data(city_name: str):
    df_city = df[df["Commune"] == city_name.upper()]
    if df_city.empty:
        raise HTTPException(status_code=404, detail=f"City '{city_name}' not found")
    return CityResponse(
        city=city_name.upper(),
        median_price_m2=float(df_city["prix_m2"].median()),
        nb_transactions=int(len(df_city)),
    )


##
# TRANSACTIONS
##
@app.get("/transactions", summary="Paginated transactions", tags=["Transactions"])
def get_transactions(
    limit: int = Query(default=10000, ge=1, le=50000),
    offset: int = Query(default=0, ge=0),
):
    cols = [
        "Commune", "prix_m2", "Valeur fonciere", "Surface reelle bati", "longitude", "latitude",
        "cluster_name", "MED_SL", "SL", "CHOMAGE", "PR_MD60"
    ]
    return df[cols].dropna().iloc[offset:offset + limit].to_dict(orient="records")


@app.get("/transactions/months", summary="Transaction count by month", tags=["Transactions"])
def transactions_by_month():
    return (
        df.groupby(df["Date mutation"].dt.month)["Date mutation"]
        .count()
        .rename_axis("month_number")
        .reset_index(name="nb_transactions")
        .assign(month=lambda x: x["month_number"].map(MONTH_NAMES))
        .drop(columns=["month_number"])
        .to_dict(orient="records")
    )


@app.get("/transactions/top_cities", summary="Top cities by transaction count", tags=["Transactions"])
def top_cities_by_transactions(top_n: int = Query(default=10, ge=1, le=100)):
    return (
        df["Commune"]
        .value_counts()
        .head(top_n)
        .reset_index()
        .rename(columns={"Commune": "city", "count": "nb_transactions"})
        .to_dict(orient="records")
    )


@app.get("/transactions/top_departments", summary="Top departments by transaction count", tags=["Transactions"])
def top_departments_by_transactions(top_n: int = Query(default=10, ge=1, le=100)):
    return (
        df["Code departement"]
        .value_counts()
        .head(top_n)
        .reset_index()
        .rename(columns={"Code departement": "department", "count": "nb_transactions"})
        .to_dict(orient="records")
    )


@app.get("/transactions/departments", summary="Transaction count per department", tags=["Transactions"])
def transactions_by_department():
    return (
        df["Code departement"]
        .value_counts()
        .reset_index()
        .rename(columns={"Code departement": "department", "count": "nb_transactions"})
        .to_dict(orient="records")
    )


##
# CLUSTERS
##
@app.get("/clusters", summary="Paginated transactions with cluster info", tags=["Clusters"])
def get_clusters(
    limit: int = Query(default=10000, ge=1, le=50000),
    offset: int = Query(default=0, ge=0),
):
    cols = [
        "Commune", "prix_m2", "Valeur fonciere", "Surface reelle bati",
        "longitude", "latitude", "cluster_name",
        "MED_SL", "SL", "CHOMAGE", "PR_MD60",
    ]
    return df[cols].dropna().iloc[offset:offset + limit].to_dict(orient="records")


@app.get("/clusters/stats", summary="Socio-economic profile per cluster", tags=["Clusters"])
def get_clusters_stats():
    stats = (
        df.groupby("cluster_name")
        .agg(
            median_price_m2=("prix_m2", "median"),
            mean_price_m2=("prix_m2", "mean"),
            nb_transactions=("prix_m2", "count"),
            median_surface=("Surface reelle bati", "median"),
            median_income=("MED_SL", "median"),
            median_unemployment=("CHOMAGE", "median"),
        )
        .reset_index()
    )
    return stats.to_dict(orient="records")

##
# CORRELATIONS
##
@app.get("/correlations", tags=["Analysis"])
def get_correlations():
    """Spearman correlations with prix_m2"""

    numeric_cols = ["MED_SL", "SL", "CHOMAGE", "PR_MD60"]

    available = [col for col in numeric_cols if col in df.columns]

    corr = (
        df[available + ["prix_m2"]]
        .corr(method="spearman")["prix_m2"]
        .drop("prix_m2")
        .reset_index()
        .rename(columns={"index": "feature", "prix_m2": "correlation"})
        .sort_values("correlation", ascending=False)
    )

    corr["correlation"] = corr["correlation"].round(3)

    return corr.to_dict(orient="records")
