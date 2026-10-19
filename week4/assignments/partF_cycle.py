"""
Part F (bonus) - Week 1's flights.csv question, on data I found myself.

    python3 partF_cycle.py

The question Week 1 left open: the seasonal swing gets bigger every year - is
the seasonality growing, or is the thing being measured just getting bigger?

Data: unemployed persons (thousands) by industry, monthly, not seasonally
adjusted, Jan 2000 - Feb 2010, 14 industries (the category column is `series`).
See partF_SOURCE.md for the citation and the download date.

Writes partF_cycle.png (300 dpi) and partF_output.txt.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

import tslib
from tslib import PALETTE, style_defaults, save_fig
import w4common as w

HERE = Path(__file__).resolve().parent
SRC = HERE / "partF_data" / "unemployment-across-industries.json"
CATEGORY = "Construction"          # picked for its large seasonal swing, before the additive/multiplicative comparison
say = w.Tee(HERE / "partF_output.txt")


def main():
    style_defaults()
    raw = pd.read_json(SRC)
    say("=" * 74)
    say("PART F - is the seasonality growing, or is the series?")
    say("=" * 74)
    say(f"File: {SRC.name}, {len(raw):,} rows, {raw.series.nunique()} industries x "
        f"{len(raw) // raw.series.nunique()} months. Category column: 'series'. Focus: {CATEGORY}.")
    say("Why Construction: I looked at which industries had a visible winter swing at all (it has the largest) "
        "and picked it BEFORE comparing the additive and multiplicative")
    say("models. The code runs unchanged on any of the 14 industries; change CATEGORY to try another.")

    # the raw `date` string carries a time zone offset that flips between 07:00 and 08:00 with daylight
    # saving, so it cannot be trusted as a month start. Build the index from year + month instead.
    hrs = raw.date.dt.hour.value_counts().to_dict()
    say(f"`date` carries a time-of-day that shifts with daylight saving ({hrs} rows at each hour). "
        f"Rule: ignore it, build the index from year and month.")
    s_all = (raw[raw.series == CATEGORY]
             .assign(ts=lambda d: pd.to_datetime(dict(year=d.year, month=d.month, day=1)))
             .set_index("ts").sort_index()["count"].astype(float))
    s_all.name = "unemployed (thousands)"

    a = tslib.audit_index(s_all, "MS")
    say(f"tslib.audit_index(freq='MS'): dtype_ok={a['dtype_ok']}, monotonic={a['monotonic']}, "
        f"duplicates={a['n_duplicated']}, missing months={a['n_missing']}, span={a['span'][0][:10]} to {a['span'][1][:10]},")
    say(f"   partial_tail={a['partial_tail']} (tail = {a['tail_period']}, {a['tail_count']} of 12 months)")
    s = s_all[:"2009-12-01"]
    say(f"Rule: {len(s_all) - len(s)} rows (Jan-Feb 2010) dropped - a partial final year would distort the cycle "
        f"plot. n = {len(s)} months, {len(s) // 12} full years.")

    add = seasonal_decompose(s, model="additive", period=12)
    mul = seasonal_decompose(s, model="multiplicative", period=12)
    res_add = (add.resid / add.trend * 100).dropna()          # % of the level, so both are comparable
    res_mul = ((mul.resid - 1) * 100).dropna()

    yr = s.groupby(s.index.year)
    amp = yr.max() - yr.min()
    lvl = yr.mean()
    rel = amp / lvl
    n3 = len(res_add) // 3
    sd_add = [float(res_add.iloc[i * n3:(i + 1) * n3].std()) for i in range(3)]
    sd_mul = [float(res_mul.iloc[i * n3:(i + 1) * n3].std()) for i in range(3)]
    corr = float(np.corrcoef(amp.values, lvl.values)[0, 1])
    say("")
    say("year   level (annual mean)   swing (max - min)   swing / level")
    for y in amp.index:
        say(f"{y}   {lvl[y]:>10,.0f}        {amp[y]:>10,.0f}        {rel[y]:>8.2f}")
    say(f"correlation of yearly swing with yearly level: {corr:.2f}")
    say(f"swing as a share of level: first 3 years {rel.iloc[:3].mean():.2f}, last 3 years {rel.iloc[-3:].mean():.2f}")
    say("")
    say(f"residual spread as % of the level, by thirds of the series (early / middle / late):")
    say(f"   additive        {sd_add[0]:.1f} / {sd_add[1]:.1f} / {sd_add[2]:.1f}   (late/early = {sd_add[2] / sd_add[0]:.2f})")
    say(f"   multiplicative  {sd_mul[0]:.1f} / {sd_mul[1]:.1f} / {sd_mul[2]:.1f}   (late/early = {sd_mul[2] / sd_mul[0]:.2f})")

    # ---- the figure -----------------------------------------------------------------
    bw, bh = tslib.banked_figsize(s.to_numpy(), width=9.0)
    fig = plt.figure(figsize=(12, 8.6), layout="constrained")
    gs = fig.add_gridspec(2, 2, height_ratios=[2.5, 4.4])
    a1 = fig.add_subplot(gs[0, :])
    a1.plot(s.index, s.values, color=PALETTE["series"][0], linewidth=1.6)
    a1.set_ylim(0, None)
    a1.set_ylabel("Unemployed (thousands)")
    a1.set_title(f"{CATEGORY}: unemployed persons, monthly, 2000-2009 (the level rises 3.5x, the winter swing does not)", fontsize=10)
    asp = bw / bh
    a1.set_box_aspect(bh / bw)         # force the drawn panel to BE the banked shape, so the stated number is true
    a1.set_xlabel(f"Month (panel aspect {asp:.1f}:1, banked to 45 degrees by tslib.banked_figsize)")

    a2 = fig.add_subplot(gs[1, 0])
    tslib.cycle_plot(a2, s, by="month")
    a2.set_xticks(range(1, 13), list("JFMAMJJASOND"))
    a2.set_ylim(0, None)
    a2.set_ylabel("Unemployed (thousands)")
    first, last = s.index.year.min(), s.index.year.max()
    a2.text(12.15, s[s.index.year == first].iloc[-1], str(first), fontsize=8, va="center")
    a2.text(12.15, s[s.index.year == last].iloc[-1], str(last), fontsize=8, va="center")
    a2.set_xlim(0.7, 13.2)
    a2.set_title("One line per year: the winter peak (darker = later year)")

    sub = gs[1, 1].subgridspec(1, 2, wspace=0.12)
    lim = max(res_add.abs().max(), res_mul.abs().max()) * 1.05
    b1 = fig.add_subplot(sub[0])
    b2 = fig.add_subplot(sub[1], sharey=b1)
    b1.plot(res_add.index, res_add.values, color=PALETTE["series"][1], linewidth=1.2)
    b2.plot(res_mul.index, res_mul.values, color=PALETTE["series"][2], linewidth=1.2)
    for b, t in ((b1, "additive"), (b2, "multiplicative")):
        b.axhline(0, color=PALETTE["ink_soft"], linewidth=0.8)
        b.set_title(t, fontsize=9)
        b.xaxis.set_major_locator(mdates.YearLocator(3))
        b.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        b.tick_params(axis="x", labelsize=8)
    b1.set_ylim(-lim, lim)
    plt.setp(b2.get_yticklabels(), visible=False)
    b1.set_ylabel("Residual, % of the level")
    verdict = "multiplicative" if abs(np.log(sd_mul[2] / sd_mul[0])) < abs(np.log(sd_add[2] / sd_add[0])) else "additive"
    fig.suptitle(f"Is the seasonality growing, or the series? The {verdict} model leaves the steadier residual",
                 x=0.0, ha="left", fontsize=12, fontweight="bold", color=PALETTE["ink"])
    fig.canvas.draw()
    bb = a1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    measured = bb.width / bb.height
    assert abs(measured - asp) < 0.05, f"panel 1 is drawn {measured:.2f}:1, not the banked {asp:.2f}:1"
    save_fig(fig, HERE / "partF_cycle.png",
             note=(f"Source: US Bureau of Labor Statistics unemployment by industry, via the vega-datasets repository, "
                   f"downloaded 18 Oct 2026 (partF_SOURCE.md). n = {len(s)} months, {CATEGORY}; Jan-Feb 2010 excluded as a partial year. "
                   f"Residuals are shown as % of the level so the two models share one axis."))
    plt.close(fig)
    say("")
    say(f"banked_figsize(width=9) -> {bw:.1f} x {bh:.1f} in, aspect {asp:.1f}:1. Panel 1 is drawn at exactly that "
        f"shape (measured on the rendered figure: {measured:.1f}:1) and the number is stated on the figure.")
    say("saved partF_cycle.png at 300 dpi")

    # ---- the answer, in two sentences, with the number that settles it --------------
    say("")
    if verdict == "multiplicative":
        ans = (f"ANSWER. The swing is mostly the series growing: swing and level move together across the years "
               f"(correlation {corr:.2f}), swing as a share of level stays near {rel.mean():.2f} "
               f"({rel.iloc[:3].mean():.2f} early, {rel.iloc[-3:].mean():.2f} late), and the multiplicative "
               f"residual's spread changes by a factor of {sd_mul[2] / sd_mul[0]:.2f} from the early to the late "
               f"third against {sd_add[2] / sd_add[0]:.2f} for the additive one. So the seasonality is "
               f"roughly constant in proportion and only looks bigger in absolute numbers.")
    else:
        ans = (f"ANSWER. Neither story from flights.csv holds here, and the data say why: the level of the series "
               f"rose {lvl.iloc[-1] / lvl.iloc[0]:.1f}x ({lvl.iloc[0]:,.0f} to {lvl.iloc[-1]:,.0f}) but the yearly swing "
               f"stayed in the same band ({amp.iloc[0]:,.0f} in {amp.index[0]}, {amp.iloc[-1]:,.0f} in {amp.index[-1]}; "
               f"correlation of swing with level only {corr:.2f}), so swing as a share of the level FELL from "
               f"{rel.iloc[:3].mean():.2f} to {rel.iloc[-3:].mean():.2f}. The additive residual's spread is the steadier "
               f"one (late/early {sd_add[2] / sd_add[0]:.2f} against {sd_mul[2] / sd_mul[0]:.2f}), so the seasonality "
               f"is a roughly constant number of people, not a share of a growing total - the opposite of the "
               f"airline-passenger result, and reported as it came out.")
    say(ans)
    say("Caveat: the 2008-09 recession pushes the level up sharply in the last two years, so 'level' there is "
        "partly a one-off shock, not steady growth; this is one industry in one country.")
    say.close()


if __name__ == "__main__":
    main()
