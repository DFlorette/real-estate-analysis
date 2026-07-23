# French Real Estate Market Analysis - DVF 2025

## Context

Analysis of French real estate transactions from the Demandes de Valeurs
Foncières (DVF) 2025, enriched with socio-economic data at commune,
intercommunal, and employment zone levels.

**Scope** : France (mainland + overseas)  
**Raw volume** : 465,206 transactions - 18 variables  
**Cleaned volume (core market)** : 372,196 transactions (p10–p90)  
**Enriched dataset** : 379,890 transactions — 38 variables

**External sources:**
- Stats_Communes — INSEE 2022–2023 (income, employment, infrastructure)
- Stats_Intercommunes — INSEE 2023 (salary, poverty rate)
- Taux_Chomage — INSEE 2025 Q4 (unemployment by employment zone)
- Appartenance_Commune — INSEE (geographic hierarchy)

---

## Key Findings

### Price per m²

| Metric        | Raw        | Core market |
|---------------|------------|-------------|
| Mean          | 6,840/m²   | 3,920/m²    |
| Median        | 3,443/m²   | 3,443/m²    |
| Std deviation | 18,490     | 1,925       |
| Max           | 324,872/m² | 9,800/m²    |

> The median is stable before and after filtering - it represents the real
> market. The raw mean is artificially inflated by extreme values.

**Most expensive departments:**

| Dept                 | Median €/m² |
|----------------------|:-----------:|
| 75 - Paris           |    8,158    |
| 92 - Hauts-de-Seine  |    6,200    |
| 06 - Alpes-Maritimes |    4,778    |
| 94 - Val-de-Marne    |    4,708    |
| 83 - Var             |    3,810    |

**Seasonality:** volume varies up to 80% across months — prices stable (~10%).

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

237 distinct real estate zones identified via density-based clustering on geographic coordinates, profiled with socio-economic indicators.

**KMeans was rejected** — silhouette score collapsed after K=2, no meaningful elbow. HDBSCAN better handles the spatial and
socio-economic heterogeneity of the French market.

**Cluster distribution:**

| Cluster              | Transactions | %     | Median €/m² |
|----------------------|--------------|-------|-------------|
| Deprived Areas       | 90,078       | 26.8% | ~2,633      |
| Outliers             | 78,224       | 23.3% | ~2,778      |
| Affluent Urban       | 45,431       | 13.5% | ~4,552      |
| Premium              | 37,572       | 11.2% | ~3,826      |
| Countryside          | 32,093       | 9.6%  | ~3,482      |
| Exceptions           | 29,114       | 8.7%  | ~6,000      |
| Economically Fragile | 22,360       | 6.7%  | ~2,804      |
| Intermediate Areas   | 970          | 0.3%  | ~3,434      |

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

*`+/-` ≈ ±25% vs national median*

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

---

## Limitations

- DVF excludes off-plan sales (VEFA) and inheritances
- Data unavailable for Alsace-Moselle and Mayotte
- Prices do not account for property condition, floor level, or renovation state
- The Amiens €69M transaction (multi-lot sale) illustrates per-lot price/m²
  calculation limits on bundled sales
- Single-year scope (2025) — no inter-annual comparison available
- Geocoding at postal code level — not individual address

---

## Key Visualizations

|                                                           |                                                          |
|-----------------------------------------------------------|----------------------------------------------------------|
| ![Map](reports/figures/map_cluster_price.png)             | ![Clusters](reports/figures/map_clusters_geographic.png) |
| ![Heatmap](reports/figures/heatmap_cluster_profiles.png)  | ![Scatter](reports/figures/scatter_income_vs_price.png)  |

---

## Next Steps

- [ ] Interactive dashboard via the API (`api/app.py`)