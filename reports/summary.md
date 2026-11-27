# French Real Estate Market Analysis - DVF 2025

## Context

Analysis of French real estate transactions from the Demandes de Valeurs
Foncières (DVF) 2025, enriched with socio-economic data at commune,
intercommunal, and employment zone levels.

**Scope** : France (mainland + overseas)  
**Raw volume** : 3,714,829 rows (1,329,649 sales) — 19 of ~43 variables loaded  
**Cleaned volume** : 805,167 sales of a single house or flat (456,574 houses, 348,593 flats)  
**Core market** : 644,255 sales — 80.0% of cleaned sales (p10–p90 within each department)  
**Enriched dataset** : 644,255 sales — 42 variables

**Unit of analysis : one sale.** DVF has one row per unit and per land-use line
of a sale, and every row repeats the sale's total value. The cleaning step
rebuilds sales and keeps those of exactly one dwelling, so that price/m² is the
price of that dwelling:

| Step | Sales |
|---|---:|
| All sales in the file | 1,329,649 |
| Market sales (`Vente`) with a value | 1,249,953 |
| … including at least one house or flat | 870,118 |
| … of a single dwelling (outbuildings allowed) | 805,215 |
| … with a valid surface and value | 805,167 |

The 64,903 sales of several dwellings, or of a dwelling with a commercial unit,
are left out: their value cannot be split between units.

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
| Mean          | 3,235/m²      | 3,056/m²    |
| Median        | 2,575/m²      | 2,573/m²    |
| Std deviation | 5,186         | 1,942       |
| Max           | 2,546,587/m²  | 13,898/m²   |

By type, in the core market : **houses 2,188 €/m²**, **flats 3,250 €/m²**.

> The median is stable before and after filtering - it represents the real
> market. The raw mean is pulled up by a residual tail of extreme values
> (symbolic prices, data-entry errors) that the p10–p90 band removes.

**Most expensive departments:**

| Dept                 | Median €/m² |
|----------------------|:-----------:|
| 75 - Paris           |    9,694    |
| 92 - Hauts-de-Seine  |    6,512    |
| 06 - Alpes-Maritimes |    4,932    |
| 94 - Val-de-Marne    |    4,754    |
| 74 - Haute-Savoie    |    4,461    |

**Most expensive cities** (≥ 100 sales) : Paris 6e (12,109 €/m²), Paris 7e (11,996),
Paris 4e (11,592).

**Seasonality:** volume varies up to 68% across months (42,974 in May vs 72,310 in July)
— prices stable (~5%).

---

### 2 — Feature importance (Random Forest)

Features predicting price/m² : 20 socio-economic + geographic variables,
excluding surface and property value (data leakage).

`RandomForestRegressor(n_estimators=100, random_state=42)`, 80/20 split on the
634,957 sales with complete features (9,298 dropped for missing values).

**Hold-out performance : R² = 0.849, MAE = 565 €/m²** with a random split —
**R² = 0.765, MAE = 630 €/m²** when the test set holds communes the model never saw.

All the features but the number of rooms are commune-level, so a random split
lets the model recognise a commune it has trained on. The commune-grouped split is
the honest figure for an unseen market; the gap between the two is small, so the
model is not merely memorising communes.

| Feature group | Features | Importance |
|---|---|---:|
| Town size and amenities | COLLEGE 12.1%, LYCEE 9.0%, ECOLE 7.5%, LEGAL_UNIT 7.5%, PHARMACIE 6.9%, LEGAL_UNIT_NEW 4.1%, NB_EMPL, MEDECIN, LOG, UNIT_LOC, NB_EMPLT | 58.4% |
| Income | SL 14.1%, MED_SL 7.8% | 21.9% |
| Location | longitude 8.0%, latitude 6.9% | 14.9% |
| Other | population growth, poverty, unemployment, rooms | 4.8% |

> **The first divide is urban vs rural, then income.** Once houses are in the data,
> most of the variance in price/m² separates towns from the countryside, and the
> amenity counts — schools, businesses, pharmacies — are what measure the size of
> a commune. Income still adds a fifth of the importance on top of it.

**Caveat on correlated features.** The amenity counts all measure town size, and
`SL` and `MED_SL` both measure income, so the forest credits whichever splits best
within each group. Read the shares by group, not as a ranking of single indicators.

