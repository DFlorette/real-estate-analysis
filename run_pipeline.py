from pathlib import Path
import yaml

from src.data.enrich_data import enrich_with_stats
from src.data.geocoder import enrich_with_coordinates
from src.data.load_data import load_dvf, load_appartenance_commune, load_stats_commune, load_stats_intercommunes, \
    load_stats_chomage
from src.data.clean_data import clean_dvf, clean_appartenance_commune, clean_stats_commune, clean_stats_intercommunes, \
    clean_stats_chomage
from src.analysis.metrics import get_core_market

# Load config
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

processed_path = Path(config["paths"]["processed_data"])

if processed_path.exists():
    print("Processed data already exists - skipping pipeline")
else:
    # Load data
    print("Loading...")
    df_dvf = load_dvf(config["paths"]["raw_data"])
    df_app_co = load_appartenance_commune(config["paths"]["raw_appartenance_communes"])
    df_stats_commune = load_stats_commune(config["paths"]["raw_stats_commune"])
    df_stats_intercommunes = load_stats_intercommunes(config["paths"]["raw_stats_intercommunes"])
    df_stats_cho = load_stats_chomage(config["paths"]["raw_stats_chomage"])

    # Clean data
    print("Cleaning...")
    df_dvf = clean_dvf(df_dvf)
    df_app_co = clean_appartenance_commune(df_app_co)
    df_stats_commune = clean_stats_commune(df_stats_commune)
    df_stats_intercommunes = clean_stats_intercommunes(df_stats_intercommunes)
    df_stats_cho = clean_stats_chomage(df_stats_cho)

    df_dvf.to_parquet(config["paths"]["clean_data"], index=False)
    df_app_co.to_parquet(config["paths"]["clean"]["appartenance_communes"], index=False)
    df_stats_commune.to_parquet(config["paths"]["clean"]["stats_communes"], index=False)
    df_stats_intercommunes.to_parquet(config["paths"]["clean"]["stats_intercommunes"], index=False)
    df_stats_cho.to_parquet(config["paths"]["clean"]["stats_chomage"], index=False)

    # Core market data
    print("Filtering core market...")
    df_dvf_core = get_core_market(df_dvf)

    # Enrichment
    print("Geocoding...")
    df_dvf = enrich_with_coordinates(df_dvf_core)

    print("Enriching...")
    df_dvf = enrich_with_stats(
        df_dvf,
        appartenance_path=config["paths"]["clean"]["appartenance_communes"],
        stats_communes_path=config["paths"]["clean"]["stats_communes"],
        stats_chomage_path=config["paths"]["clean"]["stats_chomage"],
        stats_intercommunes_path=config["paths"]["clean"]["stats_intercommunes"],
    )

    # Save
    df_dvf.to_parquet(config["paths"]["processed_data"], index=False)

    print("Pipeline executed successfully")
    print(f"{len(df_dvf):,} rows saved to {processed_path}")
