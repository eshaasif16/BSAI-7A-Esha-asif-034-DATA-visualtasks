

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next(p for p in (HERE, os.path.dirname(HERE))
            if os.path.exists(os.path.join(p, "vizlib.py")))
sys.path.insert(0, ROOT)
from vizlib import PALETTE, save_fig, style_defaults   # noqa: E402
import pandas as pd                                      # noqa: E402
import seaborn as sns                                    # noqa: E402

style_defaults()
RESULTS = os.path.join(ROOT, "popout_results.csv")      # YOU fill this in
ORDER_SHEET = os.path.join(ROOT, "popout_order_sheet.csv")
N_PEOPLE = 5
PANEL_NAMES = {1: "1 No channel", 2: "2 Colour", 3: "3 Size only", 4: "4 Colour + shape"}

ROWS, COLS = 12, 18
TARGET = "3"
N_TARGETS = 9
SEED = 1947


def make_grid(seed=SEED):
    """A grid of digits with exactly N_TARGETS threes, in fixed positions."""
    rng = np.random.default_rng(seed)
    others = [d for d in "0123456789" if d != TARGET]
    grid = np.array([[rng.choice(others) for _ in range(COLS)]
                     for _ in range(ROWS)], dtype=object)
    flat = rng.choice(ROWS * COLS, size=N_TARGETS, replace=False)
    for k in flat:
        grid[k // COLS, k % COLS] = TARGET
    return grid


def draw(ax, grid, title, colour=False, size=False, shape=False):
    """
    Draw one panel.

    colour -> targets get the highlight hue   (a preattentive channel)
    size   -> targets are drawn larger        (another one)
    shape  -> targets get a ring behind them  (a third, and it survives
              greyscale printing and colour blindness)
    """
    ax.set_xlim(-0.5, COLS - 0.5)
    ax.set_ylim(-0.5, ROWS - 0.5)
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_title(title, fontsize=10.5, loc="left")
    for r in range(ROWS):
        for c in range(COLS):
            d = grid[r, c]
            hit = d == TARGET
            if shape and hit:
                ax.add_patch(plt.Circle((c, r), 0.40, fill=False,
                                        edgecolor=PALETTE["ink"], lw=1.6))
            ax.text(c, r, d, ha="center", va="center",
                    fontsize=15 if (size and hit) else 11,
                    fontweight="bold" if (size and hit) else "normal",
                    color=PALETTE["highlight"] if (colour and hit)
                    else PALETTE["ink"])


def main():
    grid = make_grid()
    fig, ax = plt.subplots(2, 2, figsize=(13.0, 8.0))

    # ---- panel 1: no pop-out. Serial search — you read every cell.
    draw(ax[0, 0], grid, "1. No channel — you have to read every cell")

    # ---- panel 2: colour. One preattentive channel; the 3s appear at once.
    draw(ax[0, 1], grid, "2. Colour — the targets appear before you look",
         colour=True)

    # ------------------------------------------------------------- TODO 1
    # Panel 3: make the targets pop out using SIZE ONLY — no colour.
    # Then answer: is size as fast as colour? Wilke ch. 20 says it is not.
    # Time yourself and find out.
    draw(ax[1, 0], grid, "3. Size only - the targets are bigger, no colour", size=True)

    # ------------------------------------------------------------- TODO 2
    # Panel 4: redundant coding — TWO channels at once (colour AND shape).
    # This is the Week 2 accessibility rule in its original perceptual form:
    # a reader with deuteranopia loses panel 2 entirely and keeps panel 4.
    draw(ax[1, 1], grid, "4. Colour AND shape together - redundant coding",
         colour=True, shape=True)

    fig.suptitle(f"Count the {TARGET}s. Same {N_TARGETS} targets in all four "
                 f"panels, same positions.",
                 x=0.006, ha="left", fontsize=13.5, fontweight="bold",
                 color=PALETTE["ink"])
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out = save_fig(fig, os.path.join(ROOT, "popout_panels.png"),
                   f"{ROWS}x{COLS} grid, {N_TARGETS} targets, seed {SEED}. "
                   f"Week 1 activity, rebuilt in Matplotlib.")
    plt.close(fig)
    print("wrote", out)

    run_experiment()


def make_order_sheet():
    """A different random panel order for each person (seeded, so you can say how)."""
    rng = np.random.default_rng(SEED)
    rows = [{"participant": f"P{i+1}", "order": " -> ".join(str(k) for k in rng.permutation([1, 2, 3, 4]) )}
            for i in range(N_PEOPLE)]
    pd.DataFrame(rows).to_csv(ORDER_SHEET, index=False)
    return pd.DataFrame(rows)


def run_experiment():
    sheet = make_order_sheet()
    print("\nRandomised show-order for each classmate (also saved to popout_order_sheet.csv):")
    print(sheet.to_string(index=False))

    # >>> YOUR TURN - this is the part that needs real people, so it is left for you.
    # >>> 1. Open popout_panels.png (it was just saved) full screen.
    # >>> 2. For each classmate, show them ONE panel at a time in THEIR order above.
    # >>>    Time how long (seconds, stopwatch/phone) until they say how many 3s there are.
    # >>> 3. Create popout_results.csv next to this script with exactly these columns:
    # >>>        participant,panel,seconds,correct
    # >>>        P1,1,41.2,1        (panel = 1,2,3 or 4;  correct = 1 if they said 9, else 0)
    # >>>    That is 5 people x 4 panels = 20 rows.
    # >>> 4. Run this script again. It will draw popout_results.png.
    if not os.path.exists(RESULTS):
        print("\npopout_results.csv not found - collect the timings first (see the "
              "instructions above), then re-run.")
        return

    df = pd.read_csv(RESULTS)
    assert set(df.panel) == {1, 2, 3, 4}, "need panels 1-4"
    df["label"] = df.panel.map(PANEL_NAMES)
    means = df.groupby("panel").seconds.mean()
    fastest, slowest = means.idxmin(), means.idxmax()
    n = df.participant.nunique()
    wrong = int((df.correct == 0).sum())

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    order = [PANEL_NAMES[k] for k in (1, 2, 3, 4)]
    sns.barplot(data=df, x="label", y="seconds", order=order, estimator="mean",
                errorbar=None, color=PALETTE["series"][0], alpha=0.30, ax=ax)
    sns.stripplot(data=df, x="label", y="seconds", order=order, color=PALETTE["ink"],
                  size=7, jitter=0.12, ax=ax)
    ax.set_ylim(bottom=0)                                   # a bar chart of a magnitude
    ax.set_xlabel("")
    ax.set_ylabel("Seconds to count the 3s")
    ax.set_title(f"{PANEL_NAMES[fastest][2:]} was fastest ({means[fastest]:.1f} s); "
                 f"{PANEL_NAMES[slowest][2:]} was slowest ({means[slowest]:.1f} s)",
                 fontsize=12)
    note = (f"n = {n} classmates, each timed on all 4 panels. Panel order randomised per person "
            f"with numpy default_rng(seed {SEED}). Bars = mean, dots = individual times. "
            f"{wrong} wrong count(s).")
    out = save_fig(fig, os.path.join(ROOT, "popout_results.png"), note)
    plt.close(fig)
    print("\nwrote", out)
    print("\nMeans (s):", means.round(2).to_dict())
    print("\n>>> YOUR TURN: write your three sentences (fastest, slowest, did redundant "
          "coding (panel 4) cost speed vs panel 2?). If your results disagree with the "
          "textbook, say so honestly - that scores full marks.")


if __name__ == "__main__":
    main()
