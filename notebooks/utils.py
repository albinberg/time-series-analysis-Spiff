"""
utils.py — shared utilities for the TMS088/MSA410 time-series project.

Import at the top of every notebook:
    from utils import (load_data, get_gap_info, compute_log_returns,
                       set_plot_style, savefig, SERIES, TRAILING_N, SERIES_COLOURS)
"""

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# ── Constants ─────────────────────────────────────────────────────────────────
SERIES = ['gurkor', 'guitars', 'slingshots', 'stocks',
          'sugar', 'water', 'tranquillity']

ANOMALY_VALUE = 1000.0   # placeholder value in raw data → treated as NaN
TRAILING_N    = 200      # final N rows are the held-out test window

# One colour per series — used consistently across all notebooks
SERIES_COLOURS = {
    'gurkor':       '#1f77b4',
    'guitars':      '#ff7f0e',
    'slingshots':   '#2ca02c',
    'stocks':       '#d62728',
    'sugar':        '#9467bd',
    'water':        '#8c564b',
    'tranquillity': '#e377c2',
}


# ── Data loading ──────────────────────────────────────────────────────────────
def load_data(path: str) -> pd.DataFrame:
    """Load spiff_data2.csv and replace ANOMALY_VALUE with NaN.

    Five rows in the raw data have every series set to exactly 1000.0 —
    a systematic recording artefact.  These are replaced with NaN so they
    do not produce spurious log-returns.

    Parameters
    ----------
    path : str  Path to spiff_data2.csv.

    Returns
    -------
    pd.DataFrame
        Full dataset with anomalous values replaced by NaN.
        Gap and trailing NaN regions are preserved as-is.
    """
    df = pd.read_csv(path, index_col=0)
    df[SERIES] = df[SERIES].replace(ANOMALY_VALUE, np.nan)
    return df


# ── Gap detection ─────────────────────────────────────────────────────────────
def get_gap_info(df: pd.DataFrame) -> dict:
    """Characterise the embedded NaN gap and trailing missing window per series.

    The trailing window is the last TRAILING_N rows of *df*.  Pre-trailing NaN
    indices are grouped into contiguous runs; the longest run is the embedded
    gap (one 50-row block per series, staggered across series).  Isolated
    single-row NaN values (anomaly replacements) are captured in 'nan_runs'
    for shading but excluded from gap_start/gap_end/gap_len.

    Returns
    -------
    dict
        {series: {'gap_start': int|None, 'gap_end': int|None,
                  'gap_len': int, 'contiguous': bool,
                  'nan_runs': list[list[int]],
                  'trailing_start': int|None, 'trailing_len': int}}
    """
    n = len(df)
    trailing_start_label = df.index[n - TRAILING_N]

    result = {}
    for col in SERIES:
        nan_labels   = df.index[df[col].isna()].tolist()
        gap_labels   = [i for i in nan_labels if i <  trailing_start_label]
        trail_labels = [i for i in nan_labels if i >= trailing_start_label]

        # Group pre-trailing NaN indices into contiguous runs
        runs: list = []
        if gap_labels:
            run = [gap_labels[0]]
            for idx in gap_labels[1:]:
                if idx == run[-1] + 1:
                    run.append(idx)
                else:
                    runs.append(run)
                    run = [idx]
            runs.append(run)

        # Embedded gap = longest contiguous run (50 rows, series-specific position)
        if runs:
            emb = max(runs, key=len)
            result[col] = {
                'gap_start':      emb[0],
                'gap_end':        emb[-1],
                'gap_len':        len(emb),
                'contiguous':     True,
                'nan_runs':       runs,
                'trailing_start': trail_labels[0] if trail_labels else None,
                'trailing_len':   len(trail_labels),
            }
        else:
            result[col] = {
                'gap_start':      None,
                'gap_end':        None,
                'gap_len':        0,
                'contiguous':     True,
                'nan_runs':       [],
                'trailing_start': trail_labels[0] if trail_labels else None,
                'trailing_len':   len(trail_labels),
            }
    return result


# ── Log-returns ───────────────────────────────────────────────────────────────
def compute_log_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Compute log-returns r_t = log(P_t) - log(P_{t-1}) for each series.

    NaN gaps are preserved: the return immediately after each gap is NaN
    (because the preceding price is NaN), preventing spurious large returns
    at gap boundaries.

    Parameters
    ----------
    df : pd.DataFrame
        Price data (full dataset or any temporal subset).

    Returns
    -------
    pd.DataFrame
        Same index as *df*, with 'day' column (if present) and one return
        column per series.
    """
    log_prices = df[SERIES].apply(np.log)
    returns = log_prices.diff()
    if 'day' in df.columns:
        out = pd.DataFrame({'day': df['day'].values}, index=df.index)
        for col in SERIES:
            out[col] = returns[col].values
        return out
    return returns


# ── Plot style ────────────────────────────────────────────────────────────────
def set_plot_style() -> None:
    """Apply a consistent matplotlib style across all project notebooks.

    Call once at the top of each notebook, immediately after importing
    matplotlib/seaborn.
    """
    for style in ('seaborn-v0_8-whitegrid', 'seaborn-whitegrid'):
        try:
            plt.style.use(style)
            break
        except OSError:
            continue

    mpl.rcParams.update({
        'figure.dpi':        110,
        'axes.spines.top':   False,
        'axes.spines.right': False,
        'axes.grid':         True,
        'grid.alpha':        0.35,
        'grid.linestyle':    '--',
        'font.size':         11,
        'axes.titlesize':    12,
        'axes.labelsize':    11,
        'xtick.labelsize':   10,
        'ytick.labelsize':   10,
        'legend.fontsize':   10,
        'lines.linewidth':   1.2,
        'figure.figsize':    (14, 4),
    })


# ── Figure saving ─────────────────────────────────────────────────────────────
def savefig(fig, name: str, figures_dir: str = '../report/figures') -> None:
    """Save *fig* to *figures_dir*/<name> at 150 dpi.  Creates dir if needed."""
    os.makedirs(figures_dir, exist_ok=True)
    fig.savefig(os.path.join(figures_dir, name), dpi=150, bbox_inches='tight')
