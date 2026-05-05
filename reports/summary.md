# French Real Estate Market Analysis - DVF 2025

## Context

Analysis of French real estate transactions from the Demandes de Valeurs
Foncières (DVF) 2025, official source data.gouv.fr.

**Scope** : France (mainland + overseas)  
**Raw volume** : 465,206 transactions - 18 variables  
**Cleaned volume (core market)** : 372,196 transactions (p10–p90)  
**Memory usage** : ~68 MB

---

## Key Findings

### Price per m² - full dataset

| Metric | Raw | Core market |
|---|---|---|
| Mean | 6,840/m² | 3,920/m² |
| Median | 3,443/m² | 3,443/m² |
| Std deviation | 18,490 | 1,925 |
| Max | 324,872/m² | 9,800/m² |

> The median is stable before and after filtering - it represents the real
> market. The raw mean is artificially inflated by extreme values.

### Geographic breakdown (core market)

**Most expensive departments:**

| Dept | Median €/m² |
|---|---|
| 75 - Paris | 8,158 |
| 92 - Hauts-de-Seine | 6,200 |
| 06 - Alpes-Maritimes | 4,778 |
| 94 - Val-de-Marne | 4,708 |
| 83 - Var | 3,810 |

**Most expensive cities (core market, min. 955 transactions):**

| City | Median €/m² |
|---|---|
| Neuilly-sur-Seine | 8,667 |
| Paris 11th | 8,536 |
| Paris 16th | 8,500 |
| Levallois-Perret | 8,428 |
| Chamonix Mont-Blanc | 8,241 |

**Top 5 cities by transaction volume:**
Nice (7,818), Toulouse (7,441), Montpellier (4,791), Nantes (4,475),
Bordeaux (3,770)

### By property type (core market)

| Type | Median €/m² | Volume |
|---|---|---|
| Apartment | 3,472 | 326,470 |
| Commercial premises | 3,232 | 25,633 |
| House | 3,223 | 20,093 |

> Differences between property types are small once outliers are removed:
> the residential market is relatively homogeneous at the median level.

### Seasonality

**Volume:** strong seasonality - up to 80% difference between months.
- Peaks: July (40,084), December (35,321), September (35,903)
- Troughs: August (22,999), May (25,634), February (26,336)

**Price:** no significant seasonality - ~10% variation across the year.
- Slightly more expensive months: December, September, July
- Slightly cheaper months: April, August, February

### Correlations (Spearman, core market)

| Factor | Correlation with property value |
|---|---|
| Built area (m²) | **0.63** |
| Price per m² | 0.56 |
| Number of rooms | 0.46 |

> Key insight: after outlier removal, **built area overtakes price/m²** as
> the primary driver of value. Larger properties tend to have a lower price
> per m² - confirming a non-linear market structure.

---

## Methodology

| Step | Tool | Detail |
|---|---|---|
| Loading | Pandas / Parquet | `src/data/load_data.py` |
| Cleaning | Pandas | `src/data/clean_data.py` |
| Analysis | Pandas / Matplotlib | `notebooks/03_analysis.ipynb` |
| Outlier filtering | Quantile p10–p90 | ~20% of transactions removed |

**Core market definition:** transactions between the 10th and 90th percentile
of price/m² (1,412 - 9,800/m²), retaining 372,196 transactions.

---

## Limitations

- DVF excludes off-plan sales (VEFA) and inheritances
- Data unavailable for Alsace-Moselle and Mayotte
- Prices do not account for property condition, floor level, or renovation state
- The Amiens 69M € transaction (19 rows, multi-lot sale) illustrates the limits
  of per-lot price/m² calculation on bundled sales
- Single-year scope (2025) - no inter-annual comparison available

---

## Next Steps

- [ ] Inter-annual comparison 2020–2025
- [ ] Interactive dashboard via the API (`api/app.py`)