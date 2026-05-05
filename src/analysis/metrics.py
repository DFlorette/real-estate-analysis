import numpy as np

def detect_outliers(df):
    q1 = df["prix_m2"].quantile(0.25)
    q3 = df["prix_m2"].quantile(0.75)
    iqr = q3 - q1

    return df[(df["prix_m2"] < q1 - 1.5 * iqr) | (df["prix_m2"] > q3 + 1.5 * iqr)]