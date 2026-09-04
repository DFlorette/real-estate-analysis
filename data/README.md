# Data

Data files are not versioned in this repository (the raw DVF file alone is
~474 MB). The pipeline needs **five** input files, all of them free and public.
Download them into `data/raw/` under the exact names below — `config/config.yaml`
looks them up by name — then run `python run_pipeline.py`.

## 1. DVF — transactions

| | |
|---|---|
| **File name** | `ValeursFoncieres-2025.txt` |
| **Source** | [data.gouv.fr — Demandes de Valeurs Foncières](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/) |
| **Period** | 2025 |
| **Format** | CSV delimited by `\|`, ~474 MB, 3.7 M rows |
| **Licence** | Licence Ouverte / Open Licence v2.0 (Etalab) |

Take the 2025 full-year file and keep the name it ships with.

## 2. Commune reference table

| | |
|---|---|
| **File name** | `table-appartenance-geo-communes-2026.xlsx` |
| **Source** | insee.fr — search *"Table d'appartenance géographique des communes"*, **2026 vintage** |
| **Format** | Excel, ~2.2 MB. The header is on **row 6**, which is why the loader passes `header=5` |
| **Columns used** | `CODGEO`, `LIBGEO`, `DEP`, `REG`, `EPCI`, `ZE2020` |

This is what maps each commune to its department, region, EPCI and 2020
employment zone — the join key for everything else.

## 3–5. INSEE local statistics

All three come from [statistiques-locales.insee.fr](https://statistiques-locales.insee.fr):
pick the geographic level, tick the indicators listed below, then export to CSV.
The export is `;`-delimited with **two banner rows above the header**, which is
why every loader passes `header=2`. Rename each export to the file name given.

### `Stats_Commune.csv` — level: *commune*

`Médiane du niveau de vie 2023` · `Logements 2022` ·
`Nb d'emplois au lieu de travail (LT) 2022` ·
`Évol. annuelle moy. de la population 2017 - 2023 (en %)` ·
`Évol. annuelle moy. de la pop. due au solde apparent entrées/sorties 2016-2022` ·
`Unités légales (en nombre) 2023` · `Créations d'entreprises (en nombre) 2025` ·
`Nombre d'établissements 2024` · `Effectifs salariés 2024` ·
`École maternelle, primaire, élémentaire (en nombre) 2024` ·
`Collège (en nombre) 2024` · `Lycée (en nombre) 2024` ·
`Pharmacie (en nombre) 2024` · `Médecin généraliste (en nombre) 2024`

### `Stats_Interco.csv` — level: *intercommunalité*

`Salaire net EQTP mensuel moyen 2023` · `Taux de pauvreté 2023`

### `Stats_Chomage.csv` — level: *zone d'emploi 2020*

`Taux de chômage trimestriel 2025-T4`

> The indicator years are part of the column names, so a different vintage will
> fail the `usecols` check in `src/data/load_data.py` rather than silently load
> the wrong data. Adjust the column lists there if you export another year.

## Directory layout

| Directory    | Content                                                        |
|--------------|----------------------------------------------------------------|
| `raw/`       | The five downloaded files, unmodified                          |
| `clean/`     | Typed and filtered Parquet — `dvf_clean`, `dvf_core`, 4 INSEE  |
| `cache/`     | `geocode_cache.json` — postal-code → coordinates, reused across runs |
| `processed/` | `dvf_processed.parquet` — enriched and clustered pipeline output |

## Volumes

| File | Format | Size |
|---|---|---|
| `raw/ValeursFoncieres-2025.txt` | CSV `\|` | ~474 MB |
| `raw/table-appartenance-geo-communes-2026.xlsx` | Excel | ~2.2 MB |
| `raw/Stats_Commune.csv` | CSV `;` | ~2.3 MB |
| `raw/Stats_Interco.csv` | CSV `;` | ~83 KB |
| `raw/Stats_Chomage.csv` | CSV `;` | ~7 KB |
| `clean/dvf_clean.parquet` | Parquet | ~11 MB |
| `processed/dvf_processed.parquet` | Parquet | ~17 MB |

## First run

The first run geocodes every distinct postal code against the
[Géoplateforme](https://data.geopf.fr/geocodage/search) API, rate-limited to 5
calls/second, and writes `cache/geocode_cache.json` as it goes. Later runs read
the cache and issue no requests. Budget for that on a cold start.
