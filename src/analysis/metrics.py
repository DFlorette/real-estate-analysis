import pandas as pd


def get_core_market(df: pd.DataFrame, lower: float = 0.1, upper: float = 0.9) -> pd.DataFrame:
    """Keep the central price band, cutting the tails of prix_m2.

    The quantiles are computed on the whole frame, so the band is national and
    the share of rows kept varies with local price levels: 46% in the cheapest
    departments and 51% in Paris, against 93% in mid-priced ones. Fine for
    national aggregates, biased for any department-level reading — clip within
    each department for that. See reports/summary.md, "Known bias of the
    p10-p90 filter".
    """
    q_low = df["prix_m2"].quantile(lower)
    q_high = df["prix_m2"].quantile(upper)
    return df[(df["prix_m2"] >= q_low) & (df["prix_m2"] <= q_high)]