**Caveat on the coordinates.** Neither correlates linearly with price (Spearman
ρ = 0.13 for longitude, −0.09 for latitude). Their weight comes from the trees
partitioning space into local markets, not from a national North/South or
East/West price gradient — the importance says *"which market"*, not *"which direction"*.

**Caveat on importance.** Gini importance ranks features within this model; it is
not variance explained. The model accounts for 77–85% of the variance in price/m²
(R² above); the rest is driven by property-level characteristics absent from the
dataset — condition, floor, exact street, DPE.

> **Revision note.** Earlier versions of this section reported R² = 0.523, then
> 0.607, with income at 42%, then 51%, of the importance. Two defects were behind
> them. Paris, Lyon, Marseille and the overseas departments had no socio-economic
> data (DVF codes the three cities by arrondissement, INSEE by city). And the
> dataset counted DVF rows rather than sales: it kept about 5% of the houses and
> priced bundled sales on the surface of a single unit, so it was 84% flats. On
> that flat-dominated sample income was the main driver, but the model did not
> generalise — its R² fell to 0.390 on unseen communes.

---

### 3 — Clustering (HDBSCAN)

395 distinct real estate zones identified via density-based clustering on geographic coordinates, profiled with socio-economic indicators.

**KMeans was rejected** — silhouette score collapsed after K=2, no meaningful elbow. HDBSCAN better handles the spatial and
socio-economic heterogeneity of the French market.

**A third of sales are in no zone.** HDBSCAN only forms a zone where sales are
dense (`min_cluster_size=500`). 212,105 sales (33%) — 80% of them houses — are
labelled *Outliers*: they are mostly rural France, where sales are too sparse to
form a zone at this setting. The zones describe urban and periurban France.

**Cluster distribution:**

| Cluster              | Sales        | %      | Median €/m² | vs France |
|----------------------|--------------|--------|-------------|-----------|
| Outliers             | 212,105      | 32.9%  | ~2,098      | -18.46%   |
| Deprived Areas       | 171,251      | 26.6%  | ~2,074      | -19.40%   |
| Affluent Urban       | 68,788       | 10.7%  | ~4,044      | +57.19%   |
| Countryside          | 68,339       | 10.6%  | ~3,102      | +20.56%   |
| Exceptions           | 55,948       | 8.7%   | ~7,121      | +176.79%  |
| Economically Fragile | 43,814       | 6.8%   | ~2,171      | -15.64%   |
| Premium              | 19,681       | 3.1%   | ~3,468      | +34.79%   |
| Intermediate Areas   | 4,329        | 0.7%   | ~3,457      | +34.37%   |

**Cluster profiles:**

| Cluster              | Price/m² | Price | Surface | Unemployment | Income |
|----------------------|:--------:|:-----:|:-------:|:------------:|:------:|
| Deprived Areas       |    -     |   -   |    =    |      =       |   -    |
| Economically Fragile |    -     |   -   |    =    |      ++      |   -    |
| Intermediate Areas   |    ++    |   =   |    -    |      -       |   =    |
| Countryside          |    +     |   +   |    =    |      +       |   +    |
| Premium              |    ++    |   +   |    -    |      +       |   =    |
| Affluent Urban       |    ++    |  ++   |    -    |      =       |   +    |
| Exceptions           |   +++    |  +++  |   --    |      =       |   ++   |
| Outliers             |    -     |   -   |    +    |      =       |   =    |

*Cluster median vs national median — `=` within ±5% — `+/-` 5–25% — `++/--`
25–75% — `+++` above +75%*

**Geographic patterns** (departments and communes with the most sales):
- Exceptions : Paris and its inner ring (92, 94, 93, 78), Côte d'Azur (Cannes, Var),
  Haute-Savoie
- Affluent Urban : large dynamic cities — Nice, Bordeaux, Nantes, Rennes,
  Villeurbanne, Aix-en-Provence, Annecy, Toulon, Antibes
- Premium : Toulouse and the Lyon and Marseille arrondissements — see the caveat below
- Countryside : coastal towns (Agde, Fréjus, Saint-Raphaël, Sète, Royan, Vannes)
  and the outer Paris ring (95, 78, 91)
- Economically Fragile : Languedoc-Roussillon (Nîmes, Montpellier, Perpignan,
  Béziers, Narbonne, Carcassonne), Nord (Tourcoing, Calais), La Réunion
