import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pandas as pd
from matplotlib.patches import Rectangle

PREVALENCE_CSV = "data/prevalence.csv"
OUTPUT_PDF = "data/figure2_prevalence.pdf"

BLUE, MAGENTA, ORANGE = "#005982", "#C91869", "#E97008"
PALETTE = [BLUE, MAGENTA, ORANGE]
INK = "#000000"
FS_YLABEL, FS_VALUE, FS_SWATCH, FS_AXIS = 8.0, 8.0, 7.3, 7.5
FW, FH = 7.9, 3.95
BAR_H, ROW_STEP, XMAX = 0.72, 1.0, 50.0
GAP_BAR, GAP_PLUS = 0.45, 1.15

# (bar label, [(codebook label, legend caption or None)])
BARS = [
    ("Disruption (RQ1)", [("Disruption", None)]),
    ("Asset Theft (RQ1)", [("Asset Theft", None)]),
    ("Safety Evasion (RQ1)", [("Safety Evasion", None)]),
    ("Private Info Access (RQ1)", [("Private Info Access", None)]),
    ("Mod Side-Effects (RQ1)", [("Mod Side-Effects", None)]),
    ("AC Effectiveness (RQ2)",
     [("AC Effective", "AC Effective"),
      ("AC Ineffective", "AC Ineffective"),
      ("Limited Platform Coverage", "Limited Platform Coverage")]),
    ("AC Tradeoffs (RQ2)",
     [("Loss of Useful Mods", "Loss of Useful Mods"),
      ("Performance Overhead", "Performance Overhead"),
      ("AC Privacy Concerns", "Privacy Concerns")]),
    ("User Recommendations (RQ2)", [("User Recommendations", None)]),
    ("AC Financial Motives (RQ2)", [("AC Financial Motives", None)]),
]


def stack_offsets(k):
    return [0.0] if k == 1 else ([0.16, -0.16] if k == 2 else [0.27, 0.0, -0.27])


def main():
    prevalence = pd.read_csv(PREVALENCE_CSV).set_index("label")["percent"]
    shown = {name for _, segs in BARS for name, _ in segs}
    missing = [name for name in prevalence.index if name not in shown]
    if missing:
        print(f"not shown in Figure 2: {', '.join(missing)}")

    n = len(BARS)
    fig = plt.figure(figsize=(FW, FH), dpi=160, facecolor="white")
    ax = fig.add_axes([0.330, 0.145, 0.330, 0.830])

    yticks, ylabels = [], []
    for i, (label, segs) in enumerate(BARS):
        y = (n - i) * ROW_STEP
        yticks.append(y)
        ylabels.append(label)
        x = 0.0
        for (name, _), color in zip(segs, PALETTE):
            ax.barh(y, prevalence[name], left=x, height=BAR_H, color=color,
                    edgecolor="white", linewidth=0.8, zorder=2)
            x += prevalence[name]
        if len(segs) == 1:
            ax.text(x + 0.6, y, f"{prevalence[segs[0][0]]:.1f}%", va="center",
                    ha="left", fontsize=FS_VALUE, color=INK)
        else:
            ax.text(x + GAP_BAR + 0.3, y, "+", va="center", ha="center",
                    fontsize=9, color=INK, clip_on=False, zorder=4)
            sx = x + GAP_BAR + GAP_PLUS
            for (name, caption), color, dy in zip(segs, PALETTE,
                                                  stack_offsets(len(segs))):
                ax.add_patch(Rectangle((sx, y + dy - 0.095), 0.70, 0.19,
                                       facecolor=color, edgecolor="none",
                                       clip_on=False, zorder=4))
                ax.text(sx + 1.05, y + dy, f"{caption} ({prevalence[name]:.1f}%)",
                        va="center", ha="left", fontsize=FS_SWATCH, color=INK,
                        clip_on=False, zorder=4)

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=FS_YLABEL)
    ax.set_ylim(0.4 * ROW_STEP, (n + 0.6) * ROW_STEP)
    ax.set_xlim(0, XMAX)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.tick_params(axis="x", length=3, width=0.8, labelsize=FS_AXIS, pad=2)
    ax.tick_params(axis="y", length=0, pad=4)
    ax.set_xlabel("Percentage of labeled posts (%)", fontsize=FS_YLABEL, labelpad=3)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_linewidth(1.0)

    fig.savefig(OUTPUT_PDF, facecolor="white", bbox_inches="tight", pad_inches=0.06)
    print(f"-> {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
