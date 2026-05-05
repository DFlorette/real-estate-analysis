# API BAN
import requests

def geocode_address(address):
    url = "https://data.geopf.fr/geocodage/search"
    params = {"q": address, "limit": 1}

    response = requests.get(url, params=params)
    data = response.json()

    if data["features"]:
        coords = data["features"][0]["geometry"]["coordinates"]
        return coords
    return None