- Deprived Areas : regional and former industrial cities — Dijon, Brest,
  Saint-Étienne, Lille, Grenoble, Le Havre, Reims, Caen, Clermont-Ferrand
- Intermediate Areas : parts of Montpellier and Nantes

The names are relative: they rank the 395 zones against each other, so a city
labelled *Deprived Areas* is below the other zones on the naming criteria, not
deprived in absolute terms, and *Countryside* now labels coastal and periurban
towns rather than rural France, which sits mostly in *Outliers*. A large city can
also span several zones — Montpellier appears under both *Economically Fragile*
and *Intermediate Areas*.

**Caveat on Premium.** The *Premium* threshold sums all normalised indicators,
including stock counts (housing, jobs, doctors, schools) that grow with the size
of the commune. INSEE publishes Paris, Lyon and Marseille only as whole cities, so
every arrondissement inherits city-wide totals, and Toulouse is a single very
large commune. The label reflects city size, not a premium market: its income is
4% below the national median and its unemployment 17% above.

---

### 4 — Income vs price decoupling

Analysis of the price/m² vs median income scatter by commune reveals three mechanisms where prices decouple from local income:

| Mechanism              | Example cities                       | Driver           |
|------------------------|--------------------------------------|------------------|
| Demographic tension    | Lille, Toulouse, Montpellier, Rennes, Tours | Supply < demand  |
| Tourism / second homes | Corsica (Ajaccio, Bastia, Zonza), Fréjus, Arles, La Réunion (Saint-Paul, Saint-Leu) | External buyers  |
| Periurban overspill    | Cergy, Pontoise, Pierrelaye, Villeneuve-d'Ascq | Proximity to hub |

> High income almost always translates into high prices: only 8 zones (23 sales)
> combine a median income above 1.5× the national figure with a price below the
> national median. The reverse is not true — wealth is close to necessary but not
> sufficient: supply tension and external demand act as independent price amplifiers.

---

### 5 — Socio-economic correlations (Spearman)

Correlations between socio-economic indicators and price/m²,
computed on the enriched core market dataset.

| Feature                | Correlation | Interpretation                          |
|------------------------|-------------|-----------------------------------------|
| SL (average salary)    | **+0.517**  | High-wage employment zones drive prices |
| MED_SL (median income) | **+0.474**  | Stronger local wealth → higher prices   |
| PR_MD60 (poverty rate) | **+0.103**  | Weak — poverty is higher in large cities, where prices are too |
| CHOMAGE (unemployment) | **-0.038**  | No usable relationship                  |

> **Note :** earlier versions reported MED_SL at +0.395, then +0.454, on a dataset
> missing Paris, Lyon, Marseille and most houses (see the revision note in section 2).

---

## Conclusion — what to do with this

Four decisions the analysis actually supports.

**1. Screen on town size first, then income, and drop the deprivation indicators.**
The size and amenities of a commune carry most of the model's importance (58%):
price/m² first separates towns from the countryside. Income comes next (22% of
the importance; ρ = 0.517 for average salary, 0.474 for median income).
Unemployment (ρ = −0.038) and the poverty rate (ρ = +0.103) carry no usable signal
— a scoring model can drop both at no cost and gain two fewer joins to maintain.
Rank candidate areas on amenities and `SL` / `MED_SL`; ignore `CHOMAGE` and `PR_MD60`.

**2. Look for opportunities in the top-left quadrant, and treat its three
mechanisms differently.**
High income almost always produces high prices — only 8 zones break that rule —
so wealthy areas hold little mispricing. The exploitable cases are the ones priced above
what local income explains, and their drivers do not carry the same risk:

| Mechanism | Cities | What it depends on | Durability |
|---|---|---|---|
| Demographic tension | Lille, Toulouse, Montpellier, Rennes, Tours | Structural supply shortfall | Most durable — supply moves slowly |
| Periurban overspill | Cergy, Pontoise, Pierrelaye, Villeneuve-d'Ascq | The transport link to the hub | Checkable — verify the link before buying |
| Tourism / second homes | Corsica, Fréjus, Arles, La Réunion | External, non-resident demand | Most fragile — exposed to a demand shock |

**3. Time the transaction for competition, not for price.**
Volume swings 68% across the year (42,974 sales in May against 72,310
in July) while prices move only ~5%. Buying in a trough month buys negotiating
room against fewer competing offers — it does not buy a discount. Anyone
expecting a seasonal price dip should stop waiting for one.

