import yaml
from src.data.load_data import load_dvf
from src.data.clean_data import clean_dvf

# Load config
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

# Load data
df = load_dvf(config["paths"]["raw_data"])

# Clean data
df = clean_dvf(df,
               config["params"]["min_surface"],
               config["params"]["min_price"])

# Save

df.to_csv(config["paths"]["processed_data"], index=False)

print("Pipeline executed successfully")
