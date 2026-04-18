# Time Series Project — TMS088/MSA410

## Repo structure
- data/           → spiff_data2.csv
- docs/           → project PDF, lecture notes, per-task prompts
- notebooks/      → one notebook per task
- report/         → final LaTeX report

## Workflow rules
- Work one task at a time. Never begin the next task without explicit instruction.
- Start with the simplest working solution. Add complexity only if clearly needed.
- After completing a task: summarise assumptions made and flag anything that 
  may affect earlier or later tasks.

## Notebook structure (apply to every notebook)
1. Title cell (Markdown): task name and objective.
2. Theory (Markdown): full derivations in LaTeX. Explain all assumptions.
3. Implementation: each code cell preceded by a Markdown cell explaining what 
   and why.
4. Results & interpretation: critically interpret every output.
5. Conclusions & caveats: what worked, what didn't, open questions.

## Style conventions
### LaTeX in notebooks
- Inline math: $x_t$, $\mu$, $\sigma^2$
- Display math: $$\hat{y}_t = \mu + \sum_{i=1}^p \phi_i y_{t-i} + \varepsilon_t$$
- Define every symbol the first time it appears.
- State model assumptions explicitly (e.g. stationarity, normality of residuals).

### Code
- Python 3. Use pandas, numpy, matplotlib/seaborn, statsmodels, scipy.
- Random seeds pinned at the top of every notebook: np.random.seed(42)
- All plots: title, axis labels, legend, units where applicable.
- Functions over repeated code blocks.

### Markdown prose
- Write in clear academic English.
- Every modelling choice must be justified in prose — no silent assumptions.

## Notation standards (from FTSlecturenotes.pdf)

Match the notation used in the course notes exactly so the report aligns with
lecture material.

### Processes and data
| Concept | Notation |
|---|---|
| Stochastic process | $X = (X_t,\, t \in \mathbb{Z})$ |
| Observed realisation | lowercase: $(x_t,\, t = 1,\ldots,n)$ |
| Log-return at time $t$ | $r_t = \log(P_t) - \log(P_{t-1})$ |
| iid noise | $X \sim \text{IID}(\mu, \sigma^2)$ |
| White noise | $Z \sim \text{WN}(0, \sigma^2)$ |
| Innovation/noise process | $(Z_t,\, t \in \mathbb{Z})$ — always $Z$, not $\varepsilon$ |

### Moments and functions
| Concept | Notation |
|---|---|
| Expectation | $\mathbb{E}(X_t)$ — double-struck E |
| Variance / Covariance / Correlation | $\text{Var}(\cdot)$, $\text{Cov}(\cdot,\cdot)$, $\text{Cor}(\cdot,\cdot)$ — upright |
| Mean function | $\mu_X(t) := \mathbb{E}(X_t)$; stationary mean $\mu$ |
| Autocovariance function (ACVF) | $\gamma_X(h) := \text{Cov}(X_{t+h}, X_t)$ |
| Autocorrelation function (ACF) | $\rho_X(h) := \gamma_X(h)/\gamma_X(0)$ |
| Sample ACVF / ACF | $\hat{\gamma}(h)$, $\hat{\rho}(h)$ — hats on estimates |
| Sample mean | $\bar{X}_n := n^{-1}\sum_{t=1}^n X_t$ |
| Mean squared error | $\text{MSE}(Y,X) := \mathbb{E}((Y-X)^2)$ |

### Models
| Concept | Notation |
|---|---|
| AR parameters | $\phi_1, \phi_2, \ldots, \phi_p$ |
| MA parameters | $\theta_1, \theta_2, \ldots, \theta_q$ |
| AR(1) | $X_t - \phi_1 X_{t-1} = Z_t$ |
| MA(1) | $X_t = Z_t + \theta_1 Z_{t-1}$ |
| Classical decomposition | $X_t = m_t + s_t + Y_t$ (trend + seasonal + stationary) |
| Best linear predictor | $b_t^l(X^n)$ or $\hat{X}_{n+h}$ for one-step ahead |

### Formatting rules
- Definitions use $:=$ (e.g. $\gamma_X(h) := \text{Cov}(X_{t+h}, X_t)$).
- Fractions in display math use $n^{-1}$, not $\frac{1}{n}$, when inside sums.
- Transpose is $'$ (prime), not ${}^T$.
- Significance level: $\alpha \in (0,1)$; chi-squared quantile: $\chi^2_{1-\alpha,h}$.
- Ljung–Box statistic: $\lambda := n(n+2)\sum_{i=1}^h \frac{\hat{\rho}(i)^2}{n-i}$.
