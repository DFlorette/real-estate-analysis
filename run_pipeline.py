"""
End-to-end DVF pipeline.

load → clean → core market → geocoding → enrichment → clustering
Run from anywhere:  python run_pipeline.py [--force]
"""
import argparse
from pathlib import Path

import pandas as pd
import yaml

from src.data.load_data import (load_dvf,
                                load_appartenance_commune,
                                load_stats_commune,
                                load_stats_intercommunes,
                                load_stats_chomage)
from src.data.clean_data import (clean_dvf,
                                 clean_appartenance_commune,
                                 clean_stats_commune,
                                 clean_stats_intercommunes,
                                 clean_stats_chomage)
from src.analysis.metrics import get_core_market
from src.data.enrich_data import enrich_with_stats
from src.data.geocoder import enrich_with_coordinates
from src.features.build_features import rename_features
from src.analysis.clustering import add_clusters

##
# CONFIG
##
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"


def load_config(config_path: Path = CONFIG_PATH) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve(relative_path: str) -> Path:
    """Make a config path absolute, so the pipeline runs from any working directory."""
    return BASE_DIR / relative_path


def read_input(relative_path: str) -> Path:
    """Resolve an input path and fail early with an actionable message if it is missing."""
    path = resolve(relative_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found: {path}\n"
            f"See data/README.md for the download instructions."
        )

    return path


def write_parquet(df: pd.DataFrame, relative_path: str) -> Path:
    """Write a parquet file, creating the parent directory if needed."""
    path = resolve(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-run even if the output exists")
    return parser.parse_args()


def run(config: dict, force: bool = False) -> None:
    paths = config["paths"]
    processed_path = resolve(paths["processed_data"])

    if processed_path.exists() and not force:
        print(f"Output already exists at {processed_path} - use --force to re-run")
        return

    ##
    # LOAD
    ##
    print("Loading...")
    df_dvf = load_dvf(read_input(paths["raw_data"]))
    df_app_co = load_appartenance_commune(read_input(paths["raw_appartenance_communes"]))
    df_stats_commune = load_stats_commune(read_input(paths["raw_stats_commune"]))
    df_stats_intercommunes = load_stats_intercommunes(read_input(paths["raw_stats_intercommunes"]))
    df_stats_cho = load_stats_chomage(read_input(paths["raw_stats_chomage"]))

    ##
    # CLEAN
    ##
    print("Cleaning...")
    df_dvf = clean_dvf(df_dvf)
    df_app_co = clean_appartenance_commune(df_app_co)
    df_stats_commune = clean_stats_commune(df_stats_commune)
    df_stats_intercommunes = clean_stats_intercommunes(df_stats_intercommunes)
    df_stats_cho = clean_stats_chomage(df_stats_cho)

    ##
    # SAVE CLEAN
    ##
    write_parquet(df_dvf, paths["clean_data"])
    write_parquet(df_app_co, paths["clean"]["appartenance_communes"])
    write_parquet(df_stats_commune, paths["clean"]["stats_communes"])
    write_parquet(df_stats_intercommunes, paths["clean"]["stats_intercommunes"])
    write_parquet(df_stats_cho, paths["clean"]["stats_chomage"])

    ##
    # CORE MARKET
    ##
    print("Filtering core market...")
    df_dvf_core = get_core_market(df_dvf)
    write_parquet(df_dvf_core, paths["core_data"])
    print(f"  {len(df_dvf):,} cleaned rows -> {len(df_dvf_core):,} core market rows "
          f"({len(df_dvf_core) / len(df_dvf):.1%})")

    ##
    # GEOCODING
    ##
    print("Geocoding...")
    df_dvf_core = enrich_with_coordinates(df_dvf_core)

    ##
    # ENRICHMENT
    ##
    print("Enriching...")
    df_dvf_core = enrich_with_stats(
        df_dvf_core,
        appartenance_path=resolve(paths["clean"]["appartenance_communes"]),
        stats_communes_path=resolve(paths["clean"]["stats_communes"]),
        stats_chomage_path=resolve(paths["clean"]["stats_chomage"]),
        stats_intercommunes_path=resolve(paths["clean"]["stats_intercommunes"]),
    )

    df_dvf_core = rename_features(df_dvf_core)

    ##
    # CLUSTERING
    ##
    print("Clustering...")
    df_dvf_core = add_clusters(
        df_dvf_core,
        min_cluster_size=config["clustering"]["min_cluster_size"],
        min_samples=config["clustering"]["min_samples"],
    )

    ##
    # SAVE
    ##
    write_parquet(df_dvf_core, paths["processed_data"])

    print(f"Pipeline executed successfully - "
          f"{len(df_dvf_core):,} rows, {len(df_dvf_core.columns)} columns "
          f"saved to {processed_path}")


def main() -> None:
    args = parse_args()
    run(load_config(), force=args.force)


if __name__ == "__main__":
    main()
