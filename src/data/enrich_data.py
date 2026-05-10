import time
from pathlib import Path
import pandas as pd
from ratelimit import limits, sleep_and_retry
import requests
import json

CALLS = 5
PERIOD = 1

CACHE_PATH = Path("data/cache/geocode_cache.json")

if CACHE_PATH.exists():
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}


def save_cache():
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f)


@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def geocode_address(address, retries=3):
    if not address or "<NA>" in address:
        return None

    if address in cache:
        return cache[address]

    url = "https://data.geopf.fr/geocodage/search"
    params = {"q": address, "limit": 1}

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)

            response.raise_for_status()

            data = response.json()

            if data.get("features"):
                coords = data["features"][0]["geometry"]["coordinates"]
                cache[address] = coords
                return coords
        except requests.RequestException as e:
            print(
                f"[{attempt+1}/{retries}]"
                f"Geocoding error for {address}: {e}"
            )
            time.sleep(1)

    return None


def build_address(row):
    return (
        f"{row["Code postal"]} "
        f"{row["Commune"]}"
    )


def enrich_with_coordinates(df):
    df["city_address"] = df.apply(build_address, axis=1)

    unique_addresses = [
        addr
        for addr in df["city_address"].dropna().unique()
        if addr not in cache
    ]

    geo_map = {}

    for i, addr in enumerate(unique_addresses):
        cache[addr] = geocode_address(addr)

        if i % 100 == 0:
            save_cache()
            print(f"{i} city addresses processed")

    save_cache()

    df["coordinates"] = df["city_address"].map(cache)

    df["longitude"] = df["coordinates"].apply(
        lambda x: x[0] if isinstance(x, (list, tuple)) else None
    )

    df["latitude"] = df["coordinates"].apply(
        lambda x: x[1] if isinstance(x, (list, tuple)) else None
    )

    df = df.drop(columns=["coordinates", "city_address"])

    return df
