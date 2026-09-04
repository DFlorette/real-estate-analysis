from unittest.mock import patch

import pandas as pd
import pytest
import requests

from src.data.geocoder import enrich_with_coordinates, geocode_address

NANTES_COORDS = [-1.555335, 47.239367]

MOCK_RESPONSE = {
    "features": [
        {
            "geometry": {
                "coordinates": NANTES_COORDS,
            }
        }
    ]
}


##
# geocode_address
##
@patch("src.data.geocoder.requests.get")
def test_geocode_success(mock_get):
    mock_get.return_value.json.return_value = MOCK_RESPONSE

    cache = {}
    result = geocode_address("44000 NANTES", cache)

    assert result == NANTES_COORDS
    assert cache == {"44000 NANTES": NANTES_COORDS}


@patch("src.data.geocoder.requests.get")
def test_geocode_api_error(mock_get):
    """A failing request returns None instead of raising."""
    mock_get.side_effect = requests.RequestException("connection reset")

    assert geocode_address("gdrgth", {}, retries=1) is None
    assert mock_get.call_count == 1


@patch("src.data.geocoder.requests.get")
def test_geocode_retries_on_error(mock_get):
    """Transient errors are retried, and a late success is still returned."""
    ok = mock_get.return_value
    ok.json.return_value = MOCK_RESPONSE
    mock_get.side_effect = [requests.RequestException("timeout"), ok]

    assert geocode_address("44000 NANTES", {}, retries=2) == NANTES_COORDS
    assert mock_get.call_count == 2


@patch("src.data.geocoder.requests.get")
def test_geocode_empty(mock_get):
    """The API answered, but no address matched."""
    mock_get.return_value.json.return_value = {"features": []}

    assert geocode_address("Unknown", {}, retries=1) is None


@patch("src.data.geocoder.requests.get")
def test_geocode_cache(mock_get):
    """A second lookup of the same address is served from the cache."""
    mock_get.return_value.json.return_value = MOCK_RESPONSE
    cache = {}

    first = geocode_address("44000 NANTES", cache)
    second = geocode_address("44000 NANTES", cache)

    assert first == second == NANTES_COORDS
    assert mock_get.call_count == 1


@pytest.mark.parametrize("address", ["", None, "75000 <NA>"])
@patch("src.data.geocoder.requests.get")
def test_geocode_invalid_address(mock_get, address):
    """Missing or unparsable addresses never reach the API."""
    assert geocode_address(address, {}) is None
    assert mock_get.call_count == 0


##
# enrich_with_coordinates
##
@pytest.fixture
def dvf_sample():
    return pd.DataFrame({
        "Code postal": ["44000", "75001"],
        "Commune": ["NANTES", "PARIS"],
        "prix_m2": [3000.0, 12000.0],
    })


@patch("src.data.geocoder.save_cache")
@patch("src.data.geocoder.load_cache", return_value={})
@patch("src.data.geocoder.geocode_address")
def test_enrich_adds_coordinates(mock_geocode, _load, _save, dvf_sample):
    mock_geocode.side_effect = [NANTES_COORDS, [2.3522, 48.8566]]

    out = enrich_with_coordinates(dvf_sample)

    assert out["longitude"].tolist() == [-1.555335, 2.3522]
    assert out["latitude"].tolist() == [47.239367, 48.8566]


@patch("src.data.geocoder.save_cache")
@patch("src.data.geocoder.load_cache", return_value={})
@patch("src.data.geocoder.geocode_address", return_value=NANTES_COORDS)
def test_enrich_drops_temp_column(_geocode, _load, _save, dvf_sample):
    """The intermediate 'city_address' key must not leak into the output."""
    out = enrich_with_coordinates(dvf_sample)

    assert "city_address" not in out.columns


@patch("src.data.geocoder.save_cache")
@patch("src.data.geocoder.load_cache")
@patch("src.data.geocoder.geocode_address")
def test_enrich_reuses_existing_cache(mock_geocode, mock_load, _save, dvf_sample):
    """Addresses already cached on disk trigger no new geocoding call."""
    mock_load.return_value = {
        "44000 NANTES": NANTES_COORDS,
        "75001 PARIS": [2.3522, 48.8566],
    }

    out = enrich_with_coordinates(dvf_sample)

    assert mock_geocode.call_count == 0
    assert out["latitude"].tolist() == [47.239367, 48.8566]


@patch("src.data.geocoder.save_cache")
@patch("src.data.geocoder.load_cache", return_value={})
@patch("src.data.geocoder.geocode_address", return_value=None)
def test_enrich_handles_failed_geocoding(_geocode, _load, _save, dvf_sample):
    """A failed lookup leaves NaN coordinates rather than breaking the pipeline."""
    out = enrich_with_coordinates(dvf_sample)

    assert out["longitude"].isna().all()
    assert out["latitude"].isna().all()
    assert len(out) == len(dvf_sample)


@patch("src.data.geocoder.save_cache")
@patch("src.data.geocoder.load_cache", return_value={})
@patch("src.data.geocoder.geocode_address", return_value=NANTES_COORDS)
def test_enrich_does_not_mutate_input(_geocode, _load, _save, dvf_sample):
    before = dvf_sample.copy()

    enrich_with_coordinates(dvf_sample)

    pd.testing.assert_frame_equal(dvf_sample, before)
