# PLAN.md — Project Plan (Living Document)

> Update this file as tasks are completed. Check off subtasks, add notes on findings, and flag when an output from one task changes assumptions in another.

---

## Cross-Task Dependency Map

```
Task 1 (EDA)
  ├─→ Task 2: gap locations, ARIMA orders, stationarity findings, ARCH effects
  ├─→ Task 3: ARIMA orders, GARCH orders, seasonality, grouping
  └─→ Task 4: correlation structure, volatility regime, series characteristics

Task 2 (Interpolation)
  └─→ Task 4: complete series needed for full-history backtesting

Task 3 (Extrapolation)
  └─→ Task 4: 200-day forecasts used as basis for forward-looking strategy evaluation
```

---

## Task 1 — Data Analysis

**Goal:** Extract all statistically useful information from the 7 series. Work primarily with log-returns. Produce findings that directly inform modelling choices in Tasks 2–4.

### 1.1 Data Loading & Inspection
- [ ] Load `spiff data2.csv` via `utils.load_data()`
- [ ] Verify dimensions (5456 × 9), column names, index alignment
- [ ] Tabulate exact gap locations (rows and day numbers) for all series
- [ ] Identify the max=1000 rows for each series — how many, when, how long do they last?
- [ ] **Decision point:** Are the 1000-values spikes or level shifts? Document the decision on how to treat them

**Output:** `results/t1_gap_summary.csv`, `results/t1_price_extremes.csv`

### 1.2 Raw Price Visualisation
- [ ] Panel plot of all 7 price series (mark gap regions)
- [ ] Log-price series (same panel)
- [ ] Note visible trends, level shifts, regime changes

**Output:** `figures/t1_raw_prices.png`, `figures/t1_log_prices.png`

### 1.3 Log-Return Computation
- [ ] Compute $r_t = \log(P_t/P_{t-1})$, masking returns that straddle a gap
- [ ] Panel plot of all 7 return series
- [ ] Summary statistics table: mean, std, min, max, skewness, excess kurtosis

**Output:** `figures/t1_returns.png`, `results/t1_return_stats.csv`

### 1.4 Distributional Analysis
- [ ] Histogram + KDE for each series (overlay normal)
- [ ] QQ-plot vs. normal for each series
- [ ] Jarque-Bera normality test
- [ ] Document fat tails (excess kurtosis > 0) and asymmetry

**Output:** `figures/t1_histograms.png`, `figures/t1_qq_plots.png`, `results/t1_normality_tests.csv`

### 1.5 Stationarity Tests
- [ ] Augmented Dickey-Fuller (ADF) on log-prices → expect unit root (fail to reject H₀)
- [ ] ADF on log-returns → expect stationary (reject H₀)
- [ ] KPSS as confirmation
- [ ] If any return series is non-stationary, investigate and difference again

**Method:** ADF with automatic lag selection (AIC), constant + trend specification.  
$H_0$: unit root present. Reject at 5% → stationary.

**Output:** `results/t1_stationarity.csv`

### 1.6 Autocorrelation Analysis (ACF/PACF)
- [ ] ACF and PACF of log-returns for each series (lags 1–40)
- [ ] Ljung-Box test at lags 10, 20 — is there any serial correlation in returns?
- [ ] Note any series with significant ACF → will need ARMA mean equation
- [ ] Note seasonal spikes in ACF (multiples of 5, 7, 22?) → informs SARIMA in Tasks 2–3

**Output:** `figures/t1_acf_pacf.png`, `results/t1_ljung_box.csv`

### 1.7 ARCH / Volatility Effects
- [ ] ACF and PACF of **squared** returns $r_t^2$ for each series
- [ ] Ljung-Box test on $r_t^2$ — presence of ARCH effects?
- [ ] ARCH LM test
- [ ] Rolling 21-day standard deviation plot (volatility clustering visual)

**Output:** `figures/t1_squared_returns_acf.png`, `figures/t1_rolling_vol.png`, `results/t1_arch_tests.csv`

### 1.8 Seasonality Detection
- [ ] Periodogram (FFT-based) for each log-return series
- [ ] Identify dominant frequencies; convert to period in days
- [ ] If clear seasonal period $s$ found, flag for SARIMA in Tasks 2–3

**Output:** `figures/t1_periodogram.png`, `results/t1_spectral_peaks.csv`

