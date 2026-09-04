import numpy as np
import pandas as pd
import pytest

from src.analysis.metrics import get_core_market


@pytest.fixture
def linear_prices():
    """prix_m2 = 1..100 — quantiles are exact and easy to reason about."""
    return pd.DataFrame({"prix_m2": np.arange(1, 101, dtype=float)})


def test_core_market_keeps_the_p10_p90_band(linear_prices):
    core = get_core_market(linear_prices)

    assert len(core) == 80
    assert core["prix_m2"].min() == 11
    assert core["prix_m2"].max() == 90


def test_core_market_bounds_are_inclusive():
    """A value sitting exactly on a quantile bound is kept."""
    df = pd.DataFrame({"prix_m2": [10.0, 20.0, 30.0, 40.0, 50.0]})

    core = get_core_market(df, lower=0.0, upper=1.0)

    assert len(core) == len(df)


def test_core_market_removes_extremes():
    """The p10-p90 filter is what cuts the DVF outliers (e.g. the 324k EUR/m2 rows)."""
    df = pd.DataFrame({"prix_m2": [1.0] + [3000.0] * 18 + [324_872.0]})

    core = get_core_market(df)

    assert 1.0 not in core["prix_m2"].values
    assert 324_872.0 not in core["prix_m2"].values


def test_core_market_custom_quantiles(linear_prices):
    core = get_core_market(linear_prices, lower=0.25, upper=0.75)

    assert len(core) == 50
    assert core["prix_m2"].min() == 26
    assert core["prix_m2"].max() == 75


def test_core_market_keeps_the_median_stable(linear_prices):
    """Key claim of reports/summary.md: the median survives the filter, the mean does not."""
    core = get_core_market(linear_prices)

    assert core["prix_m2"].median() == linear_prices["prix_m2"].median()


def test_core_market_preserves_other_columns_and_index(linear_prices):
    """Downstream steps (geocoding, clustering) realign on the original index."""
    df = linear_prices.assign(Commune=["NANTES"] * 100)

    core = get_core_market(df)

    assert list(core.columns) == ["prix_m2", "Commune"]
    assert core.index.equals(pd.RangeIndex(10, 90))


def test_core_market_does_not_mutate_input(linear_prices):
    before = linear_prices.copy()

    get_core_market(linear_prices)

    pd.testing.assert_frame_equal(linear_prices, before)


def test_core_market_drops_nan_prices():
    """NaN prix_m2 are excluded by the comparison - documented, not accidental."""
    df = pd.DataFrame({"prix_m2": [np.nan, 1000.0, 2000.0, 3000.0, np.nan]})

    core = get_core_market(df, lower=0.0, upper=1.0)

    assert core["prix_m2"].notna().all()
    assert len(core) == 3


def test_core_market_on_empty_frame():
    df = pd.DataFrame({"prix_m2": pd.Series([], dtype=float)})

    core = get_core_market(df)

    assert core.empty
