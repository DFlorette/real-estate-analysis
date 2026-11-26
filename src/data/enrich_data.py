from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
CLEAN_DIR = BASE_DIR / "data" / "clean"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


###
# LOADERS
###
def load_appartenance_commune(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def load_stats_commune(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def load_stats_chomage(path: str) -> pd.DataFrame:
    return pd.read_parquet(path).drop(columns=["Libellé"], errors="ignore")


def load_stats_intercommunes(path: str) -> pd.DataFrame:
    return pd.read_parquet(path).drop(columns=["Libellé"], errors="ignore")


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
        on="CODGEO",
        how="left",
    )

    unmatched = ref["ZE2020"].isna().sum()
    print(f"  Stats_Communes ← Appartenance : {unmatched:,} unmatched communes")

    # Add Stats_Chomage
    ref = ref.merge(
        stats_chomage,
        on="ZE2020",
        how="left",
    )

    unmatched = ref["Taux de chômage trimestriel 2025-T4"].isna().sum()
    print(f"  ref ← Stats_Chomage : {unmatched:,} unmatched communes")

    # Add Stats_Intercommunes
    ref = ref.merge(
        stats_intercommunes,
        on="EPCI",
        how="left",
    )

    unmatched = ref["Taux de pauvreté 2023"].isna().sum()
    print(f"  ref ← Stats_Intercommunes : {unmatched:,} unmatched communes")

    return ref


###
# BUILD GEO CODE
###
# DVF records Paris, Lyon and Marseille by municipal arrondissement, while the
# INSEE commune-level exports only carry the city itself.
ARRONDISSEMENT_TO_COMMUNE = {
    **{f"751{i:02d}": "75056" for i in range(1, 21)},   # Paris 1er-20e
    **{f"6938{i}": "69123" for i in range(1, 10)},      # Lyon 1er-9e
    **{f"132{i:02d}": "13055" for i in range(1, 17)},   # Marseille 1er-16e
}


def build_geo_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate Département + Code commune → 5-digit INSEE code (CODGEO).
    e.g. '44' + '109' → '44109', '2A' + '4' → '2A004'

    Overseas departments have a 3-character code, so the commune part keeps
    2 digits: '971' + '1' → '97101'. Arrondissements are folded into their
    city: '75' + '116' → '75116' → '75056'.
    """
    dept = df["Code departement"].astype(str).str.zfill(2)
    commune = df["Code commune"].astype(str)
    commune = commune.where(dept.str.len() == 3, commune.str.zfill(3)).str.zfill(2)
    codgeo = dept + commune
    df["CODGEO"] = codgeo.replace(ARRONDISSEMENT_TO_COMMUNE)
    return df


###
# ENRICH DVF
###
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
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref.to_parquet(ref_path, index=False, compression="snappy")
    print(f"  ref_commune saved → {ref_path} ({len(ref):,} rows, {len(ref.columns)} cols)")

    print("Joining DVF ← ref_commune...")
    dvf = build_geo_code(dvf)

    ref_cols_do_drop = ["LIBGEO", "DEP", "REG"]

    dvf = dvf.merge(
        ref.drop(columns=ref_cols_do_drop, errors="ignore"),
        on="CODGEO",
        how="left",
    ).drop(columns=["CODGEO"], errors="ignore")

    unmatched = dvf["Médiane du niveau de vie 2023"].isna().sum()
    print(f"  DVF ← ref_commune : {unmatched:,} unmatched transactions ({unmatched / len(dvf):.1%})")

    return dvf
