import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CLEAN_DIR = BASE_DIR / "data" / "clean"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


###
# LOADERS
###
def load_appartenance_commune(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["CODGEO"] = df["CODGEO"].astype(str).str.zfill(5)
    df["ZE2020"] = df["ZE2020"].astype(str).str.zfill(4)
    df["EPCI"] = df["EPCI"].astype(str)
    return df


def load_stats_commune(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["CODGEO"] = df["CODGEO"].astype(str).str.zfill(5)
    return df


def load_stats_chomage(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["ZE2020"] = df["ZE2020"].astype(str).str.zfill(4)
    return df.drop(columns=["Libellé"], errors="ignore")


def load_stats_intercommunes(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["EPCI"] = df["EPCI"].astype(str)
    return df.drop(columns=["Libellé"], errors="ignore")


###
# BUILD REF_COMMUNE
###
def build_ref_commune(
        appartenance: pd.DataFrame,
        stats_communes: pd.DataFrame,
        stats_chomage: pd.DataFrame,
        stats_intercommunes: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a single reference table at city level.

    Joins:
        Stats_Communes        ← base (one row per city)
        Appartenance_Commune  ← adds zone emploi, interco, canton, département
        Stats_Chomage          ← adds taux de chômage via zone d'emploi
        Stats_Intercommunes   ← adds salaire net, taux de pauvreté via interco
    """

    # Stats_Communes + Appartenance_Commune
    ref = stats_communes.merge(
        appartenance,
        left_on="CODGEO",
        right_on="CODGEO",
        how="left",
    ).drop(columns=["Libellé"], errors="ignore")

    unmatched = ref["ZE2020"].isna().sum()
    print(f"  Stats_Communes ← Appartenance : {unmatched:,} unmatched communes")

    # Add Stats_Chomage
    ref = ref.merge(
        stats_chomage,
        left_on="ZE2020",
        right_on="ZE2020",
        how="left",
    ).drop(columns=["ZE2020"], errors="ignore")

    unmatched = ref["Taux de chômage trimestriel 2025-T4"].isna().sum()
    print(f"  ref ← Stats_Chomage : {unmatched:,} unmatched communes")

    # Add Stats_Intercommunes
    ref = ref.merge(
        stats_intercommunes,
        left_on="EPCI",
        right_on="EPCI",
        how="left",
    ).drop(columns=["EPCI"], errors="ignore")

    unmatched = ref["Taux de pauvreté 2023"].isna().sum()
    print(f"  ref ← Stats_Intercommunes : {unmatched:,} unmatched communes")

    return ref


###
# ENRICH DVF
###
def build_geo_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate Département + CODGEO → 5-digit geo code.
    e.g. '75' + '056' → '75056'
    """
    dept = df["Code departement"].astype(str).str.zfill(2)
    commune = df["Code commune"].astype(str).str.zfill(3)
    df["CODGEO"] = dept + commune
    return df


def enrich_with_stats(
        dvf: pd.DataFrame,
        appartenance_path: str,
        stats_communes_path: str,
        stats_chomage_path: str,
        stats_intercommunes_path: str,
) -> pd.DataFrame:
    print("Loading external files...")
    appartenance = load_appartenance_commune(appartenance_path)
    stats_communes = load_stats_commune(stats_communes_path)
    stats_chomage = load_stats_chomage(stats_chomage_path)
    stats_intercommunes = load_stats_intercommunes(stats_intercommunes_path)

    print("Building ref_commune...")
    ref = build_ref_commune(
        appartenance,
        stats_communes,
        stats_chomage,
        stats_intercommunes,
    )

    # Save ref_commune
    ref_path = PROCESSED_DIR / "ref_commune.parquet"
    ref.to_parquet(ref_path, index=False, compression="snappy")
    print(f"  ref_commune saved → {ref_path} ({len(ref):,} rows, {len(ref.columns)} cols)")

    print("Joining DVF ← ref_commune...")
    dvf = build_geo_code(dvf)

    dvf = dvf.merge(
        ref,
        left_on="CODGEO",
        right_on="CODGEO",
        how="left",
    ).drop(columns=["CODGEO", "CODGEO", "CODGEO", "LIBGEO", "DEP", "REG"], errors="ignore")

    unmatched = dvf["Médiane du niveau de vie 2023"].isna().sum()
    print(f"  DVF ← ref_commune : {unmatched:,} unmatched transactions ({unmatched / len(dvf):.1%})")

    return dvf