### 1.9 Cross-Series Analysis
- [ ] Pairwise Pearson correlation matrix of returns (heatmap)
- [ ] Hierarchical clustering dendrogram (Ward linkage, correlation distance $d = 1-|\rho|$)
- [ ] Identify groups of co-moving series
- [ ] Cross-correlation plots (lead-lag up to ±10 lags) for pairs within groups
- [ ] Note any strong co-movements → relevant for portfolio construction in Task 4

**Output:** `figures/t1_correlation_heatmap.png`, `figures/t1_dendrogram.png`, `figures/t1_cross_correlations.png`

### 1.10 Summary & Insights for Downstream Tasks
- [ ] Written summary: which series are volatile, which are smooth, which cluster together
- [ ] Table of recommended ARIMA orders per series (based on ACF/PACF)
- [ ] Table of series flagged for GARCH (ARCH LM significant)
- [ ] Flag any series that may need SARIMA (seasonal component detected)

**Output:** `results/t1_model_recommendations.csv`

---

## Task 2 — Interpolation

**Goal:** Fill each 50-row internal gap with smoothed estimates and posterior uncertainty intervals. Use the Kalman smoother (state-space representation of ARIMA). Do not use post-gap data to select the model.

**Key constraint:** Model order selection must be done on pre-gap data only to avoid data leakage.

### 2.1 Per-Series ARIMA Order Selection (pre-gap data only)
- [ ] For each series: fit ARIMA on observations *before* the gap
- [ ] Select $(p, d, q)$ via AICC (search $p, q \in \{0,...,4\}$, $d \in \{0,1\}$)
- [ ] Confirm residuals pass Ljung-Box whiteness test
- [ ] Use findings from Task 1 (ACF/PACF) as starting point

### 2.2 State-Space Kalman Smoother
- [ ] Re-fit the selected ARIMA as a state-space model on the **full series** (including gap rows as `NaN`)
- [ ] `statsmodels.tsa.statespace.SARIMAX` handles missing values natively via the Kalman filter
- [ ] Extract smoothed state estimates $\hat{X}_t$ and posterior variances $P_t$ for gap rows

**Math:**  
State-space form of ARIMA$(p,d,q)$:
$$X_t = Z \alpha_t, \quad \alpha_{t+1} = T \alpha_t + R \eta_t$$
Kalman smoother computes $\mathbb{E}[\alpha_t | X_1,\ldots,X_n]$ and $\text{Var}[\alpha_t | X_1,\ldots,X_n]$ for all $t$, including missing ones.  
Prediction interval: $\hat{X}_t \pm 1.96 \sqrt{P_t}$

### 2.3 Uncertainty Estimation
- [ ] 95% posterior prediction interval for each imputed point
- [ ] Plot each series with gap region highlighted and filled (point estimate + shaded CI)

**Output:** `figures/t2_interpolation_<series>.png` (7 figures), `results/t2_interpolated.csv`

### 2.4 Evaluation (Pseudo-Gap Experiment)
- [ ] For each series: create an artificial 50-row gap in a fully observed region
- [ ] Run the same Kalman smoother procedure
- [ ] Compute MSE and MAD vs. true values
- [ ] Report coverage of 95% intervals (should be ~95%)

**Output:** `results/t2_evaluation.csv`

### 2.5 Cross-Series Check (optional enrichment)
- [ ] Since other series are observed during each gap, check if adding a contemporaneous regressor improves MSE
- [ ] Use SARIMAX with the most correlated series as exogenous variable
- [ ] Only adopt if it materially improves held-out MSE

---

## Task 3 — Extrapolation

**Goal:** Forecast all 7 series for 200 steps ahead (rows 5256–5455). Produce calibrated prediction intervals using parametric bootstrap. Be honest about uncertainty growth.

**Key constraint:** No data from the forecast horizon can inform model fitting. Use rows 1–5255 only.

### 3.1 Model Selection Per Series
- [ ] Use ARIMA orders from Task 1/2 as starting point
- [ ] Refit on full available data (rows 1–5255, with gaps filled from Task 2)
- [ ] Check for ARCH effects in residuals → if significant, add GARCH(1,1)
- [ ] For series with seasonal component: use SARIMA$(p,d,q)\times(P,D,Q)_s$

