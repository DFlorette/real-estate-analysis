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

| Feature                | Importance | Interpretation                      |
|------------------------|------------|-------------------------------------|
| SL (avg salary)        | 22%        | High-wage areas have higher prices  |
| MED_SL (median income) | 20%        | Local wealth is the primary driver  |
| Latitude               | 14%        | North/South gradient, Paris premium |
| Longitude              | 6%         | East/West, coastal vs inland        |
| LOG (housing stock)    | 4.5%       | Urban density proxy                 |

> **Income (SL + MED_SL) accounts for 42% of price variance.**
> Geography adds another 20%, confirming that location operates independently of local wealth.

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

---

## Key Visualizations

|                                                           |                                                          |
|-----------------------------------------------------------|----------------------------------------------------------|
| ![Map](reports/figures/map_cluster_price.png)             | ![Clusters](reports/figures/map_clusters_geographic.png) |
| ![Heatmap](reports/figures/heatmap_cluster_profiles.png)  | ![Scatter](reports/figures/scatter_income_vs_price.png)  |

---

## Next Steps

- [x] Interactive dashboard via the API (`api/app.py`)