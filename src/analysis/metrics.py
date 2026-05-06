import numpy as np
import pandas as pd


def get_core_market(df: pd.DataFrame, lower: float = 0.1, upper: float = 0.9) -> pd.DataFrame:
    q_low = df["prix_m2"].quantile(lower)
    q_high = df["prix_m2"].quantile(upper)
    return df[(df["prix_m2"] >= q_low) & (df["prix_m2"] <= q_high)]