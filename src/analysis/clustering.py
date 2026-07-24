import pandas as pd
import numpy as np
import hdbscan
from sklearn.preprocessing import StandardScaler


CLUSTER_FEATURES = [
    "prix_m2",
    "MED_SL",
    "SL",
    "CHOMAGE",
    "PR_MD60",
    "LOG",
    "NB_EMPLT",
    "MEDECIN",
    "ECOLE",
    "COLLEGE",
    "LYCEE",
    "PHARMACIE",
]

GEO_FEATURES = ["latitude", "longitude"]

def build_cluster_labels(
    df: pd.DataFrame,
    min_cluster_size: int = 500,
    min_samples: int = 50,
) -> pd.Series:
    """
    Run HDBSCAN on geographic coordinates.
    Returns a Series of integer cluster labels (index aligned with df).
    """
    X_geo = df[GEO_FEATURES].dropna().values

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
    )

    labels = clusterer.fit_predict(X_geo)

    return pd.Series(labels, index=df[GEO_FEATURES].dropna().index, name="cluster")


def label_cluster(row: pd.Series, prix_q9, med_sl_q9, sl_q9, sum_q9) -> str:

    prix_m2_val = row["prix_m2"]
    med_sl_val  = row["MED_SL"]
    sl_val      = row["SL"]
    chomage_val = row["CHOMAGE"]
    pr_md60_val = row["PR_MD60"]
    log_val     = row["LOG"]

    def safe(val):
        return float(val) if pd.notna(val) else float("nan")

    prix_m2_val = safe(prix_m2_val)
    med_sl_val  = safe(med_sl_val)
    sl_val      = safe(sl_val)
    chomage_val = safe(chomage_val)
    pr_md60_val = safe(pr_md60_val)
    log_val     = safe(log_val)

    if (
        (pd.notna(prix_q9)   and pd.notna(prix_m2_val) and prix_m2_val > prix_q9)
        or (pd.notna(med_sl_q9) and pd.notna(med_sl_val)  and med_sl_val > med_sl_q9)
        or (pd.notna(sl_q9)     and pd.notna(sl_val)       and sl_val > sl_q9)
    ):
        return "Exceptions"

    elif pd.notna(sum_q9) and pd.notna(row.sum()) and float(row.sum()) > sum_q9:
        return "Premium"

    elif (
        (pd.notna(prix_m2_val) and prix_m2_val > 0 and pd.notna(chomage_val) and chomage_val < 0)
        or (pd.notna(pr_md60_val) and pr_md60_val < 0 and (
            (pd.notna(med_sl_val) and med_sl_val > 2)
            or (pd.notna(sl_val) and sl_val > 2)
        ))
    ):
        return "Affluent Urban"

    elif pd.notna(prix_m2_val) and prix_m2_val < 0 and pd.notna(chomage_val) and chomage_val > 1:
        return "Economically Fragile"

    elif pd.notna(prix_m2_val) and prix_m2_val < 0 and (
        (pd.notna(pr_md60_val) and pr_md60_val > 1)
        or (pd.notna(chomage_val) and chomage_val > 1)
        or (pd.notna(med_sl_val) and med_sl_val < 0)
    ):
        return "Deprived Areas"

    elif all(
        pd.notna(row.get(col)) and float(row.get(col)) < 0
        for col in ["LOG", "MEDECIN", "ECOLE", "COLLEGE", "LYCEE", "PHARMACIE"]
    ):
        return "Countryside"

    else:
        return "Intermediate Areas"


def build_cluster_names(
    df: pd.DataFrame,
    cluster_col: str = "cluster",
) -> pd.Series:
    """
    Normalize cluster profiles and assign human-readable names.
    Returns a Series mapping each row to a cluster_name.
    """
    cluster_core = df[df[cluster_col] != -1]

    # Median profil
    cluster_profile = (
        cluster_core.groupby(cluster_col)[CLUSTER_FEATURES]
        .median()
    )

    # Normalisation
    profile_normalized = (
        (cluster_profile - cluster_profile.mean()) / cluster_profile.std()
    )

    profile_normalized = profile_normalized.astype(float)

    # Quantiles for label_cluster
    prix_q9   = profile_normalized["prix_m2"].quantile(0.9)
    med_sl_q9 = profile_normalized["MED_SL"].quantile(0.9)
    sl_q9     = profile_normalized["SL"].quantile(0.9)
    sum_q9    = profile_normalized.sum(axis="columns").quantile(0.9)

    # Mapping cluster_id → cluster_name
    cluster_name_map = profile_normalized.apply(
        label_cluster,
        axis=1,
        prix_q9=prix_q9,
        med_sl_q9=med_sl_q9,
        sl_q9=sl_q9,
        sum_q9=sum_q9,
    )

    # Map on all df
    return df[cluster_col].map(cluster_name_map).fillna("Outliers")


def add_clusters(
    df: pd.DataFrame,
    min_cluster_size: int = 500,
    min_samples: int = 50,
) -> pd.DataFrame:
    """
    Full clustering pipeline:
    1. HDBSCAN on geographic coordinates
    2. Assign human-readable cluster names
    Returns df with 'cluster' and 'cluster_name' columns added.
    """
    df = df.copy().fillna(np.nan)

    print("  Running HDBSCAN...")
    cluster_labels = build_cluster_labels(df, min_cluster_size, min_samples)

    df["cluster"] = cluster_labels.reindex(df.index).fillna(-1).astype(int)

    n_clusters = df[df["cluster"] != -1]["cluster"].nunique()
    n_outliers = (df["cluster"] == -1).sum()
    print(f"  {n_clusters} clusters found — {n_outliers:,} outliers (-1)")

    print("  Assigning cluster names...")
    df["cluster_name"] = build_cluster_names(df)

    print(df["cluster_name"].value_counts().to_string())

    return df