# French Real Estate Market Analysis - DVF 2025

## Context

Analysis of French real estate transactions from the Demandes de Valeurs
Foncières (DVF) 2025, enriched with socio-economic data at commune,
intercommunal, and employment zone levels.

**Scope** : France (mainland + overseas)  
**Raw volume** : 3,714,829 rows — 18 of ~43 variables loaded  
**Cleaned volume** : 474,723 transactions (built properties, valid price and surface)  
**Core market** : 379,890 transactions — 80.0% of cleaned rows (p10–p90)  
**Enriched dataset** : 379,890 transactions — 42 variables

**External sources:**
- Stats_Communes — INSEE 2022–2023 (income, employment, infrastructure)
- Stats_Intercommunes — INSEE 2023 (salary, poverty rate)
- Taux_Chomage — INSEE 2025 Q4 (unemployment by employment zone)
- Appartenance_Commune — INSEE (geographic hierarchy)

---

## Key Findings

### Price per m²

| Metric        | Cleaned       | Core market |
|---------------|---------------|-------------|
| Mean          | 17,973/m²     | 3,955/m²    |
| Median        | 3,443/m²      | 3,443/m²    |
| Std deviation | 173,124       | 2,017       |
| Max           | 33,912,500/m² | 10,250/m²   |

> The median is stable before and after filtering - it represents the real
> market. The raw mean is artificially inflated by extreme values.

**Most expensive departments:**

| Dept                 | Median €/m² |
|----------------------|:-----------:|
| 75 - Paris           |    8,400    |
| 92 - Hauts-de-Seine  |    6,250    |
| 06 - Alpes-Maritimes |    4,792    |
| 94 - Val-de-Marne    |    4,724    |
| 74 - Haute-Savoie    |    4,393    |

**Seasonality:** volume varies up to 75% across months (23,403 in August vs 40,953 in July)
— prices stable (~6%).

---

### 2 — Feature importance (Random Forest)

Features predicting price/m² : 20 socio-economic + geographic variables,
excluding surface and property value (data leakage).

`RandomForestRegressor(n_estimators=100, random_state=42)`, 80/20 split on the
335,842 rows with complete features (44,048 dropped for missing values).

**Hold-out performance : R² = 0.523, MAE = 867 €/m².**

| Feature                | Importance | Interpretation                          |
|------------------------|------------|-----------------------------------------|
| SL (avg salary)        | 22.4%      | High-wage areas have higher prices      |
| MED_SL (median income) | 19.8%      | Local wealth is the primary driver      |
| Longitude              | 13.8%      | East/West position — see caveat below   |
| Nombre pieces principales | 9.2%    | Small units sell at a higher price/m²   |
| Latitude               | 5.9%       | North/South position                    |
| LOG (housing stock)    | 4.5%       | Urban density proxy                     |

> **Income (SL + MED_SL) carries 42% of the model's total importance**, and the two
> coordinates another 20% — location contributes on top of local wealth rather than
> merely restating it.

**Caveat on the coordinates.** Neither correlates linearly with price (Spearman
ρ = 0.05 for longitude, 0.08 for latitude). Their weight comes from the trees
partitioning space into local markets, not from a national North/South or
East/West price gradient — the importance says *"which market"*, not *"which direction"*.

**Caveat on importance.** Gini importance ranks features within this model; it is
not variance explained. The model accounts for 52% of the variance in price/m²
(R² above), so nearly half remains driven by property-level characteristics absent
from the dataset — condition, floor, exact street, DPE.

---

### 3 — Clustering (HDBSCAN)

273 distinct real estate zones identified via density-based clustering on geographic coordinates, profiled with socio-economic indicators.

**KMeans was rejected** — silhouette score collapsed after K=2, no meaningful elbow. HDBSCAN better handles the spatial and
socio-economic heterogeneity of the French market.

**Cluster distribution:**

| Cluster              | Transactions | %      | Median €/m² | vs France |
|----------------------|--------------|--------|-------------|-----------|
| Deprived Areas       | 91,360       | 24.0%  | ~2,661      | -22.70%   |
| Outliers             | 78,688       | 20.7%  | ~2,766      | -19.66%   |
| Exceptions           | 47,951       | 12.6%  | ~6,986      | +102.91%  |
| Affluent Urban       | 41,498       | 10.9%  | ~4,730      | +37.39%   |
| Premium              | 39,080       | 10.3%  | ~3,784      | +9.91%    |
| Countryside          | 34,922       | 9.2%   | ~3,558      | +3.34%    |
| Economically Fragile | 24,155       | 6.4%   | ~2,790      | -18.96%   |
| Intermediate Areas   | 22,236       | 5.9%   | ~3,743      | +8.73%    |

**Cluster profiles:**

| Cluster              | Price/m² | Price | Surface | Unemployment | Income |
|----------------------|:--------:|:-----:|:-------:|:------------:|:------:|
| Deprived Areas       |    -     |   -   |    +    |      -       |   -    |
| Economically Fragile |    -     |  --   |    -    |      ++      |   -    |
| Intermediate Areas   |    +     |   +   |    +    |      +       |   +    |
| Countryside          |    +     |   +   |    +    |      +       |   +    |
| Premium              |    +     |   +   |    -    |      +       |   -    |
| Affluent Urban       |    ++    |  ++   |    -    |      -       |   +    |
| Exceptions           |   +++    |  +++  |    +    |      =       |   ++   |
| Outliers             |    -     |   -   |    +    |      -       |   +    |

*`+/-` ≈ ±25% vs national median — `++/--` ≈ ±50% — `+++` ≈ +100%*

