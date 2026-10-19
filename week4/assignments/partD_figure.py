"""
Part D - the e-commerce review figure (2 x 2, exported at 300 dpi).

    python3 partD_figure.py

Writes partD_figure.png, partD_appendix_28day.png, partD_output.txt and
partD_numbers.json (the numbers Part E quotes) next to this file.

Decisions made BEFORE any plot was drawn, and not revisited afterwards:
  * the smoothing window is 7 days (the weekend rhythm is the cycle to cancel,
    Part B.1) and it is centred (a retrospective Monday review, Part B.4);
  * the series is drawn from its first recorded day, no start date selected.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import squarify
from matplotlib.patches import Patch, Rectangle

import tslib
from tslib import PALETTE, style_defaults, save_fig
import w4common as w

HERE = Path(__file__).resolve().parent
WINDOW = 7            # fixed in advance - see the docstring
OUT_PNG = HERE / "partD_figure.png"
OUT_APPX = HERE / "partD_appendix_28day.png"


class Tee:
    """Print to the screen and to partD_output.txt at the same time."""
    def __init__(self, path):
        self.buf = io.StringIO()
        self.path = path

    def __call__(self, *a):
        line = " ".join(str(x) for x in a)
        print(line)
        self.buf.write(line + "\n")

    def close(self):
        Path(self.path).write_text(self.buf.getvalue(), encoding="utf-8")


say = Tee(HERE / "partD_output.txt")


# ------------------------------------------------------------------ helpers
def tint(hex_colour: str, amount: float) -> tuple:
    """Mix a colour with white. amount=0 is the colour, 1 is white."""
    rgb = np.array(matplotlib.colors.to_rgb(hex_colour))
    return tuple(rgb + (1 - rgb) * amount)


def text_colour_on(rgb) -> str:
    """White or ink, whichever has the higher contrast on this fill."""
    def lum(c):
        c = np.array(c[:3])
        c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    ink = matplotlib.colors.to_rgb(PALETTE["ink"])
    l = lum(rgb)
    contrast_white = 1.05 / (l + 0.05)
    contrast_ink = (l + 0.05) / (lum(ink) + 0.05)
    return "white" if contrast_white >= contrast_ink else PALETTE["ink"]


# parent category -> hue. Three course hues plus the fourth slot; the fourth
# fails the 3:1 contrast and CVD margins on its own, so every block carries a
# printed label (vizlib's rule for #CC79A7).
PARENT_HUE = {
    "Mobile": PALETTE["series"][0],
    "Audio & Imaging": PALETTE["series"][1],
    "Computing": PALETTE["series"][2],
    "Lifestyle": PALETTE["series_4th"],
}


def nested_treemap(ax, tree: pd.DataFrame, value: str, W=160.0, H=100.0):
    """
    category -> sub-category treemap. One hue per parent; sub-categories are
    lighter tints of it, biggest darkest. Area is proportional to value at BOTH
    levels (no header strips eating into the children).
    """
    parents = (tree.groupby("category")[value].sum().sort_values(ascending=False))
    total = parents.sum()
    p_rects = squarify.squarify(squarify.normalize_sizes(parents.values, W, H),
                                0, 0, W, H)
    small = []
    for (cat, ptotal), pr in zip(parents.items(), p_rects):
        kids = (tree[tree.category == cat].groupby("subcategory")[value].sum()
                .sort_values(ascending=False))
        k_rects = squarify.squarify(
            squarify.normalize_sizes(kids.values, pr["dx"], pr["dy"]),
            pr["x"], pr["y"], pr["dx"], pr["dy"])
        for j, ((sub, v), kr) in enumerate(zip(kids.items(), k_rects)):
            fill = tint(PARENT_HUE[cat], 0.0 + 0.20 * j)
            ax.add_patch(Rectangle((kr["x"], kr["y"]), kr["dx"], kr["dy"],
                                   facecolor=fill, edgecolor="white", linewidth=1.0))
            share = v / total * 100
            label = f"{sub}\n{v:,.0f}  ({share:.1f}%)"
            if kr["dx"] >= 17 and kr["dy"] >= 11:
                ax.text(kr["x"] + kr["dx"] / 2, kr["y"] + kr["dy"] / 2 + 2.5, label,
                        ha="center", va="center", fontsize=8.5,
                        color=text_colour_on(fill), linespacing=1.3)
            elif kr["dx"] >= 9 and kr["dy"] >= 8:
                ax.text(kr["x"] + kr["dx"] / 2, kr["y"] + kr["dy"] / 2 + 2.0,
                        f"{sub}\n{v:,.0f}", ha="center", va="center", fontsize=6.8,
                        color=text_colour_on(fill), linespacing=1.25)
            else:
                small.append(f"{sub} {v:,.0f}")
        # thick white border round the parent so the grouping reads first
        ax.add_patch(Rectangle((pr["x"], pr["y"]), pr["dx"], pr["dy"], fill=False,
                               edgecolor="white", linewidth=3.2))
        first = tint(PARENT_HUE[cat], 0.0)
        ax.text(pr["x"] + 1.4, pr["y"] + 1.6,
                f"{cat.upper()}  {ptotal:,.0f}  ({ptotal / total * 100:.0f}%)",
                ha="left", va="top", fontsize=7.6, fontweight="bold",
                color=text_colour_on(first))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.invert_yaxis()
    ax.axis("off")
    return small


# ===================================================================== main
def main():
    style_defaults()
    cl = w.clean_sessions()
    hourly, daily, log = cl["hourly"], cl["daily"], cl["log"]
    cat = w.clean_catalogue()
    clog = cat["log"]

    say("=" * 74)
    say("PART D - data audit, in the order the brief says to run it")
    say("=" * 74)
    raw = pd.read_csv(w.DATA / "sessions_hourly.csv")
    say("df.info()")
    _buf = io.StringIO()
    raw.info(buf=_buf)
    say(_buf.getvalue().rstrip())
    say("")
    say("df.describe().T")
    say(raw.describe().T.to_string())
    say("")
    say(f"df.shape                          {raw.shape}")
    say(f"df.ts.head(10)                    {raw.ts.head(10).tolist()}")
    say(f"device value_counts (raw)         {log['device_raw']}")
    say(f"sessions min / max (raw)          {raw.sessions.min()} / {raw.sessions.max()}")
    say("")
    say("The six faults and the rule applied to each")
    say("-" * 74)
    say(f"1. TWO TIMESTAMP FORMATS. {log['n_iso']:,} rows are ISO (2024-04-29 11:00:00),")
    say(f"   {log['n_slash']:,} are dd/mm/yyyy hh:mm. Day-first PROVED: "
        f"{log['slash_first_gt12']:,} slash rows have a first field above 12,")
    say(f"   {log['slash_second_gt12']} have a second field above 12. So the slash rows are day-first.")
    say(f"   Rule: parse each format with its own explicit format string.")
    say(f"   pd.to_datetime(format='mixed') would also parse every row and lose none,")
    say(f"   but it reads the ambiguous slash dates month-first: the series would run "
        f"{log['mixed_min']} -> {log['mixed_max']}")
    say(f"   instead of the true {log['right_min']} -> {log['right_max']}, and move "
        f"{log['n_rows_moved_by_mixed']:,} rows to the wrong day.")
    say(f"2. NOT SORTED. Sorted on arrival: {log['sorted_on_arrival']}. Rule: sort_index() once, after parsing.")
    say(f"3. DUPLICATE HOURS. {log['n_duplicates']} rows repeat an hour already present "
        f"(one in one format, one in the other).")
    say(f"   All {log['n_duplicates']} are identical in every value "
        f"({log['dup_with_conflicting_values']} conflicting). Rule: drop the repeat, keep the first.")
    say(f"4. DEVICE SPELLED SIX WAYS (three devices): {log['device_raw']}")
    say(f"   Rule: strip + lower-case -> {log['device_clean']}.")
    say(f"5. SENTINEL -1 in sessions: {log['n_sentinel_raw_rows']} raw rows "
        f"({log['n_sentinel']} after de-duplication, on {log['n_sentinel_days']} different days).")
    say(f"   Rule: set to NaN, never to 0. Mean sessions/hour moved "
        f"{log['mean_hourly_with_sentinel']:.2f} -> {log['mean_hourly_without']:.2f}.")
    say(f"   Daily sums are made from the hours that were recorded; "
        f"{log['n_days_with_dropped_hour']} days have 1-3 dropped hours, so those days read a")
    say(f"   little low (one hour is ~4% of a day). Not filled; flagged here instead.")
    say(f"6. MISSING PERIODS. Counted on the HOURLY index before resampling: "
        f"{log['n_hours_expected']:,} hours expected, {log['n_hours_present']:,} present,")
    say(f"   {log['n_hours_missing']} missing = {log['n_missing_days']} whole days "
        f"(every one of them all 24 hours: {log['missing_days_all_24h']}).")
    say(f"   Days: {', '.join(log['missing_days'])}")
    say(f"   Rule: reindex to a complete calendar; those days stay NaN and the line breaks.")
    say(f"   (resample('D') alone would NOT have shown them - it invents the rows.)")
    say(f"   PARTIAL FINAL MONTH: {log['tail_month']} holds {log['tail_days']} of "
        f"{log['tail_month_days']} days (to {log['last_day']}). Kept, but marked on panel 1.")

    ah = tslib.audit_index(hourly.sessions, "h")
    say("")
    say(f"tslib.audit_index(hourly, 'h')  [the real gap check]  dtype_ok={ah['dtype_ok']}, "
        f"monotonic={ah['monotonic']}, n_duplicated={ah['n_duplicated']},")
    say(f"   n_missing={ah['n_missing']} hours, partial_tail={ah['partial_tail']}  "
        f"(tail = {ah['tail_period']}, {ah['tail_count']} hours)")
    say(f"daily series: {len(daily)} calendar days, {int(daily.isna().sum())} of them NaN. "
        f"(audit_index on the daily series reports 0 missing, because resample()")
    say(f"   has already built the full calendar - which is exactly why the gap count has to come "
        f"from the hourly index.)")

    # ---------------- panel 1 numbers ---------------------------------------
    smooth = daily.rolling(WINDOW, center=True, min_periods=WINDOW).mean()
    smooth28 = daily.rolling(28, center=True, min_periods=28).mean()
    n_nan_smooth_interior = int(smooth.iloc[WINDOW // 2: -(WINDOW // 2)].isna().sum())
    # like-for-like year on year: the months present in BOTH years, in full.
    # Apr-Aug is the overlap (Sep 2025 is partial); this rule is set by what the
    # file contains, not by which months look better.
    y24 = daily["2024-04-01":"2024-08-31"]
    y25 = daily["2025-04-01":"2025-08-31"]
    yoy = y25.mean() / y24.mean() - 1
    first_smooth = smooth.dropna().iloc[0]
    last_smooth = smooth.dropna().iloc[-1]

    # ---------------- panel 2 ------------------------------------------------
    h = hourly.sessions
    heat = (h.groupby([h.index.dayofweek, h.index.hour]).mean()
              .unstack().reindex(range(7)))
    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    wk = heat.loc[0:4].to_numpy().mean()
    we = heat.loc[5:6].to_numpy().mean()
    pk_d, pk_h = np.unravel_index(np.nanargmax(heat.to_numpy()), heat.shape)
    weekend_lift = we / wk - 1

    # ---------------- panels 3 and 4 -----------------------------------------
    pos = cat["pos"]
    subs = (pos.groupby(["category", "subcategory"]).net_revenue_pkr_m.sum()
              .reset_index().sort_values("net_revenue_pkr_m", ascending=False))
    total_net = subs.net_revenue_pkr_m.sum()
    subs["share"] = subs.net_revenue_pkr_m / total_net * 100
    parents_tot = subs.groupby("category").net_revenue_pkr_m.sum().sort_values(ascending=False)

    say("")
    say("=" * 74)
    say("PART D - catalogue (revenue_catalogue.csv)")
    say("=" * 74)
    say(f"Rows in file: {clog['n_raw']}.  Hierarchy checks: every sub-category has exactly one "
        f"parent ({clog['subcats_with_two_parents']} with two).")
    say(f"DUPLICATE SKU: {clog['n_dup_sku']} row repeated (SKU-0127, named AUDI-04) - it appears under "
        f"Audio AND under Wearables,")
    say(f"   so the tree had a leaf with two parents. Rule: keep the Audio copy (its name prefix is AUDI); "
        f"drop the Wearables copy.")
    say(f"   After this, sku_name prefix matches sub-category on every row "
        f"({clog['n_prefix_mismatch_after_dedupe']} mismatches).")
    say(f"NEGATIVE NET REVENUE: {clog['n_negative']} SKUs, together PKR {clog['negative_total']:.2f}m. "
        f"Negatives have no area.")
    say(f"   Rule: kept out of the treemap and the bars, listed here and footnoted on the figure.")
    for r in cat["neg"].itertuples():
        say(f"      {r.sku}  {r.sku_name:8s} {r.subcategory:11s} net {r.net_revenue_pkr_m:+.4f}")
    say(f"   {clog['n_zero']} SKU has net exactly 0 and so no area either.")
    say(f"   Net revenue total moved {clog['total_net_before']:,.2f} -> {clog['total_net_after']:,.2f} "
        f"(PKR m); SKUs drawn: {clog['n_after']}.")
    say(f"DEPTH: 336 SKUs are rolled up into 8 sub-categories under 4 categories. "
        f"No 'Other' bucket was needed - all 8 are drawn.")

    shares_eight = pd.read_csv(w.DATA / "shares_eight.csv").set_index("subcategory").share_pct
    mine = subs.set_index("subcategory").share
    diff = (mine - shares_eight).abs()
    say("")
    say("Self-check against shares_eight.csv (percentage points):")
    for sname in shares_eight.index:
        say(f"   {sname:12s} mine {mine[sname]:6.2f}   file {shares_eight[sname]:5.1f}   "
            f"diff {mine[sname] - shares_eight[sname]:+.2f}")
    say(f"   largest gap {diff.max():.2f} points ({diff.idxmax()}) - the brief's limit is 0.3")
    assert diff.max() < 0.3, "hierarchy handled wrongly"
    assert abs(shares_eight.sum() - 100) < 1e-6
    assert abs(subs.share.sum() - 100) < 1e-6

    # ---------------- the figure ---------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(14, 9.6), layout="constrained")
    ax1, ax2, ax3, ax4 = axes.ravel()

    # panel 1 ----------------------------------------------------------------
    ax1.plot(daily.index, daily.values, color=PALETTE["muted"], linewidth=0.7,
             alpha=0.75, label="Daily total (raw)")
    ax1.plot(smooth.index, smooth.values, color=PALETTE["series"][0], linewidth=2.2,
             label=f"{WINDOW}-day rolling mean (centred)")
    ax1.set_ylim(0, None)
    miss = daily.index[daily.isna()]
    ax1.plot(miss, np.zeros(len(miss)), linestyle="none", marker="|", markersize=9,
             color=PALETTE["ink_soft"], label=f"{len(miss)} unrecorded days (line breaks)")
    tail0 = pd.Timestamp(f"{log['tail_month']}-01")
    ax1.axvspan(tail0, daily.index.max(), color=PALETTE["grid"], alpha=0.9, zorder=0)
    ax1.text(tail0 + (daily.index.max() - tail0) / 2, ax1.get_ylim()[1] * 0.97,
             f"{log['tail_month'][:4]}-{log['tail_month'][5:]}\npartial\n{log['tail_days']} of "
             f"{log['tail_month_days']} days", ha="center", va="top", fontsize=7,
             color=PALETTE["ink_soft"])
    bf = pd.Timestamp("2024-11-29")
    ax1.annotate("Black Friday\n113,710", xy=(bf, daily[bf]),
                 xytext=(bf + pd.Timedelta(days=22), daily[bf] * 0.97),
                 fontsize=8, color=PALETTE["ink_soft"],
                 arrowprops=dict(arrowstyle="-", color=PALETTE["ink_soft"], lw=0.8))
    ax1.set_title(f"Traffic is up {yoy:.0%} year on year (Apr-Aug); the weekend\n"
                  f"rhythm is averaged out by a {WINDOW}-day rolling mean")
    ax1.set_ylabel("Sessions per day (sum of hourly)")
    ax1.set_xlabel("Date (first recorded day, 1 Apr 2024, to 11 Sep 2025)")
    ax1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
    ax1.legend(loc="upper left", fontsize=7.5)

    # panel 2 ----------------------------------------------------------------
    im = ax2.imshow(heat.to_numpy(), aspect="auto", cmap=PALETTE["sequential"],
                    vmin=0, interpolation="nearest")
    ax2.grid(False)
    ax2.set_yticks(range(7), dow_names)
    ax2.set_xticks(range(0, 24, 3), [f"{x:02d}" for x in range(0, 24, 3)])
    ax2.set_xlabel("Hour of day (0-23, local)")
    ax2.set_ylabel("Day of week")
    for sp in ax2.spines.values():
        sp.set_visible(False)
    cb = fig.colorbar(im, ax=ax2, pad=0.02)
    cb.set_label("Mean sessions per hour", color=PALETTE["ink_soft"])
    cb.outline.set_visible(False)
    ax2.set_title(f"Weekends run {weekend_lift:.0%} busier than weekdays;\n"
                  f"the peak is {dow_names[pk_d]} at {pk_h:02d}:00")

    # panel 3 ----------------------------------------------------------------
    small = nested_treemap(ax3, subs, "net_revenue_pkr_m")
    top_parent = parents_tot.index[0]
    ax3.set_title(f"{top_parent} holds {parents_tot.iloc[0] / total_net:.0%} of net revenue;\n"
                  f"{subs.iloc[0].subcategory} is the biggest single block")
    ax3.text(0, 104, "Area = net revenue, PKR m (gross minus returns, summed over the period). "
                     "Hue = category.", fontsize=7.2, color=PALETTE["ink_soft"],
             va="top", ha="left")
    say("")
    say(f"Treemap blocks too small for a printed label: {small if small else 'none'} (values are on panel 4)")

    # panel 4 ----------------------------------------------------------------
    order = subs.sort_values("net_revenue_pkr_m")           # barh draws bottom-up
    cols = [PARENT_HUE[c] for c in order.category]
    ypos = np.arange(len(order))
    ax4.barh(ypos, order.net_revenue_pkr_m, color=cols, height=0.68)
    for y, v, s in zip(ypos, order.net_revenue_pkr_m, order.share):
        ax4.text(v + total_net * 0.006, y, f"{v:,.1f}  ({s:.1f}%)", va="center",
                 fontsize=8.5, color=PALETTE["ink"])
    ax4.set_yticks(ypos, order.subcategory)
    ax4.set_xlim(0, order.net_revenue_pkr_m.max() * 1.22)
    ax4.grid(axis="y", visible=False)
    ax4.set_xlabel("Net revenue, PKR m (gross minus returns, summed over the period)")
    gap = subs.iloc[0].net_revenue_pkr_m / subs.iloc[1].net_revenue_pkr_m
    ax4.set_title(f"{subs.iloc[0].subcategory} earns {gap:.1f}x the runner-up "
                  f"({subs.iloc[1].subcategory});\n"
                  f"{subs.iloc[-1].subcategory} is last at {subs.iloc[-1].share:.1f}%")
    ax4.legend(handles=[Patch(color=c, label=k) for k, c in PARENT_HUE.items()],
               loc="lower right", fontsize=7.5, title="Category", title_fontsize=7.5)
    ax4.text(0.0, -0.20, f"Not drawn: {clog['n_negative']} loss-making SKUs, net "
             f"PKR {clog['negative_total']:.2f}m in total (negatives have no area).",
             transform=ax4.transAxes, fontsize=7.2, color=PALETTE["ink_soft"], va="top")

    # aspect ratio of panel 1, stated - and what banking to 45 degrees would ask for
    fig.canvas.draw()
    bb = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    asp = bb.width / bb.height
    banked = tslib.banked_figsize(smooth.dropna().to_numpy(), width=bb.width)
    say("")
    say(f"Panel 1 is drawn {bb.width:.1f} x {bb.height:.1f} in (aspect {asp:.2f}:1). "
        f"banked_figsize() for this series asks for {banked[0]:.1f} x {banked[1]:.1f} in "
        f"({banked[0] / banked[1]:.1f}:1);")
    say("   The 2x2 grid fixes the shape, so the aspect is a layout choice, not a banked one - "
        "it happens to sit close to the banked ratio. Stated here and on the figure.")

    note = (f"{w.DATA_NOTE}  Panels 1-2: sessions_hourly.csv, n = {log['n_hours_present']:,} hourly rows after "
            f"removing {log['n_duplicates']} duplicates; {log['n_sentinel']} sentinel (-1) values set missing; "
            f"{log['n_missing_days']} days never recorded.\n"
            f"Panel 1 aspect {asp:.1f}:1 (layout, not banked to 45 deg). Daily totals are sums of recorded hours; "
            f"year-on-year = mean daily sessions Apr-Aug 2025 vs Apr-Aug 2024 (the months complete in both years).\n"
            f"Panels 3-4: revenue_catalogue.csv, {clog['n_after']} SKUs drawn of {clog['n_raw']} rows: "
            f"{clog['n_dup_sku']} duplicate SKU removed, {clog['n_negative']} negative-net SKUs "
            f"(PKR {clog['negative_total']:.2f}m) and {clog['n_zero']} zero-net SKU not drawn. "
            f"No 'Other' bucket; 8 sub-categories under 4 categories. Fourth hue (pink) always carries a printed label.")
    save_fig(fig, OUT_PNG, note=note)          # savefig first; this script never calls show()
    plt.close(fig)
    say("")
    say(f"saved {OUT_PNG.name} at 300 dpi")

    # ---------------- appendix: the 28-day version -----------------------------
    fig2, ax = plt.subplots(figsize=(10, 4.2), layout="constrained")
    ax.plot(daily.index, daily.values, color=PALETTE["muted"], linewidth=0.7, alpha=0.75,
            label="Daily total (raw)")
    ax.plot(smooth.index, smooth.values, color=PALETTE["series"][0], linewidth=1.6, alpha=0.5,
            label="7-day rolling mean (the one used in the main figure)")
    ax.plot(smooth28.index, smooth28.values, color=PALETTE["series"][1], linewidth=2.2,
            label="28-day rolling mean (centred)")
    ax.set_ylim(0, None)
    ax.axvspan(tail0, daily.index.max(), color=PALETTE["grid"], alpha=0.9, zorder=0)
    ax.text(tail0 + (daily.index.max() - tail0) / 2, ax.get_ylim()[1] * 0.97,
            f"{log['tail_month']}\npartial\n{log['tail_days']} of {log['tail_month_days']} d",
            ha="center", va="top", fontsize=6.5, color=PALETTE["ink_soft"])
    ax.plot(miss, np.zeros(len(miss)), linestyle="none", marker="|", markersize=8,
            color=PALETTE["ink_soft"], label=f"{len(miss)} unrecorded days")
    ax.set_title("Appendix: a 28-day window tells the same story as the 7-day window")
    ax.set_ylabel("Sessions per day (sum of hourly)")
    ax.set_xlabel("Date")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
    ax.legend(loc="upper left", fontsize=8)
    save_fig(fig2, OUT_APPX, note=f"{w.DATA_NOTE} Same cleaned daily series as the main figure; "
             f"n = {log['n_days_recorded']} recorded days; centred windows are not drawn within half a window of an "
             f"unrecorded day or either end. Last month is partial (shaded).")
    plt.close(fig2)

    # direction check for the sentence in Part E: does the 28-day version change it?
    def slope_per_day(s):
        v = s.dropna()
        x = (v.index - v.index[0]).days.to_numpy()
        return float(np.polyfit(x, v.to_numpy(), 1)[0])
    s7, s28 = slope_per_day(smooth), slope_per_day(smooth28)
    def paired_yoy(line):
        a = line["2024-04-01":"2024-08-31"]
        b = line["2025-04-01":"2025-08-31"]
        b.index = b.index - pd.Timedelta(days=365)      # 2024-04-01 + 365 d = 2025-04-01
        both = pd.concat([a, b], axis=1, keys=["y24", "y25"]).dropna()
        return both.y25.mean() / both.y24.mean() - 1, len(both)
    y7p, n7p = paired_yoy(smooth)
    y28p, n28p = paired_yoy(smooth28)
    say("")
    say("Direction check for the appendix (Part E):")
    say(f"   fitted slope of the smoothed line  7-day {s7:+,.1f} sessions/day per day,  "
        f"28-day {s28:+,.1f}")
    say(f"   year-on-year on matched dates, Apr-Aug: 7-day line {y7p:+.1%} ({n7p} paired days);  "
        f"28-day line {y28p:+.1%} ({n28p} paired days)")
    say(f"   (raw daily mean, all days: {yoy:+.1%}; the smoothed lines differ because a centred "
        f"window cannot be drawn within half a window of an unrecorded day)")
    same_dir = bool((np.sign(s7) == np.sign(s28)) and (y7p > 0) == (y28p > 0))
    say(f"   same direction under both windows: {same_dir}")
    say(f"   interior NaNs in the 7-day line (gaps breaking it): {n_nan_smooth_interior} days "
        f"around the {len(miss)} unrecorded days")
    say(f"   7-day line is undefined for the first and last {WINDOW // 2} days (centred window).")

    nums = {
        "yoy": float(yoy), "weekend_lift": float(weekend_lift),
        "peak": f"{dow_names[pk_d]} {pk_h:02d}:00",
        "first_smooth": float(first_smooth), "last_smooth": float(last_smooth),
        "banked": [float(banked[0]), float(banked[1])], "aspect_used": float(asp),
        "same_direction_28": bool(same_dir), "slope7": s7, "slope28": s28,
        "yoy_28": float(y28p), "yoy_7_paired": float(y7p),
        "top_parent": top_parent, "top_parent_share": float(parents_tot.iloc[0] / total_net * 100),
        "top_sub": subs.iloc[0].subcategory, "top_sub_share": float(subs.iloc[0].share),
        "bottom_sub": subs.iloc[-1].subcategory, "bottom_sub_share": float(subs.iloc[-1].share),
        "max_share_gap": float(diff.max()), "n_interior_nan": n_nan_smooth_interior,
        "sessions_log": {k: v for k, v in log.items()},
        "catalogue_log": {k: v for k, v in clog.items() if k != "dup_rows"},
    }
    (HERE / "partD_numbers.json").write_text(json.dumps(nums, indent=1, default=str))
    say("")
    say("done.")
    say_close = say.close
    say_close()


if __name__ == "__main__":
    main()
