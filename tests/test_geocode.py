from unittest.mock import patch

from src.data.enrich_data import geocode_address, cache

MOCK_RESPONSE = {
    "features": [
        {
            "geometry": {
                "coordinates": [-1.555335, 47.239367],
            }
        }
    ]
}

def setup_function():
    cache.clear()


@patch("src.data.enrich_data.requests.get")
def test_geocode_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_RESPONSE

    result = geocode_address("Nantes")

    assert result == [-1.555335, 47.239367]

@patch("src.data.enrich_data.requests.get")
def test_geocode_api_error(mock_get):
    mock_get.return_value.status_code = 500

    result = geocode_address("gdrgth")

    assert result is None

@patch("src.data.enrich_data.requests.get")
def test_geocode_empty(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "features": []
    }

    result = geocode_address("Unknown")

    assert result is None

@patch("src.data.enrich_data.requests.get")
def test_geocode_cache(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = MOCK_RESPONSE

    geocode_address("Nantes")
    geocode_address("Nantes")

    assert mock_get.call_count == 1