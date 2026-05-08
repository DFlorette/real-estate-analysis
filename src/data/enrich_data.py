from ratelimit import limits, sleep_and_retry
import requests

cache = {}

CALLS = 50
PERIOD = 1

@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def geocode_address(address):
    url = "https://data.geopf.fr/geocodage/search"
    params = {"q": address, "limit": 1}

    if address in cache:
        return cache[address]

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    if data.get("features"):
        coords = data["features"][0]["geometry"]["coordinates"]
        cache[address] = coords
        return coords
    return None