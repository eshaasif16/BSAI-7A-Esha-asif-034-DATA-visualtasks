

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next(p for p in (HERE, os.path.dirname(HERE))
            if os.path.exists(os.path.join(p, "vizlib.py")))
sys.path.insert(0, ROOT)
from vizlib import (PALETTE, save_fig, simulate_cvd, style_defaults,   # noqa: E402
                    verdict, worst_pair)

style_defaults()

# ----------------------------------------------------------------- TODO 1
# Replace this with a palette you actually like the look of — matplotlib's
# tab10 first four, Excel's defaults, something from a dashboard you admire.
# Do not pick one you already know is safe; the point is to find out.
# >>> YOUR TURN: this is tab10 (the starter's default). The brief says to pick a
# >>> palette YOU like the look of. If you keep tab10, say so in your write-up;
# >>> if you swap it (Excel defaults, a dashboard palette), change both lines.
MY_PALETTE = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728"]   # matplotlib tab10
MY_LABEL = "matplotlib tab10, first four"

COURSE_PALETTE = PALETTE["series"] + [PALETTE["series_4th"]]
KINDS = ["normal", "deutan", "protan", "tritan"]


def swatch_sheet(palettes, path):
    fig, axes = plt.subplots(len(palettes), len(KINDS),
                             figsize=(3.0 * len(KINDS), 2.1 * len(palettes)))
    if len(palettes) == 1:
        axes = axes.reshape(1, -1)
    for row, (pal, label) in enumerate(palettes):
        for col, kind in enumerate(KINDS):
            ax = axes[row, col]
            shown = pal if kind == "normal" else simulate_cvd(pal, kind)
            for i, hexc in enumerate(shown):
                ax.add_patch(plt.Rectangle((i, 0), 0.92, 1, color=hexc))
                ax.text(i + 0.46, -0.22, f"S{i+1}", ha="center", fontsize=8,
                        color=PALETTE["ink_soft"])
            ax.set_xlim(-0.1, len(pal))
            ax.set_ylim(-0.4, 1.1)
            ax.axis("off")
            ax.set_title(kind, fontsize=10)
        axes[row, 0].text(-0.05, 1.42, label, transform=axes[row, 0].transAxes,
                          fontsize=11, fontweight="bold", color=PALETTE["ink"])
    fig.suptitle("Prove it, do not claim it", x=0.006, ha="left",
                 fontsize=13, fontweight="bold", color=PALETTE["ink"])
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    out = save_fig(fig, path,
                   "Machado, Oliveira & Fernandes (2009) severity-1.0 "
                   "matrices, applied in linear RGB.")
    plt.close(fig)
    return out


def audit(pal, label):
    """
    The numbers, not the impression.

    `vizlib.worst_pair` measures every pair in OKLab, which is near-uniform,
    so a single threshold means the same thing for every hue. The thresholds
    are documented on `vizlib.delta_e`.
    """
    print(label)
    rows = []
    for kind in ["normal", "deutan", "protan", "tritan"]:
        i, j, a, b, d = worst_pair(pal, kind)
        rows.append((kind, i, j, a, b, d))
        print(f"  {kind:7s} closest pair  S{i} {a} vs S{j} {b}"
              f"   ΔE {d:5.1f}   {verdict(d)}")
    print()
    return rows


def main():
    out = swatch_sheet([(MY_PALETTE, MY_LABEL),
                        (COURSE_PALETTE, "The course palette")],
                       os.path.join(ROOT, "partC_palette.png"))
    print("wrote", out, "\n")

    audit(MY_PALETTE, MY_LABEL)
    audit(COURSE_PALETTE, "The course palette (3 slots + the 4th)")

    # ---- Q3: worst pair in each palette, in each vision type ---------------
    print("Q3 - worst pair per palette (every pair compared)")
    for label, pal in [(MY_LABEL, MY_PALETTE), ("course 3 slots", PALETTE["series"]),
                       ("course + 4th slot", COURSE_PALETTE)]:
        for kind in ["normal", "deutan", "protan", "tritan"]:
            i, j, a, b, d = worst_pair(pal, kind)
            print(f"  {label:26s} {kind:7s} S{i}/S{j}  dE {d:5.1f}  {verdict(d)}")
    print()

    # ---- Q4: the rule --------------------------------------------------------
    print("Q4 - my rule for charts with more than three categories:")
    print("  Never add a fourth colour. Keep the three safe hues, and carry the "
          "extra category with a second channel:\n  a marker shape (vizlib.MARKERS), "
          "a direct label on the line/bar, or small multiples (facet) / a table.\n"
          "  The 4th slot (#CC79A7) is only legal WITH direct labels or a table view.")

    # ---- Bonus (2 marks): simulate deuteranopia on the exported Part D figure
    fig_path = os.path.join(ROOT, "partD_figure.png")
    if os.path.exists(fig_path):
        import matplotlib.image as mpimg
        img = mpimg.imread(fig_path)
        sim = simulate_cvd(img[..., :3], "deutan")
        fig, ax = plt.subplots(1, 2, figsize=(14, 4.6))
        ax[0].imshow(img)
        ax[0].set_title("Original")
        ax[1].imshow(sim)
        ax[1].set_title("Deuteranopia simulation")
        for a in ax:
            a.axis("off")
        out = save_fig(fig, os.path.join(ROOT, "partC_figure_deutan.png"),
                       "Machado et al. (2009), severity 1.0, linear RGB.")
        plt.close(fig)
        print("\nwrote", out)


if __name__ == "__main__":
    main()