**4. Benchmark against the cluster, not against France.**
Cluster medians run from −19.4% (Deprived Areas) to +176.8% (Exceptions) around
the national figure. A property compared to the €2,573/m² national median is
compared to almost nothing; compared to its cluster median it is compared to
similar markets. This is what the clustering is *for*.

### What this analysis cannot tell you

- **It does not price a property.** The model explains 77% of the variance in
  price/m² across unseen communes (R² = 0.765, MAE 630 €/m²). The rest sits in attributes absent from
  DVF — condition, floor, DPE, exact street. Use it to rank markets, not to
  value an address.
- **It shows association, not causation.** Nothing here establishes that raising
  local income raises prices rather than the reverse, or that a third factor
  drives both.
- **It is a single year.** 2025 alone, with no inter-annual comparison, so
  nothing here separates a trend from a one-off.
- **It covers single-dwelling sales only.** Sales of several dwellings or of a
  dwelling with a shop (64,903) are left out — see *Unit of analysis* above.

---

## Methodology

| Step              | Tool                 | Detail                                 |
|-------------------|----------------------|----------------------------------------|
| Loading           | Pandas / Parquet     | `src/data/load_data.py`                |
| Cleaning          | Pandas               | `src/data/clean_data.py`               |
| Geocoding         | API géo + cache JSON | `src/data/geocoder.py`                 |
| Enrichment        | Pandas joins         | `src/data/enrich_data.py`              |
| Outlier filtering | Quantile p10–p90     | 20% of sales removed, per department   |
| Feature analysis  | Sklearn RandomForest | `notebooks/04_features_analysis.ipynb` |
| Clustering        | HDBSCAN              | `notebooks/05_clustering.ipynb`        |
| Dashboard         | Power BI + FastAPI   | `api/app.py`                           |

### Core market filter

The core market keeps the p10–p90 band of price/m² **within each department**
(`get_core_market(df, by="Code departement")`), so every department keeps 80% of
its sales by construction.

A single national band would not be usable on this data. Once houses are in the
dataset, the national p10–p90 band is 1,064 – 5,926 €/m², below the median of
Paris (9,694 €/m²) — it is a *price* filter, and it cuts hardest wherever local
prices sit near a national extreme:

| Department          | Median €/m² | Kept by a national band |
|---------------------|------------:|------------------------:|
| **75 - Paris**      |   **9,694** |                **5.1%** |
| 23 - Creuse         |         852 |                   35.5% |
| 92 - Hauts-de-Seine |       6,512 |                   37.8% |
| 52 - Haute-Marne    |       1,005 |                   46.2% |
| 77 - Seine-et-Marne |       3,038 |                   96.2% |
| 91 - Essonne        |       3,143 |                   96.5% |

*(departments with ≥ 1,000 sales)*

Paris would fall from 3.62% of cleaned sales to 0.23% of the core market. The
per-department band gives almost the same national dataset — 644,255 sales
instead of 644,137, median 2,573 €/m² instead of 2,575 — without that distortion.

What the per-department band does *not* remove are extreme values in a
department's own tails: the core market still reaches 13,898 €/m² in Paris and
265 €/m² in the cheapest rural sales. They are real segments of those markets.

---

## Limitations

- Inheritances are not in DVF; exchanges, auctions, expropriations and off-plan
  sales (VEFA) are in DVF but excluded here, as they do not follow open-market prices
- Data unavailable for Alsace-Moselle and Mayotte
- INSEE publishes no median standard of living for Guadeloupe, Martinique and
  Guyane, so their 3,167 sales carry no `MED_SL`; with small communes under
  statistical secrecy, 5,938 sales (0.9%) lack it
- Rural France is mostly outside the HDBSCAN zones (33% of sales are *Outliers*)
- Paris, Lyon and Marseille are joined to INSEE at city level: every arrondissement
  shares the same income and stock figures, so within-city variation is invisible
  to the socio-economic features (see *Caveat on Premium*)
- Prices do not account for property condition, floor level, or renovation state
- Sales of several dwellings, or of a dwelling with a commercial unit, are
  excluded (64,903 sales): their value cannot be split between units
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

- [ ] Interactive dashboard via the API (`api/app.py`)