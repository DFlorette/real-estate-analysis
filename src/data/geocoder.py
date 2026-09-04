import json
import time
from pathlib import Path

import pandas as pd
import requests
from ratelimit import limits, sleep_and_retry

BASE_DIR = Path(__file__).resolve().parents[2]
CACHE_PATH = BASE_DIR / "data" / "cache" / "geocode_cache.json"

CALLS = 5
PERIOD = 1


def load_cache() -> dict:
    if CACHE_PATH.exists():
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f)


@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def geocode_address(address: str, cache: dict, retries: int = 3) -> list | None:
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
            print(f"[{attempt + 1}/{retries}] Geocoding error for {address}: {e}")
            time.sleep(1)

    return None


def enrich_with_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cache = load_cache()

    df["city_address"] = df["Code postal"].astype(str) + " " + df["Commune"].astype(str)

    unique_addresses = [
        addr for addr in df["city_address"].dropna().unique()
        if addr not in cache
    ]

    for i, addr in enumerate(unique_addresses):
        cache[addr] = geocode_address(addr, cache)

        if i % 100 == 0:
            save_cache(cache)
            print(f"{i}/{len(unique_addresses)} addresses processed")

    save_cache(cache)

    df["longitude"] = df["city_address"].map(cache).apply(
        lambda x: x[0] if isinstance(x, (list, tuple)) else None
    )
    df["latitude"] = df["city_address"].map(cache).apply(
        lambda x: x[1] if isinstance(x, (list, tuple)) else None
    )

    df = df.drop(columns=["city_address"])

    return df
