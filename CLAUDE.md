# CLAUDE.md — Financial Time Series Analysis (TMS088/MSA410)

## Project Overview

Analysis of 7 financial price series from the planet Spiff. The goal is a complete time-series workflow: exploratory analysis, interpolation of internal gaps, forecasting of a 200-day horizon, and evaluation of trading strategies. The project is assessed in four equally weighted tasks (2 pts each).

---

## Data

**File:** `project files/spiff data2.csv`  
**Dimensions:** 5456 rows × 9 columns (`index`, `day`, + 7 series)  
**Series:** `gurkor`, `guitars`, `slingshots`, `stocks`, `sugar`, `water`, `tranquillity`  
**Valid observations:** 5206 per series

### Gap Locations

| Series | Internal gap (rows, 0-indexed) | Length |
|---|---|---|
| gurkor | 198–247 | 50 |
| guitars | 398–447 | 50 |
| slingshots | 598–647 | 50 |
| stocks | 798–847 | 50 |
| sugar | 998–1047 | 50 |
| water | 1198–1247 | 50 |
| tranquillity | 1398–1447 | 50 |
| **All series** | **5256–5455** | **200** |

Gaps are staggered: when one series has its internal gap, all others are observed. The final 200 rows are missing for every series simultaneously — this is the forecasting target.

**Anomaly:** Every series has a maximum value of exactly 1000. Investigate in Task 1 before modelling.

---

## Tasks

| # | Name | Goal |
|---|---|---|
| 1 | Data Analysis | Patterns, grouping, stationarity, ACF/PACF, ARCH effects, distributions |
| 2 | Interpolation | Fill 50-row internal gaps with uncertainty estimates (Kalman smoother) |
| 3 | Extrapolation | Forecast 200 end-points with uncertainty (ARIMA-GARCH + bootstrap) |
| 4 | Investment Strategies | Compare several strategies, evaluate with Sharpe ratio (rf = 3%) |

---

## Tech Stack

| Library | Purpose |
|---|---|
| `pandas`, `numpy` | Data loading, returns, wrangling |
| `statsmodels` | ARIMA, SARIMA, state-space / Kalman, ADF/KPSS tests, ACF/PACF |
| `arch` | GARCH/EGARCH fitting (conditional MLE) |
| `scipy` | Spectral analysis, statistical tests (Jarque-Bera, Ljung-Box) |
| `scikit-learn` | Hierarchical clustering, preprocessing |
| `matplotlib`, `seaborn` | All plots |
| `jupyter` | Notebooks |

---

## Repository Structure

```
time-series-analysis-Spiff/
├── CLAUDE.md              # this file
├── PLAN.md                # living task plan with subtask checklist
├── utils.py               # shared: data loading, log-returns, gap detection, plotting helpers
├── notebooks/
│   ├── task1_data_analysis.ipynb
│   ├── task2_interpolation.ipynb
│   ├── task3_extrapolation.ipynb
│   └── task4_strategies.ipynb
├── figures/               # all saved plots (gitignored if large)
├── results/               # saved model outputs, CSVs, fitted params
└── project files/
    ├── spiff data2.csv
    ├── Project Financial Timeseries 2526.pdf
    └── FTSlecturenotes.pdf
```

---

## Coding Conventions

- **One notebook per task.** Each notebook is self-contained and can be run in a fresh kernel by importing `utils.py`.
- **utils.py** holds: `load_data()`, `compute_log_returns()`, `get_gap_info()`, and any plotting helpers reused across notebooks.
- **Primary representation:** log-returns $r_t = \log(P_t / P_{t-1})$. Never compute a return across a gap boundary.
- **Figures:** Save every plot to `figures/` with a task prefix, e.g. `figures/t1_acf_gurkor.png`. Use `plt.savefig(..., dpi=150, bbox_inches='tight')`.
- **Results:** Save fitted model parameters, test statistics, and imputed/forecast values to `results/` as `.csv` or `.pkl`.
- **Math in notebooks:** Every analytical step has a markdown cell above it with the model definition, assumptions, and intuition in LaTeX. A separate `theory/` document (or `PLAN.md` sections) collects the full mathematical writeup.
- **Random seeds:** Set `np.random.seed(42)` at the top of any notebook using simulation/bootstrap.

---

## Key Pitfalls

| Risk | Guard |
|---|---|
| **Data leakage in interpolation** | Use only data available at the time — Kalman smoother uses the full series but is retrospective, which is valid for interpolation. Never use post-gap data to select the model (fit on pre-gap only, then smooth). |
| **Return computed across gap** | Mask the first return after every gap. Checked by `utils.get_gap_info()`. |
| **Look-ahead bias in backtesting** | All strategy signals use only information available at time $t$. Rolling parameter estimates must use expanding or fixed windows anchored before $t$. |
| **Overfitting ARIMA order** | For linear ARMA models the overfitting risk is low with AIC/BIC, but cap search at $p,q \leq 5$. |
| **Overfitting trading strategies** | Always evaluate strategies on a held-out period. Report out-of-sample Sharpe, not in-sample. |
| **Stationarity assumptions** | Run ADF and KPSS on log-returns before fitting any ARMA/GARCH. If non-stationary, difference again. |
| **The 1000 price cap** | Investigate before modelling. These will produce extreme log-return spikes. Decide explicitly whether to winsorize or model as-is. |

---

## Notation (Lang & Petersson / Tsay conventions)

| Symbol | Meaning |
|---|---|
| $P_t$ | Price at time $t$ |
| $r_t = \log(P_t/P_{t-1})$ | Log-return |
| $B$ | Backshift operator: $BX_t = X_{t-1}$ |
| $\nabla = 1-B$ | Difference operator |
| $\nabla_s = 1-B^s$ | Seasonal difference, period $s$ |
| $\gamma(h)$ | Autocovariance at lag $h$ |
| $\rho(h) = \gamma(h)/\gamma(0)$ | Autocorrelation |
| $\alpha(h)$ | Partial autocorrelation (PACF) |
| $Z_t \sim \text{WN}(0,\sigma^2)$ | White noise |
| $\sigma_t^2$ | Conditional variance (GARCH) |
| $\hat{X}_t$ | One-step-ahead forecast |
| AICC | Corrected AIC (preferred for order selection) |
