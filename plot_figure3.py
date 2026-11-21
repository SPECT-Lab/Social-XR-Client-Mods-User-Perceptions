import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

DATA_CSV = "results/regression_analysis/retained_associations_w{window}.csv"
OUTPUT_PDF = "data/figure3_window{window}.pdf"
GREY = "#EDEDED"

THEMES = ["Disruption", "Asset Theft", "Safety Evasion", "Private Info Access",
          "Mod Side-Effects", "AC Effective", "AC Ineffective",
          "Limited Platform Coverage", "Loss of Useful Mods",
          "Performance Overhead", "AC Privacy Concerns", "User Recommendations",
          "AC Financial Motives"]


def fold_label(value):
    if value >= 10:
        return f"{value:.0f}x"
    if value >= 1:
        return f"{value:.1f}x"
    return f"{value:.2f}x"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=int, default=14, choices=(7, 14, 30))
    w = parser.parse_args().window

    data = pd.read_csv(DATA_CSV.format(window=w))
    events = list(dict.fromkeys(data["figure_label"]))
    print(f"±{w}: {len(data)} retained associations across "
          f"{data['event_id'].nunique()} events")

    here = set(zip(data["event_id"], data["label"], data["platform"]))
    elsewhere = set()
    others = [v for v in (7, 14, 30) if v != w]
    for other in others:
        alt = pd.read_csv(DATA_CSV.format(window=other))
        elsewhere |= set(zip(alt["event_id"], alt["label"], alt["platform"]))
    robust = len(here & elsewhere)
    print(f"      {robust} of {len(here)} also retained at "
          f"{' or '.join(f'±{v}' for v in others)} days")

    grid = np.full((len(events), len(THEMES)), np.nan)
    cells = {}
    for _, row in data.iterrows():
        i, j = events.index(row["figure_label"]), THEMES.index(row["label"])
        grid[i, j] = row["fold_laplace"]
        cells[(i, j)] = (row["pre_mean_per_day"], row["post_mean_per_day"])

    fig, ax = plt.subplots(figsize=(0.80 * len(THEMES) + 3.4,
                                    0.46 * len(events) + 2.0))
    ax.imshow(np.ones_like(grid), cmap=matplotlib.colors.ListedColormap([GREY]),
              aspect="auto")
    norm = TwoSlopeNorm(vmin=-1.0, vcenter=0.0, vmax=3.0)
    im = ax.imshow(np.ma.masked_invalid(np.log10(grid)), cmap="PuOr_r", norm=norm,
                   aspect="auto")

    for (i, j), (pre, post) in cells.items():
        ax.text(j, i - 0.13, fold_label(grid[i, j]), ha="center", va="center",
                fontsize=7, fontweight="bold")
        ax.text(j, i + 0.22, f"{pre:.2g}→{post:.3g}", ha="center",
                va="center", fontsize=4.6, color="#333333")

    ax.set_xticks(range(len(THEMES)))
    ax.set_xticklabels(THEMES, rotation=40, ha="right", fontsize=7)
    ax.set_yticks(range(len(events)))
    ax.set_yticklabels(events, fontsize=7)
    ax.set_xticks(np.arange(len(THEMES) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(events) + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=1.6)
    ax.tick_params(which="both", length=0)
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)

    bar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.015, ticks=[-1, 0, 1, 2, 3])
    bar.ax.set_yticklabels(["0.1x", "1x", "10x", "100x", "1000x"])
    bar.set_label("Fold change in mean daily posts", fontsize=7)
    bar.ax.tick_params(labelsize=6)
    fig.tight_layout()
    out = OUTPUT_PDF.format(window=w)
    fig.savefig(out)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