### 3.2 ARIMA-GARCH Fitting
- [ ] **Mean equation:** ARIMA$(p,d,q)$ fit via conditional MLE
- [ ] **Variance equation:** GARCH$(1,1)$ on residuals via `arch` library (conditional MLE, Method 4.2.1)
- [ ] Use Student-$t$ innovations if QQ plots from Task 1 show fat tails
- [ ] Residual diagnostics: standardised residuals $\hat{Z}_t = \hat{\epsilon}_t / \hat{\sigma}_t$ should be iid, mean 0, variance 1

**GARCH(1,1) model:**
$$r_t = \mu + \epsilon_t, \quad \epsilon_t = \sigma_t Z_t, \quad Z_t \sim \text{IID}(0,1)$$
$$\sigma_t^2 = \alpha_0 + \alpha_1 \epsilon_{t-1}^2 + \beta_1 \sigma_{t-1}^2$$
Stationarity condition: $\alpha_1 + \beta_1 < 1$

### 3.3 200-Step Forecasts
- [ ] Point forecast from ARIMA conditional mean recursion
- [ ] GARCH conditional variance forecast (converges to unconditional variance $\alpha_0/(1-\alpha_1-\beta_1)$)
- [ ] **Parametric bootstrap** (Method 5.4.1): 1000 simulated paths of length 200, using fitted model and re-sampled innovations
- [ ] Extract 68% and 95% prediction intervals from bootstrap distribution

### 3.4 Forecast Visualisation
- [ ] For each series: plot last 200 observed points + 200-step forecast + CI bands
- [ ] Show uncertainty widening with horizon

**Output:** `figures/t3_forecast_<series>.png`, `results/t3_forecasts.csv` (point + lower/upper bounds)

### 3.5 Evaluation (Pseudo-Holdout)
- [ ] Hold out last 200 observed days (rows 5056–5255) as pseudo-test set
- [ ] Fit model on rows 1–5055, forecast 200 steps, compare to held-out
- [ ] Metrics: MSE, MAD, MAPE (Method 5.4.3), directional accuracy (Method 5.4.2)
- [ ] Discuss: how does performance degrade with horizon length?

**Output:** `results/t3_evaluation.csv`

---

## Task 4 — Investment Strategies

**Goal:** Implement and compare several trading strategies on the Spiff markets. At least one must be a full-portfolio strategy (all 7 assets). Evaluate using Sharpe ratio (risk-free rate = 3% per year). Assess out-of-sample performance.

**Conventions:** Daily risk-free rate $r_f = 0.03/252$. Annualised Sharpe $= \sqrt{252} \cdot \bar{r}_{\text{excess}} / \hat{\sigma}_{\text{excess}}$. No transaction costs, infinite liquidity.

### 4.1 Data Preparation
- [ ] Reconstruct full price series: original data + Task 2 interpolations
- [ ] Use log-returns as trading signal input; simple returns for P&L
- [ ] Define train/test split: train on first 80% of available data, evaluate on last 20%

### 4.2 Strategy 1 — Buy and Hold (Baseline)
- [ ] Equal-weight portfolio, rebalanced daily to equal weights (or no rebalancing)
- [ ] Compute daily portfolio return, cumulative return, Sharpe ratio
- [ ] Serves as the passive benchmark

### 4.3 Strategy 2 — Momentum (Moving Average Crossover)
- [ ] Signal: long if 20-day MA > 60-day MA, else hold cash
- [ ] Applied per asset, then combined equal-weight
- [ ] **Pros:** Simple, captures trends. **Cons:** Lagging, whipsaws in flat markets
- [ ] Explain the math: MAs as low-pass filters on the return signal

### 4.4 Strategy 3 — Mean-Reversion
- [ ] Signal: long if $P_t < \mu_{60} - k \cdot \sigma_{60}$, short if $P_t > \mu_{60} + k \cdot \sigma_{60}$ (Bollinger bands, $k=1$)
- [ ] Applied per asset, combined equal-weight
- [ ] **Pros:** Works in range-bound markets. **Cons:** Fails in trending markets. Opposite of momentum
- [ ] Compare directly with Strategy 2: which regime does each Spiff series favour?

### 4.5 Strategy 4 — Minimum Variance Portfolio (Full Portfolio)
- [ ] Optimise $\min_w \, w^\top \hat{\Sigma} w$ subject to $\mathbf{1}^\top w = 1$, $w \geq 0$
- [ ] $\hat{\Sigma}$: rolling sample covariance matrix (252-day window), rebalance monthly
- [ ] **Pros:** No return forecast required — pure risk management. **Cons:** Sensitive to covariance estimation errors
- [ ] Use scipy.optimize or closed-form solution

