import yaml

from src.data.enrich_data import enrich_with_coordinates
from src.data.load_data import load_dvf
from src.data.clean_data import clean_dvf
from src.analysis.metrics import get_core_market

# Load config
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

# Load data
df = load_dvf(config["paths"]["raw_data"])

# Clean data
df = clean_dvf(df)

# Enrichment
df = enrich_with_coordinates(df)

# Core market data
df_core = get_core_market(df)

# Save
df_core.to_parquet(config["paths"]["processed_data"], index=False)

print("Pipeline executed successfully")
