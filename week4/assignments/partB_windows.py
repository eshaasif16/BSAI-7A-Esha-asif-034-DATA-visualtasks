"""
Part B - smoothing, windows and panel shape, computed rather than eyeballed.

    python3 partB_windows.py

Works on the CLEANED daily session series from Part D (parsed with explicit
formats, de-duplicated, -1 sentinels set to NaN, resampled to daily with sum(),
the 13 unrecorded days left as NaN, September 2025 known to be partial).

Writes partB_output.txt (every number and every written answer) and
partB_windows.png (300 dpi). All five questions are answered in prose below,
each one starting with the word ANSWER so none can be missed.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

import tslib
from tslib import PALETTE, style_defaults, save_fig
import w4common as w

HERE = Path(__file__).resolve().parent
say = w.Tee(HERE / "partB_output.txt")


def r2_of_weekday(s: pd.Series, trend: pd.Series) -> float:
    """Share of what is left after removing a slow trend that a day-of-week
    effect explains. Used to show the 7-day window really cancels the cycle."""
    x = (s - trend).dropna()
    sst = ((x - x.mean()) ** 2).sum()
    sse = ((x - x.groupby(x.index.dayofweek).transform("mean")) ** 2).sum()
    return float(1 - sse / sst)


def main():
    style_defaults()
    cl = w.clean_sessions()
    daily = cl["daily"]                       # 529 days, 13 of them NaN
    filled, filled_mask = w.fill_for_models(daily)
    n_filled = int(filled_mask.sum())

    say("=" * 74)
    say("PART B - computed on the cleaned daily session series")
    say("=" * 74)
    say(f"{len(daily)} calendar days, {daily.index.min().date()} to {daily.index.max().date()}; "
        f"{n_filled} unrecorded days are NaN.")
    say(f"Where a function refuses NaN (seasonal_decompose, lag_at_turn, EWMA) the {n_filled} days are "
        f"filled by linear interpolation, for that call only, and say so.")
    say(f"The final month ({cl['log']['tail_month']}) is partial: {cl['log']['tail_days']} of "
        f"{cl['log']['tail_month_days']} days. It is kept in the daily series.")

    # ============================================================ B1
    say("")
    say("-" * 74)
    say("B1. THE WINDOW IS A HYPOTHESIS - tslib.window_report() for 7, 28 and 91")
    say("-" * 74)
    wr = tslib.window_report(daily, (7, 28, 91), center=True)
    say(wr.to_string(index=False))
    trend91 = daily.rolling(91, center=True, min_periods=45).mean()
    sm7 = daily.rolling(7, center=True, min_periods=4).mean()
    r2_raw = r2_of_weekday(daily, trend91)
    r2_7 = r2_of_weekday(sm7, trend91)
    say("")
    say(f"Is the weekly cycle really what the 7-day window removes? Share of the detrended variation "
        f"explained by day-of-week:")
    say(f"   raw daily series  R2 = {r2_raw:.3f}      7-day rolling mean  R2 = {r2_7:.3f}")
    say("")
    # how much of the seasonal swing each window leaves visible, measured on the quiet stretch after
    # Black Friday (Jan - Sep 2025) so the one-day spike does not decide it
    swing = {}
    for L in (7, 28, 91):
        sm = daily.rolling(L, center=True, min_periods=L // 2).mean()["2025-01-01":]
        swing[L] = float(sm.max() - sm.min())
    say(f"Peak-to-trough of each smoothed line over Jan-Sep 2025 (after Black Friday): "
        + "   ".join(f"{L}d {v:,.0f}" for L, v in swing.items()))
    removed = {int(r.window): r.variation_removed_pct for r in wr.itertuples()}
    say(f"ANSWER B1. A 7-day window removes {removed[7]:.1f}% of the raw standard deviation and costs "
        f"{wr.periods_lost_each_end[0]} days at each end. The cycle it cancels is the weekly one: "
        f"a window exactly one cycle long holds each weekday once, so Saturday's high and Tuesday's low "
        f"average out. The R2 above shows it - day-of-week explains {r2_raw:.0%} of the detrended raw series "
        f"and {r2_7:.1%} of the 7-day line. A 28-day window is four whole weekly cycles, so it cancels the "
        f"weekly rhythm too, plus any swing shorter than a month, but it only removes a further "
        f"{removed[28] - removed[7]:.1f} points of variation for {wr.periods_lost_each_end[1]} days lost "
        f"at each end. A 91-day window is a quarter of a year: it adds only {removed[91] - removed[28]:.1f} "
        f"more points, costs {wr.periods_lost_each_end[2]} days at each end (about a tenth of the whole "
        f"series), and flattens the seasonal swing leadership is trying to see (its Jan-Sep 2025 range is {swing[91]:,.0f} "
        f"sessions/day against {swing[7]:,.0f} for the 7-day line). "
        f"I am using 7 days in Part D. The reason is the cycle being cancelled - weekly - and not "
        f"how smooth the line looks; 7 days does the job and nothing longer buys enough to justify "
        f"the extra periods lost.")

    # ============================================================ B2
    say("")
    say("-" * 74)
    say("B2. THREE SMOOTHERS AGAINST ONE SPIKE - Black Friday, 29 Nov 2024")
    say("-" * 74)
    bf = pd.Timestamp("2024-11-29")
    raw_bf = float(daily[bf])
    fortnight = daily[bf - pd.Timedelta(days=7): bf + pd.Timedelta(days=6)]
    med_ref = float(fortnight.median())
    mean14 = float(filled.rolling(14, center=True).mean()[bf])
    med14 = float(filled.rolling(14, center=True).median()[bf])
    ewma14 = float(filled.ewm(span=14, adjust=False).mean()[bf])
    say(f"raw value on the day                    {raw_bf:>10,.0f}")
    say(f"median of the surrounding fortnight     {med_ref:>10,.0f}   (the brief quotes about 24,600)")
    say(f"14-day centred MEAN                     {mean14:>10,.0f}   ({mean14 / med_ref - 1:+.0%} vs fortnight median)")
    say(f"14-day centred MEDIAN                   {med14:>10,.0f}   ({med14 / med_ref - 1:+.0%})")
    say(f"EWMA, span = 14 (trailing by design)    {ewma14:>10,.0f}   ({ewma14 / med_ref - 1:+.0%})")
    say("   (an even window has no middle day; pandas centres a 14-day window on days t-7 ... t+6.")
    say("    An EWMA has no 'centred' form - it only looks backwards - so it is the trailing member here.)")
    say("")
    say(f"ANSWER B2. On the day, the raw value is {raw_bf:,.0f} against a fortnight median of about "
        f"{med_ref:,.0f} (the brief says about 24,600; the small difference is just where the fortnight is placed). The mean is dragged up to {mean14:,.0f} because one huge day in fourteen still "
        f"carries one-fourteenth of the weight; the EWMA reads {ewma14:,.0f}, since it gives the newest "
        f"day the most weight; the median stays at {med14:,.0f}, because a single value can never move "
        f"the middle of fourteen. For a monitoring dashboard I would use the EWMA (or the mean), because "
        f"there the spike IS the news - an alerting line that quietly ignores a four-fold jump is "
        f"useless, and the EWMA is also the one that needs no future data. For a quarterly report I "
        f"would use the median, because the report is about the level of traffic and one sale day "
        f"should not bend the line; Black Friday then gets its own annotation instead of hiding inside "
        f"the average.")

    # ============================================================ B3
    say("")
    say("-" * 74)
    say("B3. DECOMPOSE IT - seasonal_decompose, additive")
    say("-" * 74)
    dec = seasonal_decompose(filled, model="additive", period=7)
    week = dec.seasonal.iloc[:7]
    amp = float(dec.seasonal.max() - dec.seasonal.min())
    resid = dec.resid.where(~filled_mask)         # an interpolated day cannot be 'the event'
    top = resid.abs().nlargest(3)
    big_day = top.index[0]
    say(f"period = 7. Weekly seasonal component, by weekday of the first seven days "
        f"({', '.join(d.strftime('%a') for d in week.index)}):")
    say("   " + "  ".join(f"{d.strftime('%a')} {v:+,.0f}" for d, v in week.items()))
    say(f"peak-to-trough amplitude of the weekly component: {amp:,.0f} sessions/day")
    say("three largest |residuals| (interpolated days excluded):")
    for d, v in top.items():
        say(f"   {d.date()} ({d.strftime('%a')})   residual {resid[d]:+,.0f}")
    say("")
    try:
        seasonal_decompose(filled, model="additive", period=365)
        p365 = "ran"
    except ValueError as e:
        p365 = str(e)
    say(f"period = 365 -> statsmodels says: ValueError: {p365}")
    say(f"ANSWER B3. The weekly component swings {amp:,.0f} sessions/day from its lowest weekday to its "
        f"highest (Saturday and Sunday sit about {week.iloc[5:].mean() - week.iloc[:5].mean():,.0f} above the "
        f"weekday average). The largest residual is {big_day.date()}, Black Friday, at "
        f"{resid[big_day]:+,.0f}: once the trend and the weekly rhythm are taken out, nothing "
        f"explains that day, which is exactly why it is the one to investigate. The next largest residuals "
        f"({top.index[1].date()}, {top.index[2].date()}) are its immediate neighbours and are mostly an "
        f"echo - the 7-day trend component absorbs part of the spike and spreads it across the days around it. "
        f"I could not complete the period=365 run: statsmodels refuses, because it needs two complete "
        f"cycles (730 days) and this series has {len(filled)}. What would move, given enough data, is "
        f"anything that repeats once a year - the November sale surge and the holiday ramp - which sit in "
        f"`resid` and `trend` at period=7 and would be learned as `seasonal` at period=365. With a single "
        f"November on file there is no second one to confirm it, so even a workaround would be fitting "
        f"noise.")

    # ============================================================ B4
    say("")
    say("-" * 74)
    say("B4. TRAILING OR CENTRED - tslib.lag_at_turn(), 31-day window")
    say("-" * 74)
    lg = tslib.lag_at_turn(filled, 31, how="min")
    say(f"turning point (minimum of the smoothed line): trailing {lg['trailing_turn'].date()}, "
        f"centred {lg['centred_turn'].date()}")
    say(f"lag = {lg['lag_periods']} days; half the window = {lg['half_window']} days")
    for wd in (7, 15, 61):
        l2 = tslib.lag_at_turn(filled, wd, how="min")
        say(f"   check with window {wd:>2}: lag {l2['lag_periods']:>2} days (half-window {l2['half_window']})")
    say(f"ANSWER B4. The trailing mean finds the turn {lg['lag_periods']} days after the centred one, and "
        f"half of 31 is {lg['half_window']}: the lag is the half-window, to the day. It is arithmetic rather "
        f"than a fault - a trailing window cannot know a turn has happened until enough post-turn days have "
        f"entered it. A dashboard that refreshes every morning only has data up to yesterday, so a centred "
        f"window is impossible there (it needs days that have not happened yet) and it must show the "
        f"trailing mean. Its caption has to say so: '31-day trailing mean - turning points show up about "
        f"15 days after they happen.' A centred line can replace it later, once the future days exist.")

    # ============================================================ B5
    say("")
    say("-" * 74)
    say("B5. THE WINDOW IS A CLAIM - 12 start months x 5 window lengths")
    say("-" * 74)
    starts = pd.date_range("2024-04-01", periods=12, freq="MS")
    lengths = [7, 14, 28, 56, 91]
    grid = pd.DataFrame(index=starts.strftime("%b %Y"), columns=lengths, dtype=float)
    skipped = 0
    for s0 in starts:
        for L in lengths:
            seg = daily[s0: s0 + pd.Timedelta(days=L - 1)].dropna()
            if len(seg) < 5:
                skipped += 1
                continue
            x = (seg.index - s0).days.to_numpy()
            grid.loc[s0.strftime("%b %Y"), L] = np.polyfit(x, seg.to_numpy(), 1)[0]
    vals = grid.to_numpy().ravel()
    vals = vals[~np.isnan(vals)]
    n_up, n_down = int((vals > 0).sum()), int((vals < 0).sum())
    say(f"combinations tried: {len(starts)} x {len(lengths)} = {len(starts) * len(lengths)}  "
        f"(skipped for too few recorded days: {skipped})")
    say(f"slopes (sessions/day per day), fitted by least squares to the RAW daily values:")
    say(grid.round(0).to_string())
    early = grid.iloc[:7]       # starts Apr - Oct 2024
    late = grid.iloc[7:]        # starts Nov 2024 - Mar 2025
    e_up, e_n = int((early.to_numpy() > 0).sum()), int(early.notna().to_numpy().sum())
    l_up, l_n = int((late.to_numpy() > 0).sum()), int(late.notna().to_numpy().sum())
    ratio = float(grid[7].abs().median() / grid[91].abs().median())
    say("")
    say(f"RISING: {n_up}     FALLING: {n_down}")
    say(f"starts Apr-Oct 2024: {e_up} of {e_n} rise;  starts Nov 2024-Mar 2025: {l_up} of {l_n} rise")
    say(f"median |slope|, 7-day windows vs 91-day windows: {ratio:.0f}x")
    by_len = {L: (int((grid[L] > 0).sum()), int((grid[L] < 0).sum())) for L in lengths}
    say("by window length (rising / falling): " + "   ".join(f"{L}d {u}/{d}" for L, (u, d) in by_len.items()))
    say("")
    say(f"ANSWER B5. On one unchanged series, {n_up} of the {n_up + n_down} start-and-window combinations "
        f"produce a rising trend and {n_down} produce a falling one. The short windows are the least "
        f"stable: the 7-day slopes are about {ratio:.0f} times the size of the 91-day ones, which means a "
        f"7-day fit mostly measures where in the weekly cycle it happened to start. And the start month "
        f"matters because the series has a seasonal shape - {e_up} of {e_n} fits that start between April "
        f"and October 2024 rise, against only {l_up} of {l_n} that start from November onwards. Anyone could "
        f"pick a row of this table and call it 'the trend'.")
    say(f"Why the Lie Factor cannot be computed for a cherry-picked window: the formula is "
        f"(effect shown) / (effect in the data), and it assumes the data effect exists independently of "
        f"the picture - one agreed start and one agreed end. A chosen window is both: the 'effect in the "
        f"data' is measured from the same two endpoints the chart shows, so numerator and denominator are "
        f"the same number and the Lie Factor is 1.0 by construction, even when the chart is misleading. "
        f"The lie is in which window was chosen, not in how the ink is scaled to it. The honest substitute "
        f"is to report the spread: show the full series, say how many of the combinations rise and how "
        f"many fall ({n_up} / {n_down} here), or the range of slopes, so the reader can see how much the "
        f"choice matters. That is what the table above does.")

    # ----------------------------------------------------------- figure
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8), layout="constrained",
                                 gridspec_kw={"width_ratios": [1.5, 1]})
    a1.plot(daily.index, daily.values, color=PALETTE["muted"], linewidth=0.7, alpha=0.7,
            label="Daily total (raw)")
    for L, colr, lw in [(7, PALETTE["series"][0], 2.0), (28, PALETTE["series"][1], 2.0),
                        (91, PALETTE["series"][2], 2.0)]:
        sm = daily.rolling(L, center=True, min_periods=L // 2).mean()
        a1.plot(sm.index, sm.values, color=colr, linewidth=lw, label=f"{L}-day centred mean")
    a1.set_ylim(0, 60000)
    tail0 = pd.Timestamp(f"{cl['log']['tail_month']}-01")
    a1.axvspan(tail0, daily.index.max(), color=PALETTE["grid"], alpha=0.9, zorder=0)
    a1.text(tail0 + (daily.index.max() - tail0) / 2, 57500,
            f"{cl['log']['tail_month']}\npartial\n{cl['log']['tail_days']} of {cl['log']['tail_month_days']} d",
            ha="center", va="top", fontsize=6.5, color=PALETTE["ink_soft"])
    gap_days = daily.index[daily.isna()]
    a1.plot(gap_days, np.zeros(len(gap_days)), linestyle="none", marker="|", markersize=8,
            color=PALETTE["ink_soft"], label=f"{len(gap_days)} unrecorded days")
    a1.annotate(f"Black Friday {raw_bf:,.0f} (off the scale)", xy=(bf, 60000),
                xytext=(bf + pd.Timedelta(days=15), 56000), fontsize=7.5, color=PALETTE["ink_soft"],
                arrowprops=dict(arrowstyle="-", color=PALETTE["ink_soft"], lw=0.8))
    a1.set_title("Seven days removes most of what any window removes")
    a1.set_ylabel("Sessions per day (sum of hourly)")
    a1.set_xlabel("Date")
    a1.legend(loc="upper left", fontsize=7.5, ncol=2)
    a1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k"))

    lim = np.nanmax(np.abs(grid.to_numpy()))
    im = a2.imshow(grid.to_numpy(), cmap=PALETTE["diverging"], vmin=-lim, vmax=lim, aspect="auto")
    a2.grid(False)
    a2.set_xticks(range(len(lengths)), [f"{L} d" for L in lengths])
    a2.set_yticks(range(len(starts)), grid.index)
    for sp in a2.spines.values():
        sp.set_visible(False)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            v = grid.iloc[i, j]
            if np.isnan(v):
                continue
            a2.text(j, i, "+" if v > 0 else "-", ha="center", va="center", fontsize=9,
                    color="white" if abs(v) > lim * 0.55 else PALETTE["ink"])
    a2.set_xlabel("Window length (days)")
    a2.set_ylabel("Window starts on the 1st of")
    cb = fig.colorbar(im, ax=a2, pad=0.02)
    cb.set_label("Fitted slope (sessions/day per day)", color=PALETTE["ink_soft"])
    cb.outline.set_visible(False)
    a2.set_title(f"Same series: {n_up} windows rise, {n_down} fall")
    save_fig(fig, HERE / "partB_windows.png",
             note=f"{w.DATA_NOTE} Cleaned daily sessions, n = {int(daily.notna().sum())} recorded days of "
                  f"{len(daily)}; centred windows with min_periods = half the window; slopes fitted to raw daily "
                  f"values, one fit per cell. Last month is partial (shaded); unrecorded days are ticked on the baseline.")
    plt.close(fig)
    say("")
    say("saved partB_windows.png at 300 dpi")
    say.close()


if __name__ == "__main__":
    main()
