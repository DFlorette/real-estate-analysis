# Data

Data files are not versioned in this repository (too large).

## Source

**Demandes de Valeurs Foncières (DVF)** — public data on real estate transactions in France.

- Provider : [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)
- Period used : 2025
- Licence : Licence Ouverte / Open Licence v2.0 (Etalab)

## Downloading

1. Download `ValeursFoncieres-2025.txt` on data.gouv.fr
2. Put the file in `data/raw/`
3. Launch the cleanup pipeline  :

```bash
python run_pipeline.py
```

## Structure

| Directory    | Content                                   |
|--------------|-------------------------------------------|
| `raw/`       | Raw DVF file uploaded (not modified)      |
| `clean/`     | Cleaned data — `dvf_clean.parquet`        |
| `processed/` | Enriched and aggregated data for analysis |
| `external/`  | Third-party data (geolocation, INSEE, …)  |

## Indicative volume

| File                        | Format             | Approximate size |
|-----------------------------|--------------------|------------------|
| `ValeursFoncieres-2025.txt` | CSV delimited `\|` | ~500 Mo          |
| `dvf_clean.parquet`         | Compressed Parquet | ~80 Mo           |