**Output:** `results/t4_weights_minvar.csv`

### 4.6 Strategy 5 — Equal Risk Contribution (Risk Parity)
- [ ] Weight assets so each contributes equally to total portfolio variance
- [ ] $w_i \propto 1/\sigma_i$ (simple approximation)
- [ ] **Pros:** More diversified than min-variance. **Cons:** Ignores correlations in simple form

### 4.7 Evaluation
- [ ] Cumulative return plot for all strategies (same axes)
- [ ] Table: annualised return, annualised vol, Sharpe ratio, max drawdown
- [ ] Out-of-sample Sharpe ratio (test set only)
- [ ] Directional accuracy of signal-based strategies

**Output:** `figures/t4_cumulative_returns.png`, `figures/t4_drawdowns.png`, `results/t4_strategy_comparison.csv`

### 4.8 Expected Production Performance
- [ ] Rolling Sharpe ratio over time (detect regime sensitivity)
- [ ] Discuss: strategies fitted/tuned on training data — expected to degrade out-of-sample?
- [ ] Note: infinite liquidity + zero costs is unrealistic; discuss real-world adjustment

---

## Mathematical / Theory Outline

> This section outlines the content for the written theoretical report (Part 2). Full derivations go in a separate `theory/` document; brief summaries appear as markdown cells in each notebook.

### Log-returns
$$r_t = \log(P_t/P_{t-1}) \approx \frac{P_t - P_{t-1}}{P_{t-1}}$$
Why: removes non-stationarity from prices, approximately normally distributed, additively composes over time.

### ARMA$(p,q)$ — Brockwell & Davis Ch. 3
$$\phi(B) X_t = \theta(B) Z_t, \quad Z_t \sim \text{WN}(0, \sigma^2)$$
Causality: $\phi(z) \neq 0$ for $|z| \leq 1$. Invertibility: $\theta(z) \neq 0$ for $|z| \leq 1$.  
Estimation: conditional MLE. Order selection: AICC.

### SARIMA$(p,d,q)\times(P,D,Q)_s$
$$\phi(B)\Phi(B^s) \nabla^d \nabla_s^D X_t = \theta(B)\Theta(B^s) Z_t$$
Use when periodogram shows dominant frequency at period $s$.

### Augmented Dickey-Fuller Test
$H_0$: unit root ($\phi_1 = 1$). Test on $\Delta X_t = \phi_0^* + \phi_1^* X_{t-1} + \sum_{j=1}^k \gamma_j \Delta X_{t-j} + Z_t$.  
Non-standard distribution — use Dickey-Fuller critical values.

### GARCH$(1,1)$ — Tsay Ch. 3
$$\sigma_t^2 = \alpha_0 + \alpha_1 \epsilon_{t-1}^2 + \beta_1 \sigma_{t-1}^2$$
Unconditional variance: $\mathbb{E}[\sigma_t^2] = \alpha_0 / (1 - \alpha_1 - \beta_1)$.  
Kurtosis > 3 even with Gaussian $Z_t$ — explains fat tails in returns.

### Kalman Smoother (Interpolation)
State-space ARIMA; smoother computes $\mathbb{E}[\alpha_t | \mathbf{X}]$ and posterior variances for all $t$ including missing. Theoretically optimal linear interpolator.

### Parametric Bootstrap (Forecast Intervals)
Simulate $K = 1000$ paths of length $h$ from fitted model. Empirical quantiles give prediction intervals. Captures both parameter uncertainty (if refitted per path) and innovation uncertainty.

### Sharpe Ratio
$$\text{SR} = \frac{\mathbb{E}[r_t - r_f]}{\sqrt{\text{Var}(r_t - r_f)}} \cdot \sqrt{252}$$
Annualised. Higher is better. Sensitive to return distribution assumptions (penalises volatility regardless of sign).

---

## Status

| Task | Status | Notes |
|---|---|---|
| Task 1 | Not started | |
| Task 2 | Not started | Depends on Task 1 model recommendations |
| Task 3 | Not started | Depends on Task 1; can use Task 2 filled data |
| Task 4 | Not started | Depends on Tasks 2 & 3 for complete series |
