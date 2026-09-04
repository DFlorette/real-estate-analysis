# French Real Estate Analysis 🏠

[![tests](https://github.com/DFlorette/real-estate-analysis/actions/workflows/tests.yml/badge.svg)](https://github.com/DFlorette/real-estate-analysis/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Exploratory analysis of the French real estate market using official DVF
(Demandes de Valeurs Foncières) 2025 data — 465,000+ transactions enriched
with INSEE socio-economic indicators at commune, intercommunal, and
employment zone levels.

---

## Key Findings

- **Median price/m²** : €3,443 nationally (core market)  
- **Most expensive city** : Neuilly-sur-Seine at €8,988/m² (472 transactions)  
- **Primary price drivers** : local income (SL + MED_SL = 42% RF importance) and geography (lat/lon = 20%)  
- **273 real estate clusters** identified via HDBSCAN — from Deprived Areas to Exceptions  
- **Income decoupling** : tourist cities (Ajaccio, Fréjus) and periurban zones (Cergy, Pierrelaye) show high prices despite modest local income  
- **Seasonality** : volume varies up to 75% across months — prices remain stable (~6%)  

---

## Key Visualizations

| | |
|---|---|
| ![Map](reports/figures/map_cluster_price.png) | ![Clusters](reports/figures/map_clusters_geographic.png) |
| ![Heatmap](reports/figures/heatmap_cluster_profiles.png) | ![Scatter](reports/figures/scatter_income_vs_price.png) |

---

## Project Structure

```bash
real-estate-analysis/
├── notebooks/
│   ├── 01_exploration.ipynb        # Initial data exploration
│   ├── 02_cleaning.ipynb           # Cleaning pipeline
│   ├── 03_analysis.ipynb           # Full market analysis
│   ├── 04_features_analysis.ipynb  # RF feature importance + correlations
│   └── 05_clustering.ipynb         # HDBSCAN clustering + profiling
├── src/
│   ├── data/
│   │   ├── load_data.py            # Readers for DVF and the 4 INSEE files
│   │   ├── clean_data.py           # Typing, filtering, prix_m2
│   │   ├── geocoder.py             # API Géo + JSON cache (rate-limited)
│   │   └── enrich_data.py          # ref_commune + join onto DVF
│   ├── analysis/
│   │   ├── metrics.py              # Core market filter (p10–p90)
│   │   └── clustering.py           # HDBSCAN + cluster naming
│   └── features/
│       └── build_features.py       # Feature engineering and renaming
├── api/
│   └── app.py                      # REST API (FastAPI) — 18 endpoints
├── tests/
│   ├── test_geocode.py             # Geocoding and cache behaviour
│   └── test_metrics.py             # Core market filter
├── reports/
│   ├── summary.md                  # Full analysis results
│   ├── real_estate_dashboard.pbix  # Power BI dashboard
│   └── figures/                    # Exported charts
├── data/
│   ├── README.md                   # Data sources and download instructions
│   ├── raw/                        # Source files (not versioned)
│   ├── clean/                      # dvf_clean / dvf_core + INSEE (Parquet)
│   ├── cache/                      # geocode_cache.json
│   └── processed/                  # dvf_processed.parquet — pipeline output
├── config/
│   └── config.yaml                 # Paths and clustering parameters
├── run_pipeline.py                 # End-to-end pipeline
├── pyproject.toml                  # pytest configuration
└── requirements.txt
```

---

## Stack

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458)
![Sklearn](https://img.shields.io/badge/Sklearn-1.x-F7931E)
![Parquet](https://img.shields.io/badge/Format-Parquet-orange)

**Data wrangling** : Pandas, NumPy  
**Visualisation** : Matplotlib, Seaborn  
**Machine learning** : Scikit-learn (RandomForest), HDBSCAN  
**Geocoding** : API Géo (data.gouv.fr) + JSON cache  
**Storage** : Parquet (Snappy compression)  
**API** : FastAPI  
**Environment** : Python 3.11, virtual env  

---

## Dataset

| Property              | Value                                        |
|-----------------------|----------------------------------------------|
| Source                | data.gouv.fr — DVF 2025                      |
| Raw file rows         | 3,714,829                                    |
| After cleaning (built properties only) | 474,723                     |
| Core market (p10–p90) | 379,890 — 80.0% of cleaned rows              |
| Enriched dataset      | 379,890 — 42 variables                       |
| DVF variables loaded  | 18 (of ~43 available)                        |
| Memory                | 17 MB on disk (Parquet) — 150 MB in RAM      |
| License               | Licence Ouverte / Open Licence v2.0 (Etalab) |

**External sources (INSEE) :**
- Stats_Communes 2022–2023 — income, employment, infrastructure
- Stats_Intercommunes 2023 — salary, poverty rate
- Taux_Chômage 2025 Q4 — unemployment by employment zone
- Appartenance_Commune — geographic hierarchy

Raw data files are not versioned — see [`data/README.md`](data/README.md).

---

## Getting Started

### 1 — Clone & install

```bash
git clone https://github.com/DFlorette/real-estate-analysis.git
cd real-estate-analysis
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Download the data

Download `ValeursFoncieres-2025.txt` from
[data.gouv.fr](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)
and the INSEE files listed in [`data/README.md`](data/README.md).
Place all files in `data/raw/`.

### 3 — Run the pipeline

```bash
python run_pipeline.py
```

> First run includes geocoding (~500k addresses via API) — this may take
> several hours. Subsequent runs use the JSON cache automatically.

### 4 — Explore the notebooks

```bash
jupyter notebook notebooks/
```

---

## Results

Full findings in [`reports/summary.md`](reports/summary.md).

---

## Next Steps

- [ ] Interactive dashboard via the API (`api/app.py`)

---

## Author

**DFlorette** — Data Analyst
[GitHub](https://github.com/DFlorette)

---

## License

Code released under the [MIT License](LICENSE).

The underlying data keeps its own terms: DVF and the INSEE files are published
under the *Licence Ouverte / Open Licence v2.0* (Etalab) and are not covered by
the MIT license above.