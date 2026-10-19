"""
Part C - part-to-whole legality, and the pie-ranking experiment.

    python partC_shares.py             tests, draws the two stimuli, scores results if they exist
    python partC_shares.py --run       run the experiment on a REAL reader (about 3 minutes)

What this script does NOT do is make up a reader. pie_ranking_results.csv is
written only by --run, from a person's actual answers and a real stopwatch. If
the file is absent, the scoring section says so instead of inventing numbers.

Writes: pie_stimulus.png, bars_stimulus.png (300 dpi), partC_output.txt, and
(only after --run) pie_ranking_results.csv.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tslib
from tslib import PALETTE, style_defaults, save_fig
import w4common as w

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "pie_ranking_results.csv"
say = w.Tee(HERE / "partC_output.txt")


# ----------------------------------------------------------------- C.1 legality
def legality():
    say("=" * 74)
    say("C.1  THE THREE CONDITIONS, TESTED IN CODE (slide 32)")
    say("=" * 74)
    say("Condition 1: parts are exclusive.  2: the whole is meaningful.  3: the share is the question.")

    # ---- (a) the four touch_* columns -----------------------------------------
    c8 = pd.read_csv(w.DATA / "case08_channel_attrib.csv")
    cols = [c for c in c8.columns if c.startswith("touch_")]
    ex = tslib.exclusivity_check(c8, cols)
    say("")
    say("(a) the four touch_* columns of case08_channel_attrib.csv")
    say(f"    shares: {ex['shares_pct']}")
    say(f"    sum = {ex['sum_pct']}%   exclusive = {ex['exclusive']}   "
        f"customers in 2+ channels = {ex['n_multi']:,} of {ex['n']:,} ({ex['pct_multi']}%)")
    say("    1 exclusive parts ....... FAIL (shares sum to 131%, so a unit sits in several parts)")
    say("    2 meaningful whole ...... the whole is 'customers' - fine, but the parts are not slices of it")
    say("    3 share is the question . 'how many customers does each channel reach?' - that is four separate")
    say("                              percentages of the same 4,000, not one pie")
    say("    VERDICT: NOT a pie. A bar chart of reach per channel (each bar its own % of customers) is legal;")
    say("             a stacked bar or treemap is not, for the same reason as the pie.")

    # ---- (b) shares_eight --------------------------------------------------------
    sh = pd.read_csv(w.DATA / "shares_eight.csv")
    cat = w.clean_catalogue()["all"]
    one_parent = bool((cat.groupby("sku").subcategory.nunique() == 1).all())
    assert abs(sh.share_pct.sum() - 100) < 1e-6
    ranked = sh.sort_values("share_pct", ascending=False).reset_index(drop=True)
    gaps = ranked.share_pct.diff(-1).dropna()
    say("")
    say("(b) the eight rows of shares_eight.csv")
    say(f"    sum = {sh.share_pct.sum():.6f}  (assert abs(sum - 100) < 1e-6 passes)")
    say(f"    every SKU belongs to exactly one sub-category: {one_parent}")
    say(f"    the three middle slices are within {ranked.share_pct.iloc[2] - ranked.share_pct.iloc[4]:.1f} points "
        f"({', '.join(f'{r.slice} {r.share_pct}%' for r in ranked.iloc[2:5].itertuples())})")
    say("    1 exclusive parts ....... PASS   2 meaningful whole ... PASS (the eight are all the sub-categories,")
    say("    so the whole is the whole catalogue)   3 share is the question ... PARTLY: the real question is a")
    say("    ranking, and eight slices is twice the 4 +/- 1 chunks a reader holds.")
    say("    VERDICT: legal as a pie, but draw it as a sorted bar chart. Part C.2-C.3 tests exactly that.")

    # ---- (c) premium vs other, 2025Q4 -------------------------------------------
    c9 = pd.read_csv(w.DATA / "case09_premium_share.csv").set_index("quarter")
    q = c9.loc["2025Q4"]
    prem = q.premium_revenue_pkr_m / q.total_revenue_pkr_m * 100
    other = 100 - prem
    say("")
    say("(c) premium vs other revenue, case09, 2025Q4")
    say(f"    premium {q.premium_revenue_pkr_m:.1f} + other {q.total_revenue_pkr_m - q.premium_revenue_pkr_m:.1f} = "
        f"{q.total_revenue_pkr_m:.1f}  ->  {prem:.1f}% + {other:.1f}% = {prem + other:.1f}%")
    say("    1 exclusive parts ....... PASS (other is defined as total minus premium)")
    say("    2 meaningful whole ...... PASS for ONE quarter (all revenue in 2025Q4)")
    say("    3 share is the question . PASS only if the question is 'how much of this quarter is premium'.")
    first, last = c9.iloc[0], c9.iloc[-1]
    say(f"    It FAILS the moment the question is 'is premium growing?': the whole shrank "
        f"{first.total_revenue_pkr_m:,.0f} -> {last.total_revenue_pkr_m:,.0f} while premium moved "
        f"{first.premium_revenue_pkr_m:.0f} -> {last.premium_revenue_pkr_m:.0f}.")
    say("    VERDICT: a two-slice pie (or one stacked bar) is legal for the single quarter, and a bar is")
    say("             clearer; NEITHER may be used to show a change over time.")


# ------------------------------------------------------------------ stimuli
def draw_stimuli():
    style_defaults()
    sh = pd.read_csv(w.DATA / "shares_eight.csv")           # file order, not rank order
    tints = [PALETTE["series"][0], "#5B9FCB"] * 4

    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    ax.pie(sh.share_pct, labels=sh.slice, colors=tints, startangle=90, counterclock=False,
           wedgeprops=dict(edgecolor="white", linewidth=1.6), textprops=dict(fontsize=14, color=PALETTE["ink"]),
           labeldistance=1.08)
    ax.set_title("Which slice is largest? Put A-H in order, largest first", fontsize=11)
    save_fig(fig, HERE / "pie_stimulus.png",
             note="Synthetic data generated for CDB601220. Eight sub-categories, file order, no numbers on the chart.")
    plt.close(fig)

    ranked = sh.sort_values("share_pct")
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.barh(ranked.slice, ranked.share_pct, color=PALETTE["series"][0], height=0.7)
    ax.set_xlabel("Share of the eight-category total, %")
    ax.set_xlim(0, 28)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", labelsize=14)
    ax.set_title("The same eight, sorted. Put A-H in order, largest first", fontsize=11)
    save_fig(fig, HERE / "bars_stimulus.png",
             note="Synthetic data generated for CDB601220. Same eight shares, sorted, values not printed on the bars.")
    plt.close(fig)
    say("")
    say("saved pie_stimulus.png and bars_stimulus.png at 300 dpi")


# --------------------------------------------------------------- C.2 experiment
def run_experiment():
    if RESULTS.exists() and "--force" not in sys.argv:
        print(f"\n{RESULTS.name} already exists, so it will NOT be overwritten (it holds real results).")
        print("To record a different reader on purpose, add --force (the old file is kept as a .bak copy).")
        return
    if RESULTS.exists():
        RESULTS.replace(RESULTS.with_suffix(".csv.bak"))
    sh = pd.read_csv(w.DATA / "shares_eight.csv")
    print("\nPart C.2 - ranking experiment with ONE real reader.")
    print("1. Open pie_stimulus.png on a screen the reader can see, and do not show them bars_stimulus.png yet.")
    print("2. Tell them: 'say the letters A to H aloud, largest slice first'.")
    print("3. Press Enter when they start; press Enter again the moment they finish speaking.")
    print("4. Then type the letters in the order they said.  Repeat with bars_stimulus.png.\n")
    reader = input("Reader's first name (and anything relevant, e.g. 'Ayesha, first-year student'): ").strip()
    rows = []
    for stim, png in (("pie", "pie_stimulus.png"), ("bars", "bars_stimulus.png")):
        input(f"\n[{stim}] Show {png}. Press Enter when the reader STARTS speaking...")
        t0 = time.perf_counter()
        input("      ...press Enter the moment they FINISH...")
        secs = time.perf_counter() - t0
        while True:
            order = input("      Type the letters they said, largest first (e.g. ABCDEFGH): ").strip().upper().replace(" ", "")
            if sorted(order) == list("ABCDEFGH"):
                break
            print("      Need each of A-H exactly once - try again.")
        rows.append({"reader": reader, "stimulus": stim, "order": order, "seconds": round(secs, 2)})
    pd.DataFrame(rows).to_csv(RESULTS, index=False)
    print(f"\nsaved {RESULTS.name}. Now run: python partC_shares.py   to score it.")


# ------------------------------------------------------------------ C.3 scoring
def load_results():
    """Read pie_ranking_results.csv as the reader's data. Header spelling and the way the order was typed
    ('ABCHGDEF', 'A B C H G D E F', 'a,b,c...') are normalised; nothing is ever filled in or corrected."""
    raw = pd.read_csv(RESULTS)
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    alias = {"participant": "reader", "name": "reader", "time": "seconds", "secs": "seconds", "time_s": "seconds",
             "response": "order", "ranking": "order", "rank_order": "order", "chart": "stimulus",
             "condition": "stimulus"}
    raw = raw.rename(columns={k: v for k, v in alias.items() if k in raw.columns and v not in raw.columns})
    missing = {"reader", "stimulus", "order", "seconds"} - set(raw.columns)
    if missing:
        return None, f"columns missing from {RESULTS.name}: {sorted(missing)} (found {list(raw.columns)})"
    raw["order"] = raw.order.astype(str).str.upper().str.replace(r"[^A-H]", "", regex=True)
    st = raw.stimulus.astype(str).str.lower()
    raw["stimulus"] = np.where(st.str.contains("pie"), "pie", np.where(st.str.contains("bar"), "bars", st))
    bad = raw[raw.order.map(lambda o: sorted(o) != list("ABCDEFGH"))]
    if len(bad):
        return None, (f"{len(bad)} row(s) do not contain each of A-H exactly once "
                      f"(row numbers {list(bad.index + 2)} counting the header as 1); fix the file, not the scorer")
    return raw, None


def score():
    sh = pd.read_csv(w.DATA / "shares_eight.csv")
    truth = "".join(sh.sort_values("share_pct", ascending=False).slice)
    say("")
    say("=" * 74)
    say("C.2 / C.3  THE EXPERIMENT AND ITS SCORE")
    say("=" * 74)
    say(f"True order, largest first: {truth}  "
        f"({', '.join(f'{r.slice} {r.share_pct}%' for r in sh.sort_values('share_pct', ascending=False).itertuples())})")
    if not RESULTS.exists():
        say("pie_ranking_results.csv does not exist yet: the experiment has not been run on a reader.")
        say("Run  python partC_shares.py --run  (python3 on Mac/Linux) with a real person, then run this script again.")
        return
    res, err = load_results()
    if err:
        say(f"COULD NOT SCORE: {err}")
        return
    readers = list(dict.fromkeys(res.reader))
    mid = {3, 4, 5}
    for rd in readers:
        g = res[res.reader == rd]
        have = set(g.stimulus)
        say(f"Reader: {rd}")
        if not {"pie", "bars"} <= have:
            say(f"  needs one 'pie' row and one 'bars' row; found {sorted(have)} - not scored")
            continue
        wrong_pos = {}
        for r in g.itertuples():
            pos = [i + 1 for i, (a, b) in enumerate(zip(r.order, truth)) if a != b]
            wrong_pos[r.stimulus] = pos
            top2_ok = r.order[:2] == truth[:2]
            bottom_ok = r.order[-1] == truth[-1]
            say(f"  {r.stimulus:4s} said {r.order}   {float(r.seconds):>6.1f} s   letters in the wrong rank: {len(pos)}"
                f"   wrong ranks: {pos if pos else 'none'}   top two right: {top2_ok}   bottom right: {bottom_ok}")
        pie, bars = g[g.stimulus == "pie"].iloc[0], g[g.stimulus == "bars"].iloc[0]
        say("")
        say("Where did the errors fall? The deck predicts: top two and the bottom one right, the middle (C 15.0%,")
        say("H 13.1%, G 11.2%, ranks 3-5) disputed.")
        for name, pos in wrong_pos.items():
            if not pos:
                say(f"  {name}: no errors, so the prediction cannot be tested on this stimulus.")
            else:
                inside = [x for x in pos if x in mid]
                say(f"  {name}: {len(inside)} of {len(pos)} wrong ranks are in the predicted middle (ranks 3-5); "
                    f"outside it: {[x for x in pos if x not in mid] or 'none'}.")
        say("")
        say(f"Time: pie {float(pie.seconds):.1f} s, bars {float(bars.seconds):.1f} s "
            f"({'bars faster' if float(bars.seconds) < float(pie.seconds) else 'pie faster or equal'}, "
            f"{abs(float(pie.seconds) - float(bars.seconds)):.1f} s apart).")
        say("")
    if len(readers) == 1:
        say("What one reader can and cannot support: this is a single person, tested once on each chart, always pie")
        say("first and bars second. The bars may be faster partly because the reader had just seen the same eight")
        say("letters (a practice effect I could not counterbalance with one reader), and one person's speed and errors")
        say("carry no information about how much they vary between people. It can illustrate the deck's claim; it")
        say("cannot confirm it, and it does not measure how large any pie-versus-bar difference is.")
    else:
        say(f"What {len(readers)} readers can and cannot support: a handful of people is still an illustration, not a")
        say("test. If every reader saw the pie first, the bars may be faster partly from practice on the same eight")
        say("letters, and the numbers do not measure how large any pie-versus-bar difference is.")


def main():
    if "--run" in sys.argv:
        draw_stimuli()
        run_experiment()
        return
    legality()
    draw_stimuli()
    score()
    say("")
    say("C.4  MY RULE. I will draw a pie only when there are two to four exclusive parts of a whole the reader "
        "cares about and the question is 'how much of the whole is this one part'; for a ranking, for five or "
        "more parts, or for anything that changes over time, I will draw sorted bars.")
    say.close()


if __name__ == "__main__":
    main()
