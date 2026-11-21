import argparse
from datetime import timedelta
from pathlib import Path

import numpy as np

import pandas as pd
import statsmodels.api as sm

from labeling_prompts import LABELS as CODEBOOK_LABELS


LABELED_PATH = Path("data/labeled_posts.csv")  # from multilabel_classifier.py
EVENTS_PATH = Path("events.csv")

WINDOW_DAYS = 14 # window around each event in +/- days
NW_LAG = 7 # Newey-West HAC lag (one week)
FDR_Q = 0.05 # BH-FDR threshold for significance
MIN_POSTS = 3 # skip an event-label pair with fewer posts than this in the window
EPS = 0.5 # Laplace smoothing for the fold change

LABELS = list(CODEBOOK_LABELS)  # the 13 codebook labels, single source of truth


def daily_counts(path):
    """Labeled posts -> counts per (label, subreddit, day)."""
    df = pd.read_csv(path, usecols=["subreddit", "post_date", "labels"])
    df["subreddit"] = df["subreddit"].astype(str).str.lower()
    df["date"] = df["post_date"].astype(str).str.slice(0, 10)
    df["labels"] = df["labels"].fillna("").astype(str).str.split(",")
    df = df.explode("labels")
    df["labels"] = df["labels"].str.strip()
    df = df[df["labels"].isin(LABELS)]
    counts = df.groupby(["labels", "subreddit", "date"]).size().to_dict()
    return counts, df["date"].max()


def window_counts(counts, label, scope, event_date, window):
    days = [(event_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(-window, window + 1)]
    return np.array([counts.get((label, scope, d), 0) for d in days], dtype=float)


def fit_its(y, window, hac_lag=NW_LAG):
    t = np.arange(len(y))
    post = (t >= window).astype(float)
    time_after = np.where(post == 1, t - window, 0.0)
    X = np.column_stack([np.ones(len(y)), t, post, time_after])
    res = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lag})
    return float(res.params[2]), float(res.pvalues[2])


def benjamini_hochberg(pvalues, q=FDR_Q):
    p = np.asarray(pvalues, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    crit = (np.arange(1, n + 1) / n) * q
    passing = ranked <= crit

    mask = np.zeros(n, dtype=bool)
    if passing.any():
        k = int(np.max(np.where(passing)[0]))
        mask[order[:k + 1]] = True

    q_sorted = np.minimum.accumulate(
        ranked[::-1] * n / np.arange(n, 0, -1)
    )[::-1]
    q_adj = np.empty(n)
    q_adj[order] = np.minimum(q_sorted, 1.0)
    return mask, q_adj


def run_pipeline(window=WINDOW_DAYS):
    counts, data_max = daily_counts(LABELED_PATH)
    events = pd.read_csv(EVENTS_PATH)

    rows = []
    for ev in events.itertuples():
        event_date = pd.Timestamp(str(ev.date)[:10])
        scope = str(ev.platform).lower()
        if (event_date + timedelta(days=window)).strftime("%Y-%m-%d") > data_max:
            continue
        for label in LABELS:
            y = window_counts(counts, label, scope, event_date, window)
            if y.sum() < MIN_POSTS:
                continue
            pre = float(y[:window].mean())
            post = float(y[window:].mean())
            level_coef, level_p = fit_its(y, window)
            rows.append({
                "event_id": ev.event_id,
                "event_title": ev.title,
                "event_date": event_date.date().isoformat(),
                "platform": scope,
                "label": label,
                "window_days": window,
                "pre_mean_per_day": pre,
                "post_mean_per_day": post,
                "fold": (post + EPS) / EPS if pre == 0 else post / pre,
                "fold_laplace": (post + EPS) / (pre + EPS),
                "level_coef": level_coef,
                "level_p": level_p,
            })

    rdf = pd.DataFrame(rows)
    if rdf.empty:
        print(f"No event-label pair reached {MIN_POSTS} posts in a +/-{window}-day window.")
        return rdf

    mask, q_adj = benjamini_hochberg(rdf["level_p"].values, q=FDR_Q)
    rdf["q_value_bh"] = q_adj
    rdf["significant_bh"] = mask
    rdf["significant"] = mask & ((rdf["level_coef"] >= 0) == (rdf["fold"] >= 1))
    rdf["direction"] = np.where(rdf["level_coef"] > 0, "increase", "decrease")

    out_cols = [
        "event_id", "event_title", "event_date", "platform", "label", "direction",
        "window_days", "pre_mean_per_day", "post_mean_per_day", "fold", "fold_laplace",
        "level_coef", "level_p", "q_value_bh", "significant_bh", "significant",
    ]
    rdf = rdf[out_cols].sort_values(["event_date", "label"]).reset_index(drop=True)
    rdf.to_csv(f"data/its_results_w{window}.csv", index=False)
    rdf[rdf["significant"]].to_csv(f"data/its_results_significant_w{window}.csv", index=False)

    sig = rdf[rdf["significant"]]
    print(f"{len(sig)}/{len(rdf)} tests significant at q<{FDR_Q} (window ±{window})\n")
    for ev_date, g in sig.groupby("event_date"):
        title = g["event_title"].iloc[0]
        n_inc = (g["direction"] == "increase").sum()
        n_dec = (g["direction"] == "decrease").sum()
        print(f"  {ev_date}  {title:55s}  +{n_inc} -{n_dec}")

    return rdf


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=WINDOW_DAYS, help="+/- days around each event")
    run_pipeline(ap.parse_args().window)
