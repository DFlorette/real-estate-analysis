import json
import time
from pathlib import Path

import pandas as pd
import requests
from ratelimit import limits, sleep_and_retry

BASE_DIR = Path(__file__).resolve().parents[2]
CACHE_PATH = BASE_DIR / "data" / "cache" / "geocode_cache.json"

API_URL = "https://data.geopf.fr/geocodage/search"

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
def fetch_coordinates(address: str) -> list | None:
    """One rate-limited call to the API. Only the HTTP call consumes quota."""
    response = requests.get(API_URL, params={"q": address, "limit": 1}, timeout=10)

    response.raise_for_status()

    features = response.json().get("features")

    if not features:
        return None

    return features[0]["geometry"]["coordinates"]


def geocode_address(address: str, cache: dict, retries: int = 3) -> list | None:
    if not address or "<NA>" in address:
        return None

    if address in cache:
        return cache[address]

    for attempt in range(retries):
        try:
            coords = fetch_coordinates(address)
        except requests.RequestException as e:
            print(f"[{attempt + 1}/{retries}] Geocoding error for {address}: {e}")

            if attempt < retries - 1:
                time.sleep(1)

            continue

        # The API answered: either it matched, or the address does not exist.
        if coords is not None:
            cache[address] = coords

        return coords

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
