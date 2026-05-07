from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import calendar
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "dvf_core.parquet"

MONTH_NAMES = {
    i: calendar.month_name[i]
    for i in range(1, 13)
}

# Load data
if not DATA_PATH.exists():
    raise FileNotFoundError("Parquet file not found. Did you run preprocessing?")

df = pd.read_parquet(DATA_PATH)

app = FastAPI(
    title="Real Estate API",
    description="French real estate market analysis - DVF 2025",
    version="1.0.0",
)


class StatsResponse(BaseModel):
    median_price_m2: float
    mean_price_m2: float
    nb_transactions: int


class CityResponse(BaseModel):
    city: str
    median_price_m2: float
    nb_transactions: int


##
# ROOT
##
@app.get("/", tags=["Roots"])
def root():
    return {"message": "Real Estate API is running"}


##
# GLOBAL STATS
##
@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
def get_stats():
    return StatsResponse(
        median_price_m2=float(df["prix_m2"].median()),
        mean_price_m2=float(df["prix_m2"].mean()),
        nb_transactions=int(len(df)),
    )


##
# PRICE BY CITY
##
@app.get("/prices/cities", summary="Median price/m² by city", tags=["Prices"])
def prices_by_city(top_n: int = Query(default=10, ge=1, le=100)):
    city_prices = (
        df.groupby("Commune")["prix_m2"]
        .median()
        .sort_values(ascending=False)
        .head(top_n)
    )

    return city_prices.to_dict()


##
# PRICE BY DEPARTMENT
##
@app.get("/prices/departments", summary="Median price/m² by French department", tags=["Prices"])
def prices_by_dept():
    dept_prices = (
        df.groupby("Code departement")["prix_m2"]
        .median()
        .sort_values(ascending=False)
    )

    return dept_prices.to_dict()


##
# PRICE BY TYPE
##
@app.get("/prices/types", summary="Median price/m² by type", tags=["Prices"])
def prices_by_type():
    type_prices = (
        df.groupby("Type local")["prix_m2"]
        .median()
        .sort_values(ascending=False)
    )

    return type_prices.to_dict()


##
# FILTER BY CITY
##
@app.get("/city/{city_name}", response_model=CityResponse, summary="Stats for a specific city", tags=["Cities"])
def get_city_data(city_name: str):
    df_city = df[df["Commune"] == city_name.upper()]

    if df_city.empty:
        return HTTPException(status_code=404, detail=f"City '{city_name}' not found")

    return CityResponse(
        city=city_name.upper(),
        median_price_m2=float(df_city["prix_m2"].median()),
        nb_transactions=int(len(df_city)),
    )


##
# TRANSACTIONS BY MONTH
##
@app.get("/transactions/months", summary="Transaction count by month", tags=["Transactions"])
def transactions_by_month():
    month_transactions = (
        df.groupby(df["Date mutation"].dt.month)["Date mutation"]
        .count()
    )

    month_transactions.index = (
        month_transactions.index.map(MONTH_NAMES)
    )

    return month_transactions.to_dict()


##
# TRANSACTIONS BY CITY (TOP)
##
@app.get("/transactions/top_cities", summary="Transaction count for the top cities", tags=["Transactions"])
def top_cities_by_transactions(top_n: int = Query(default=10, ge=1, le=100)):
    top_cities_transactions = (
        df["Commune"]
        .value_counts()
        .head(top_n)
    )

    return top_cities_transactions.to_dict()


##
# TRANSACTIONS BY DEPARTMENT (TOP)
##
@app.get("/transactions/top_departments", summary="Transaction count for the top French departments",
         tags=["Transactions"])
def top_departments_by_transactions(top_n: int = Query(default=10, ge=1, le=101)):
    top_departments_transactions = (
        df["Code departement"]
        .value_counts()
        .head(top_n)
    )

    return top_departments_transactions.to_dict()


##
# TRANSACTIONS BY DEPARTMENT
##
@app.get("/transactions/departments", summary="Transaction count for each French department",
         tags=["Transactions"])
def transactions_departments():
    departments_transactions = (
        df["Code departement"]
        .value_counts()
        .reset_index()
    )

    departments_transactions.columns = ["Code departement", "nb_transactions"]

    return departments_transactions.to_dict(orient="records")