**Geographic patterns:**
- Exceptions : Paris, Côte d'Azur, Geneva border, Arcachon, Basque Coast
- Premium : City centres of all major French cities (except Paris)
- Affluent Urban : Western Paris suburbs (92), Lyon west, Bordeaux Métropole
- Countryside : Periurban ring around major cities ("rurban" migration)
- Economically Fragile : Former industrial basins (Lorraine, Ardennes)

---

### 4 — Income vs price decoupling

Analysis of the price/m² vs median income scatter by postal code reveals three mechanisms where prices decouple from local income:

| Mechanism              | Example cities                       | Driver           |
|------------------------|--------------------------------------|------------------|
| Demographic tension    | Nantes, Toulouse, Rennes, Lille      | Supply < demand  |
| Tourism / second homes | Ajaccio, Fréjus, Corsica             | External buyers  |
| Periurban overspill    | Cergy, Pierrelaye, Villeneuve-d'Ascq | Proximity to hub |

> High income areas **always** translate into high prices (bottom-right quadrant is empty). 
> The reverse is not true — confirming that wealth is necessary but not sufficient: supply 
> tension and external demand act as independent price amplifiers.

---

### 5 — Socio-economic correlations (Spearman)

Correlations between socio-economic indicators and price/m²,
computed on the enriched core market dataset.

| Feature                | Correlation | Interpretation                          |
|------------------------|-------------|-----------------------------------------|
| MED_SL (median income) | **+0.395**  | Stronger local wealth → higher prices   |
| SL (average salary)    | **+0.250**  | High-wage employment zones drive prices |
| CHOMAGE (unemployment) | **-0.060**  | Weak negative signal                    |
| PR_MD60 (poverty rate) | **+0.005**  | No significant linear relationship      |

> **Note :** correlations are weaker than in the raw feature analysis notebook
> (MED_SL : 0.52 → 0.395) because the enriched dataset includes a broader
> geographic scope and different outlier composition after pipeline processing.

---

## Methodology

| Step              | Tool                 | Detail                                 |
|-------------------|----------------------|----------------------------------------|
| Loading           | Pandas / Parquet     | `src/data/load_data.py`                |
| Cleaning          | Pandas               | `src/data/clean_data.py`               |
| Geocoding         | API géo + cache JSON | `src/data/geocoder.py`                 |
| Enrichment        | Pandas joins         | `src/data/enrich_data.py`              |
| Outlier filtering | Quantile p10–p90     | ~20% of transactions removed           |
| Feature analysis  | Sklearn RandomForest | `notebooks/04_features_analysis.ipynb` |
| Clustering        | HDBSCAN              | `notebooks/05_clustering.ipynb`        |
| Dashboard         | Power BI + FastAPI   | `api/app.py`                           |

### Known bias of the p10–p90 filter

The core market is defined by a **single national band** (1,357 – 10,250 €/m²),
applied identically everywhere. That band removes 20.0% of transactions overall,
but not evenly — it is a *price* filter, so it cuts hardest wherever local prices
sit near a national extreme:

| Department        | Median €/m² | Transactions kept |
|-------------------|------------:|------------------:|
| 03 - Allier       |       1,333 |             46.4% |
| 42 - Loire        |       1,360 |             48.0% |
| 90 - Belfort      |       1,358 |             48.9% |
| **75 - Paris**    |   **9,920** |         **51.2%** |
| 44 - Loire-Atl.   |       3,329 |             93.0% |
| 91 - Essonne      |       3,000 |             93.2% |

*(departments with ≥ 1,000 transactions)*

Retention ranges from **46% to 93%** — a 47-point spread. Both tails are
legitimate market segments, not data errors: cheap rural stock at one end, central
Paris at the other. The effect is visible in the national mix — **Paris falls from
8.03% of transactions to 5.14%**, a 36% relative under-representation of the single
most-studied market in the dataset.

**Alternative available.** `get_core_market(df, by="Code departement")` clips
p10–p90 *within each department*, holding retention at 80% everywhere by
construction, for a near-identical national dataset: 379,791 rows instead of
379,890 (−99), national median 3,417 €/m² instead of 3,443 (−0.8%). Same volume,
same headline figure, no spatial distortion.

The global filter is kept here because the report's central claim — the median is
stable while the mean deflates from 17,973 to 3,955 €/m² — is unaffected by the
choice. **Any department-level reading of the core market should use the per-department
variant instead**; the clustering and Random Forest sections inherit this bias.

---

## Limitations

- DVF excludes off-plan sales (VEFA) and inheritances
- Data unavailable for Alsace-Moselle and Mayotte
- Prices do not account for property condition, floor level, or renovation state
- The Amiens €69M transaction (multi-lot sale) illustrates per-lot price/m²
  calculation limits on bundled sales
- Single-year scope (2025) — no inter-annual comparison available
- Geocoding at postal code level — not individual address
- Correlations computed on Spearman rank — linear relationships only
- The p10–p90 core-market filter is global, so it under-samples both the cheapest
  departments and Paris (46%–93% retention depending on the department — see
  *Known bias of the p10–p90 filter*)

---

## Key Visualizations

|                                                           |                                                          |
|-----------------------------------------------------------|----------------------------------------------------------|
| ![Map](reports/figures/map_cluster_price.png)             | ![Clusters](reports/figures/map_clusters_geographic.png) |
| ![Heatmap](reports/figures/heatmap_cluster_profiles.png)  | ![Scatter](reports/figures/scatter_income_vs_price.png)  |

---

## Next Steps

- [ ] Interactive dashboard via the API (`api/app.py`)