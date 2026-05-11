import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CLEAN_DIR = BASE_DIR / "data" / "clean"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


###
# LOADERS
###
def load_appartenance(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["Code géographique"] = df["Code géographique"].astype(str).str.zfill(5)
    df["Zone d'emploi 2020"] = df["Zone d'emploi 2020"].astype(str).str.zfill(4)
    df["Intercommunalité – Métropole"] = df["Intercommunalité – Métropole"].astype(str)
    return df


def load_stats_communes(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["CodeCommune"] = df["CodeCommune"].astype(str).str.zfill(5)
    return df


def load_stats_chomage(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["CodeZoneEmploi"] = df["CodeZoneEmploi"].astype(str).str.zfill(4)
    return df.drop(columns=["Libellé"], errors="ignore")


def load_stats_intercommunes(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["CodeInterco"] = df["CodeInterco"].astype(str)
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
        left_on="CodeCommune",
        right_on="Code géographique",
        how="left",
    ).drop(columns=["Libellé géographique"], errors="ignore")

    unmatched = ref["Zone d'emploi 2020"].isna().sum()
    print(f"  Stats_Communes ← Appartenance : {unmatched:,} unmatched communes")

    # Add Stats_Chomage
    ref = ref.merge(
        stats_chomage,
        left_on="Zone d'emploi 2020",
        right_on="CodeZoneEmploi",
        how="left",
    ).drop(columns=["CodeZoneEmploi"], errors="ignore")

    unmatched = ref["Taux de chômage"].isna().sum()
    print(f"  ref ← Stats_Chomage : {unmatched:,} unmatched communes")

    # Add Stats_Intercommunes
    ref = ref.merge(
        stats_intercommunes,
        left_on="Intercommunalité – Métropole",
        right_on="CodeInterco",
        how="left",
    ).drop(columns=["CodeInterco"], errors="ignore")

    unmatched = ref["Taux de pauvreté"].isna().sum()
    print(f"  ref ← Stats_Intercommunes : {unmatched:,} unmatched communes")

    return ref


###
# ENRICH DVF
###
def build_geo_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate Département + Code commune → 5-digit geo code.
    e.g. '75' + '056' → '75056'
    """
    dept = df["Departement"].astype(str).str.zfill(2)
    commune = df["Code commune"].astype(str).str.zfill(3)
    df["code_geo"] = dept + commune
    return df


def enrich_with_stats(
        dvf: pd.DataFrame,
        appartenance_path: str,
        stats_communes_path: str,
        stats_chomage_path: str,
        stats_intercommunes_path: str,
) -> pd.DataFrame:
    print("Loading external files...")
    appartenance = load_appartenance(appartenance_path)
    stats_communes = load_stats_communes(stats_communes_path)
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
        left_on="code_geo",
        right_on="CodeCommune",
        how="left",
    ).drop(columns=["code_geo", "CodeCommune", "Code géographique"], errors="ignore")

    unmatched = dvf["Médiane du niveau de vie"].isna().sum()
    print(f"  DVF ← ref_commune : {unmatched:,} unmatched transactions ({unmatched / len(dvf):.1%})")

    return dvf
