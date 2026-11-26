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
376,845 rows with complete features (3,045 dropped for missing values).

**Hold-out performance : R² = 0.607, MAE = 890 €/m².**

| Feature                   | Importance | Interpretation                          |
|---------------------------|------------|-----------------------------------------|
| MED_SL (median income)    | 47.2%      | Local wealth is the primary driver      |
| Longitude                 | 9.2%       | East/West position — see caveat below   |
| NB_EMPLT (local jobs)     | 6.5%       | Employment hubs price higher            |
| Nombre pieces principales | 6.5%       | Small units sell at a higher price/m²   |
| LOG (housing stock)       | 5.8%       | Urban density proxy                     |
| Latitude                  | 4.9%       | North/South position                    |
| SL (avg salary)           | 4.1%       | Largely redundant with MED_SL           |

> **Median income alone carries 47% of the model's total importance** (51% with
> average salary), and the two coordinates another 14% — location contributes on
> top of local wealth rather than merely restating it.

**Caveat on the income split.** `MED_SL` and `SL` measure close things, so the
forest leans on whichever splits best and the other gets little credit. Read the
51% as the weight of *income*, not as a ranking between the two indicators.

**Caveat on the coordinates.** Neither correlates linearly with price (Spearman
ρ = 0.05 for longitude, 0.08 for latitude). Their weight comes from the trees
partitioning space into local markets, not from a national North/South or
East/West price gradient — the importance says *"which market"*, not *"which direction"*.

**Caveat on importance.** Gini importance ranks features within this model; it is
not variance explained. The model accounts for 61% of the variance in price/m²
(R² above), so about 40% remains driven by property-level characteristics absent
from the dataset — condition, floor, exact street, DPE.

> **Revision note.** An earlier version of this section reported R² = 0.523 and
> income at 42% of the importance. That run silently lacked socio-economic data for
> every transaction in Paris, Lyon and Marseille (DVF codes them by arrondissement,
> INSEE by city) and in the overseas departments — 11.5% of the core market, and
> its most expensive part. With those rows joined, the model explains more and
> leans harder on income.

---

### 3 — Clustering (HDBSCAN)

273 distinct real estate zones identified via density-based clustering on geographic coordinates, profiled with socio-economic indicators.

**KMeans was rejected** — silhouette score collapsed after K=2, no meaningful elbow. HDBSCAN better handles the spatial and
socio-economic heterogeneity of the French market.

**Cluster distribution:**

| Cluster              | Transactions | %      | Median €/m² | vs France |
|----------------------|--------------|--------|-------------|-----------|
| Deprived Areas       | 110,601      | 29.1%  | ~2,727      | -20.78%   |
| Outliers             | 78,688       | 20.7%  | ~2,766      | -19.66%   |
| Affluent Urban       | 61,817       | 16.3%  | ~4,659      | +35.34%   |
| Exceptions           | 46,025       | 12.1%  | ~7,084      | +105.78%  |
| Countryside          | 32,188       | 8.5%   | ~3,647      | +5.93%    |
| Economically Fragile | 27,652       | 7.3%   | ~3,012      | -12.51%   |
| Premium              | 12,679       | 3.3%   | ~3,692      | +7.25%    |
| Intermediate Areas   | 10,240       | 2.7%   | ~3,658      | +6.25%    |

**Cluster profiles:**

| Cluster              | Price/m² | Price | Surface | Unemployment | Income |
|----------------------|:--------:|:-----:|:-------:|:------------:|:------:|
| Deprived Areas       |    -     |   -   |    =    |      =       |   -    |
| Economically Fragile |    -     |   -   |    -    |      ++      |   -    |
| Intermediate Areas   |    +     |   =   |    =    |      =       |   +    |
| Countryside          |    +     |   +   |    =    |      =       |   +    |
| Premium              |    +     |   +   |    +    |      ++      |   -    |
| Affluent Urban       |    ++    |  ++   |    =    |      =       |   +    |
| Exceptions           |   +++    |  +++  |    -    |      =       |   ++   |
| Outliers             |    -     |   -   |    +    |      =       |   =    |

*Cluster median vs national median — `=` within ±5% — `+/-` 5–25% — `++/--`
25–75% — `+++` above +75%*

**Geographic patterns** (departments and communes with the most transactions):
- Exceptions : Paris and its inner ring (92, 94, 93, 78), Swiss border (Ain, Doubs)
- Affluent Urban : Côte d'Azur (Nice, Cannes, Antibes), Bordeaux, Aix-en-Provence,
  central Lyon, Annecy, La Rochelle
- Premium : the Marseille arrondissements and Lyon 6e — see the caveat below
- Countryside : Var coast (Fréjus, Saint-Raphaël), outer Paris ring (95, 91, 78),
  Genevois (74)
- Economically Fragile : Mediterranean Languedoc (Montpellier, Nîmes, Agde,
  Perpignan, Béziers), Avignon, La Réunion
- Deprived Areas : large regional cities — Toulouse, Toulon, Dijon, Lille, Rennes,
  Grenoble, Reims, Brest, Rouen

The names are relative: they rank the 273 zones against each other, so a city
labelled *Deprived Areas* is below the other zones on the naming criteria, not
deprived in absolute terms. A large city can also span several zones — Toulouse
appears under both *Deprived Areas* and *Intermediate Areas*.

