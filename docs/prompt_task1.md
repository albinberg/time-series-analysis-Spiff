# Task 1 — Data Analysis
**File:** `task1_data_analysis.ipynb`

## Goals
- Load and inspect the data; identify where the embedded gaps are in each series.
- Analyse patterns within each individual series (trends, seasonality, stationarity,
  autocorrelation, volatility clustering, etc.).
- Analyse relationships between series (correlation, cross-correlation, co-movement).
- Investigate whether series can be grouped.
- Work primarily with log-returns rather than price levels; explain why in a
  theory cell.
- Keep a critical mindset: document what you see AND what you are uncertain about.
- Produce clean, well-labelled plots for every finding.

## Guiding questions from the spec (not exhaustive)
- What patterns exist within individual series?
- What relationships exist between series?
- Can the series be grouped?

## Data notes
- `spiff_data2.csv` — 7 price series (gurkor, guitars, slingshots, stocks, sugar,
  water, tranquillity), 5456 rows.
- Each series has ONE embedded gap of missing data AND is missing its final 200
  data points.
