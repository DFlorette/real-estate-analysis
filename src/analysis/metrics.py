import pandas as pd


def _in_band(prices: pd.Series, lower: float, upper: float) -> pd.Series:
    """Boolean mask of the [lower, upper] quantile band. NaN prices compare False."""
    low = prices.quantile(lower)
    high = prices.quantile(upper)
    return (prices >= low) & (prices <= high)


def get_core_market(
    df: pd.DataFrame,
    lower: float = 0.1,
    upper: float = 0.9,
    by: str | list[str] | None = None,
) -> pd.DataFrame:
    """Keep the central price band, cutting the tails of prix_m2.

    By default the quantiles are computed on the whole frame, so the band is
    national and the share of rows kept varies with local price levels: 46% in
    the cheapest departments and 51% in Paris, against 93% in mid-priced ones.
    Fine for national aggregates, biased for any department-level reading. See
    reports/summary.md, "Known bias of the p10-p90 filter".

    Pass ``by`` to compute the band within each group instead, which holds the
    retention rate at ``upper - lower`` everywhere by construction::

        get_core_market(df, by="Code departement")

    Rows whose ``by`` value is missing are dropped, since they belong to no
    group. Row order and index are preserved either way.
    """
    if by is None:
        mask = _in_band(df["prix_m2"], lower, upper)
    else:
        mask = (
            df.groupby(by, observed=True, dropna=True)["prix_m2"]
            .transform(_in_band, lower, upper)
            .fillna(False)
            .astype(bool)
        )

    return df[mask]