**Caveat on Premium.** INSEE publishes Paris, Lyon and Marseille only as whole
cities, so every arrondissement inherits city-wide figures — including stock
counts (housing, jobs, doctors, schools) that are city totals. Those inflated
counts push the Marseille arrondissements over the *Premium* threshold, which sums
all normalised indicators. The label reflects the size of the city, not a premium
market: its income is 10% below the national median and its unemployment 33% above.

---

### 4 — Income vs price decoupling

Analysis of the price/m² vs median income scatter by postal code reveals three mechanisms where prices decouple from local income:

| Mechanism              | Example cities                       | Driver           |
|------------------------|--------------------------------------|------------------|
| Demographic tension    | Nantes, Toulouse, Rennes, Lille      | Supply < demand  |
| Tourism / second homes | Ajaccio, Fréjus, Corsica, La Réunion (Saint-Paul, Saint-Leu) | External buyers  |
| Periurban overspill    | Cergy, Pierrelaye, Villeneuve-d'Ascq | Proximity to hub |

La Réunion appears here only since the overseas departments were joined to the
INSEE data; it was absent from earlier versions of this report.

> High income almost always translates into high prices; the reverse is not true —
> wealth is close to necessary but not sufficient: supply tension and external
> demand act as independent price amplifiers.
>
> The one systematic exception is the **Swiss border**. Of the 39 zones whose
> median income exceeds 1.5× the national figure while prices stay below the
> national median, 82% sit in the Doubs, the Jura or Haute-Savoie — consistent with
> residents earning Swiss salaries in markets priced locally. An earlier version of
> this report described that quadrant as empty; it is not.

---

### 5 — Socio-economic correlations (Spearman)

Correlations between socio-economic indicators and price/m²,
computed on the enriched core market dataset.

| Feature                | Correlation | Interpretation                          |
|------------------------|-------------|-----------------------------------------|
| MED_SL (median income) | **+0.454**  | Stronger local wealth → higher prices   |
| SL (average salary)    | **+0.340**  | High-wage employment zones drive prices |
| CHOMAGE (unemployment) | **-0.048**  | Weak negative signal                    |
| PR_MD60 (poverty rate) | **+0.062**  | No usable relationship                  |

> **Note :** an earlier version reported MED_SL at +0.395 and SL at +0.250. The gap
> came from the missing Paris, Lyon, Marseille and overseas rows (see the revision
> note in section 2): dropping the most expensive markets weakened the link between
> income and price.

---

## Conclusion — what to do with this

Four decisions the analysis actually supports.

**1. Screen on income, and drop the deprivation indicators.**
Median income is the single best predictor available here (ρ = 0.454, 47% of the
model's importance); average salary adds little on top of it (ρ = 0.340, 4%).
Unemployment (ρ = −0.048) and the poverty rate (ρ = +0.062) carry no usable signal — a scoring
model can drop both at no cost and gain two fewer joins to maintain. Rank
candidate areas on `MED_SL` and `SL`; ignore `CHOMAGE` and `PR_MD60`.

**2. Look for opportunities in the top-left quadrant, and treat its three
mechanisms differently.**
High income almost always produces high prices, so wealthy areas hold little
mispricing — the Swiss border, where residents likely earn Swiss salaries, is the one
systematic exception. The exploitable cases are the ones priced above
what local income explains, and their drivers do not carry the same risk:

| Mechanism | Cities | What it depends on | Durability |
|---|---|---|---|
| Demographic tension | Nantes, Toulouse, Rennes, Lille | Structural supply shortfall | Most durable — supply moves slowly |
| Periurban overspill | Cergy, Pierrelaye, Villeneuve-d'Ascq | The transport link to the hub | Checkable — verify the link before buying |
| Tourism / second homes | Ajaccio, Fréjus, Corsica, La Réunion | External, non-resident demand | Most fragile — exposed to a demand shock |

**3. Time the transaction for competition, not for price.**
Volume swings 75% across the year (23,403 transactions in August against 40,953
in July) while prices move only ~6%. Buying in a trough month buys negotiating
room against fewer competing offers — it does not buy a discount. Anyone
expecting a seasonal price dip should stop waiting for one.

**4. Benchmark against the cluster, not against France.**
Cluster medians run from −20.8% (Deprived Areas) to +105.8% (Exceptions) around
the national figure. A property compared to the €3,443/m² national median is
compared to almost nothing; compared to its cluster median it is compared to
similar markets. This is what the clustering is *for*.

### What this analysis cannot tell you

- **It does not price a property.** The model explains 61% of the variance in
  price/m² (R² = 0.607, MAE 890 €/m²). The rest sits in attributes absent from
  DVF — condition, floor, DPE, exact street. Use it to rank markets, not to
  value an address.
- **It shows association, not causation.** Nothing here establishes that raising
  local income raises prices rather than the reverse, or that a third factor
  drives both.
- **It is a single year.** 2025 alone, with no inter-annual comparison, so
  nothing here separates a trend from a one-off.
- **The core market is filtered globally**, which under-samples both the cheapest
  departments and Paris — see *Known bias of the p10–p90 filter*. Any
  department-level reading should re-run with `get_core_market(df, by="Code departement")`.

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
- INSEE publishes no median standard of living for Guadeloupe, Martinique and
  Guyane, so their 2,327 transactions carry no `MED_SL` (0.6% of the core market)
- Paris, Lyon and Marseille are joined to INSEE at city level: every arrondissement
  shares the same income and stock figures, so within-city variation is invisible
  to the socio-economic features (see *Caveat on Premium*)
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