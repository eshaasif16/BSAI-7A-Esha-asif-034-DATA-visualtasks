"""
Part A - rebuild nine charts, take them apart, plot the nine honest versions.

    python3 partA_charts.py

For every case this script does the four things the brief marks:
    1. REBUILD  the chart exactly as the analyst's recipe says, and assert the
                brief's self-check number so you know the rebuild is faithful;
    2. DECOY    test the first objection that comes to mind, with a number;
    3. MECHANISM  compute the number that proves what is really going on;
    4. REDESIGN  plot the honest chart.

Writes (all next to this file, all PNGs at 300 dpi):
    partA_published_all.png    the nine charts as the analysts published them
    partA_redesigns_all.png    the nine redesigns, same 3 x 3 layout
    partA_figures/caseNN_published.png, caseNN_redesign.png   (used by the PDF)
    partA_output.txt           every number and the written diagnosis
    partA_diagnosis.json       the same diagnosis, for build_partA_pdf.py
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from vizlib import PALETTE, MARKERS, style_defaults, save_fig, lie_factor
import w4common as w

HERE = Path(__file__).resolve().parent
FIGS = HERE / "partA_figures"
FIGS.mkdir(exist_ok=True)
D = w.DATA
say = w.Tee(HERE / "partA_output.txt")

BLUE, ORANGE, GREEN = PALETTE["series"]
PINK, GREY, INK, SOFT = PALETTE["series_4th"], PALETTE["muted"], PALETTE["ink"], PALETTE["ink_soft"]
TITLE_FS = 9.5


def ttl(ax, text):
    ax.set_title(textwrap.fill(text, 58), fontsize=TITLE_FS)


def kfmt(ax, axis="y"):
    f = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


def pct(x, d=1):
    return f"{x * 100:+.{d}f}%"


# =============================================================== data + evidence
def compute() -> dict:
    N: dict = {}

    # ---------------------------------------------------------------- case 1
    c1 = pd.read_csv(D / "case01_orders_stringdate.csv")
    txt = c1.sort_values("month").reset_index(drop=True)            # what the recipe does
    c1["d"] = pd.to_datetime(c1.month, format="%Y-%m")
    fixed = c1.sort_values("d").reset_index(drop=True)
    diffs_txt = txt.orders.diff().dropna()
    n1 = dict(
        txt=txt, fixed=fixed, n=len(txt),
        drops_txt=[abs(int(v)) for v in diffs_txt[diffs_txt < 0]],
        n_fall_txt=int((diffs_txt < 0).sum()),
        n_fall_fixed=int((fixed.orders.diff() < 0).sum()),
        min_rise=float(fixed.orders.diff().min()),
        max_rise=float(fixed.orders.diff().max()),
        first=int(fixed.orders.iloc[0]), last=int(fixed.orders.iloc[-1]),
        total_rise=float(fixed.orders.iloc[-1] / fixed.orders.iloc[0] - 1),
        feb24=int(fixed.orders.iloc[1]), jan24=int(fixed.orders.iloc[0]),
        rider_branch_values=int(c1.branch.nunique()),
        order_txt=txt.month.tolist()[:6],
    )
    n1["feb_vs_jan"] = n1["feb24"] - n1["jan24"]
    assert n1["n"] == 24 and n1["drops_txt"] == [958, 978]
    N[1] = n1

    # ---------------------------------------------------------------- case 2
    c2 = pd.read_csv(D / "case02_shop_closed.csv", parse_dates=["date"])
    full = pd.date_range(c2.date.min(), c2.date.max())
    miss = full.difference(c2.date)
    pre, post = c2[c2.date < miss.min()], c2[c2.date > miss.max()]
    x_row = np.arange(len(c2))
    x_day = (c2.date - c2.date.min()).dt.days.to_numpy()
    n2 = dict(
        df=c2, n=len(c2), span=len(full), n_missing=len(miss),
        gap_start=miss.min(), gap_end=miss.max(),
        gap_contiguous=bool((miss[-1] - miss[0]).days + 1 == len(miss)),
        first=int(c2.sales_pkr_k.iloc[0]), last=int(c2.sales_pkr_k.iloc[-1]),
        rise=float(c2.sales_pkr_k.iloc[-1] / c2.sales_pkr_k.iloc[0] - 1),
        pre_mean=float(pre.sales_pkr_k.mean()), post_mean=float(post.sales_pkr_k.mean()),
        n_pre=len(pre), n_post=len(post),
        slope_pre=float(np.polyfit((pre.date - pre.date.min()).dt.days, pre.sales_pkr_k, 1)[0]),
        slope_post=float(np.polyfit((post.date - post.date.min()).dt.days, post.sales_pkr_k, 1)[0]),
        slope_row=float(np.polyfit(x_row, c2.sales_pkr_k, 1)[0]),
        slope_day=float(np.polyfit(x_day, c2.sales_pkr_k, 1)[0]),
        missing_by_weekday=pd.Series(miss.dayofweek).value_counts().sort_index().tolist(),
        dow_mean_min=float(c2.groupby(c2.date.dt.dayofweek).sales_pkr_k.mean().min()),
        dow_mean_max=float(c2.groupby(c2.date.dt.dayofweek).sales_pkr_k.mean().max()),
    )
    n2["missing_outside_block"] = int(len(miss.difference(pd.date_range(miss.min(), miss.max()))))
    n2["step"] = n2["post_mean"] / n2["pre_mean"] - 1
    n2["row_overstates"] = n2["slope_row"] / n2["slope_day"] - 1
    assert n2["n"] == 69 and n2["first"] == 207 and n2["last"] == 253 and round(n2["rise"] * 100) == 22
    N[2] = n2

    # ---------------------------------------------------------------- case 3
    c3 = pd.read_csv(D / "case03_bandwidth_levels.csv", parse_dates=["ts"]).set_index("ts")
    users, byts = c3.concurrent_users, c3.bytes_served
    dsum = users.resample("D").sum()
    jun, jul = c3[c3.index.month == 6], c3[c3.index.month == 7]
    cnt = users.resample("D").count()
    jh = jun.groupby(jun.index.hour).concurrent_users.mean()
    lh = jul.groupby(jul.index.hour).concurrent_users.mean()
    bsum = byts.resample("D").sum()
    n3 = dict(
        c3=c3, dsum=dsum, cnt=cnt, daily_mean=users.resample("D").mean(),
        jun_mean_sum=float(dsum[dsum.index.month == 6].mean()),
        jul_mean_sum=float(dsum[dsum.index.month == 7].mean()),
        jun_hours=int(len(jun)), jun_hours_possible=30 * 24,
        jul_hours=int(len(jul)),
        jun_obs_per_day=float(cnt[cnt.index.month == 6].mean()),
        jul_obs_per_day=float(cnt[cnt.index.month == 7].mean()),
        per_hour_jun=float(jun.concurrent_users.mean()),
        per_hour_jul=float(jul.concurrent_users.mean()),
        matched_hours_change=float(lh.loc[jh.index].mean() / jh.mean() - 1),
        bytes_sum_jump=float(bsum[bsum.index.month == 7].mean() / bsum[bsum.index.month == 6].mean() - 1),
        bytes_per_hour_change=float(jul.bytes_served.mean() / jun.bytes_served.mean() - 1),
        n_rows=len(c3),
    )
    n3["sum_jump"] = n3["jul_mean_sum"] / n3["jun_mean_sum"] - 1
    n3["per_hour_change"] = n3["per_hour_jul"] / n3["per_hour_jun"] - 1
    assert round(n3["jun_mean_sum"], -2) == 8800 and round(n3["jul_mean_sum"], -2) == 12500
    assert round(n3["sum_jump"] * 100) == 43
    N[3] = n3

    # ---------------------------------------------------------------- case 4
    s4 = pd.read_csv(D / "case04_intervention_lag.csv", parse_dates=["date"]).set_index("date").conversion_pct
    tr31, ce31 = s4.rolling(31).mean(), s4.rolling(31, center=True).mean()
    ce7 = s4.rolling(7, center=True).mean()
    lags = {}
    for wd in (7, 15, 31, 61):
        t_, c_ = s4.rolling(wd).mean().idxmin(), s4.rolling(wd, center=True).mean().idxmin()
        lags[wd] = (int((t_ - c_).days), wd // 2)
    # piecewise-linear break, as an independent estimate of where the line turned
    xx = np.arange(len(s4))
    best = None
    for i in range(20, len(s4) - 20):
        A = np.column_stack([np.ones(len(s4)), xx, np.clip(xx - i, 0, None)])
        beta = np.linalg.lstsq(A, s4.values, rcond=None)[0]
        sse = float(((A @ beta - s4.values) ** 2).sum())
        if best is None or sse < best[0]:
            best = (sse, i)
    n4 = dict(s=s4, tr31=tr31, ce31=ce31, ce7=ce7, n=len(s4),
              trailing_min=tr31.idxmin(), centred_min=ce31.idxmin(),
              ce7_min=ce7.idxmin(), pw_break=s4.index[best[1]], lags=lags,
              lag31=lags[31][0], min_level=float(tr31.min()),
              last=float(s4.iloc[-1]), first=float(s4.iloc[0]))
    assert str(n4["trailing_min"].date()) == "2025-09-07"
    N[4] = n4

    # ---------------------------------------------------------------- case 5
    c5 = pd.read_csv(D / "case05_revenue_window.csv")
    c5["d"] = pd.to_datetime(c5.month)
    win = c5[(c5.d >= "2025-05-01") & (c5.d <= "2025-11-01")]
    yrs = {}
    for y in (2023, 2024, 2025):
        ys = c5[c5.d.dt.year == y].set_index(c5[c5.d.dt.year == y].d.dt.month).revenue_pkr_m
        yrs[y] = dict(may=float(ys[5]), nov=float(ys[11]), fall=float(ys[11] / ys[5] - 1),
                      peak_month=int(ys.idxmax()), trough_month=int(ys.idxmin()),
                      total=float(ys.sum()), series=ys)
    n5 = dict(c5=c5, win=win, n=len(win), first=float(win.revenue_pkr_m.iloc[0]),
              last=float(win.revenue_pkr_m.iloc[-1]),
              fall=float(win.revenue_pkr_m.iloc[-1] / win.revenue_pkr_m.iloc[0] - 1),
              straight_falls=int((win.revenue_pkr_m.diff().dropna() < 0).sum()),
              years=yrs, n_total=len(c5),
              yoy_may=yrs[2025]["may"] / yrs[2024]["may"] - 1,
              yoy_nov=yrs[2025]["nov"] / yrs[2024]["nov"] - 1,
              annual_growth=yrs[2025]["total"] / yrs[2024]["total"] - 1,
              dec_rebound=float(c5.revenue_pkr_m.iloc[-1] / c5.revenue_pkr_m.iloc[-2] - 1),
              zero_baseline=bool(True))
    assert n5["n"] == 7 and round(n5["first"], 1) == 158.8 and round(n5["last"], 1) == 92.2
    N[5] = n5

    # ---------------------------------------------------------------- case 6
    c6 = pd.read_csv(D / "case06_monthly_partial.csv", parse_dates=["date"]).set_index("date")
    msum = c6.orders.resample("MS").sum()
    mdays = c6.orders.resample("MS").count()
    per_day = msum / mdays
    oct_days = c6.orders["2025-10-01":]
    n6 = dict(msum=msum, mdays=mdays, per_day=per_day, n_bars=len(msum),
              sep=int(msum.iloc[-2]), oct=int(msum.iloc[-1]),
              oct_over_sep=float(msum.iloc[-1] / msum.iloc[-2]),
              oct_days=int(mdays.iloc[-1]), oct_possible=31,
              last_day=str(c6.index.max().date()),
              oct_rate=float(per_day.iloc[-1]), sep_rate=float(per_day.iloc[-2]),
              best_prev_rate=float(per_day.iloc[:-1].max()),
              oct_daily_min=int(oct_days.min()), sep_daily_mean=float(c6.orders["2025-09-01":"2025-09-30"].mean()),
              sep_first11=int(c6.orders["2025-09-01":"2025-09-11"].sum()),
              oct_first11=int(c6.orders["2025-10-01":"2025-10-11"].sum()),
              n_rows=len(c6), c6=c6)
    n6["like_for_like"] = n6["oct_first11"] / n6["sep_first11"] - 1
    assert n6["n_bars"] == 10 and n6["sep"] == 10805 and n6["oct"] == 4041
    N[6] = n6

    # ---------------------------------------------------------------- case 7
    c7 = pd.read_csv(D / "case07_stacked_products.csv")
    c7["d"] = pd.to_datetime(c7.month)
    P = c7[["product_a", "product_b", "product_c", "product_d"]]
    tot = P.sum(axis=1)
    base_d = P[["product_a", "product_b", "product_c"]].sum(axis=1)
    mid = c7.d >= "2024-07-01"
    dpc = P.product_d.pct_change()
    n7 = dict(c7=c7, P=P, tot_min=float(tot.min()), tot_max=float(tot.max()),
              sd=P.std().to_dict(), mean=P.mean().to_dict(),
              d_cv=float(P.product_d.std() / P.product_d.mean()),
              b_cv=float(P.product_b.std() / P.product_b.mean()),
              mad_d=float(P.product_d.diff().abs().mean()),
              mad_b=float(P.product_b.diff().abs().mean()),
              mad_base=float(base_d.diff().abs().mean()),
              corr_base_b=float(base_d.diff().corr(P.product_b.diff())),
              d_vol_before=float(dpc[~mid].std() * 100), d_vol_after=float(dpc[mid].std() * 100),
              d_range=float(P.product_d.max() - P.product_d.min()))
    assert round(n7["tot_min"]) == 548 and round(n7["tot_max"]) == 709
    N[7] = n7

    # ---------------------------------------------------------------- case 8
    c8 = pd.read_csv(D / "case08_channel_attrib.csv")
    tc = ["touch_search", "touch_social", "touch_email", "touch_direct"]
    nt = c8[tc].sum(axis=1)
    shares = (c8[tc].mean() * 100)
    sole = {c: float(((c8[c]) & (nt == 1)).sum() / len(c8) * 100) for c in tc}
    rev_sh = {c: float(c8.loc[c8[c], "revenue_pkr"].sum() / c8.revenue_pkr.sum() * 100) for c in tc}
    ex = __import__("tslib").exclusivity_check(c8, tc)
    n8 = dict(c8=c8, tc=tc, shares=shares.to_dict(), sum=float(shares.sum()), sole=sole,
              rev_sh=rev_sh, rev_sum=float(sum(rev_sh.values())), n=len(c8),
              n_multi=ex["n_multi"], pct_multi=ex["pct_multi"], n_zero=ex["n_zero"],
              exclusive=ex["exclusive"], n_one=int((nt == 1).sum()),
              pie_search_drawn=float(shares.iloc[0] / shares.sum() * 100),
              unique_ids=int(c8.customer_id.nunique()))
    assert [round(v, 1) for v in shares] == [42.6, 32.3, 27.5, 28.6]
    N[8] = n8

    # ---------------------------------------------------------------- case 9
    c9 = pd.read_csv(D / "case09_premium_share.csv")
    c9["share"] = c9.premium_revenue_pkr_m / c9.total_revenue_pkr_m * 100
    c9["other"] = c9.total_revenue_pkr_m - c9.premium_revenue_pkr_m
    n9 = dict(c9=c9, first=float(c9.share.iloc[0]), last=float(c9.share.iloc[-1]),
              prem_first=float(c9.premium_revenue_pkr_m.iloc[0]),
              prem_last=float(c9.premium_revenue_pkr_m.iloc[-1]),
              tot_first=float(c9.total_revenue_pkr_m.iloc[0]),
              tot_last=float(c9.total_revenue_pkr_m.iloc[-1]),
              oth_first=float(c9.other.iloc[0]), oth_last=float(c9.other.iloc[-1]))
    n9["prem_change"] = n9["prem_last"] / n9["prem_first"] - 1
    n9["tot_change"] = n9["tot_last"] / n9["tot_first"] - 1
    n9["oth_change"] = n9["oth_last"] / n9["oth_first"] - 1
    n9["recomputed_last"] = n9["prem_last"] / n9["tot_last"] * 100
    n9["prem_peak_quarter"] = str(c9.loc[c9.premium_revenue_pkr_m.idxmax(), "quarter"])
    assert round(n9["first"], 1) == 24.0 and round(n9["last"], 1) == 38.0
    N[9] = n9
    return N


# ================================================================ the diagnoses
def diagnoses(N: dict) -> dict:
    n1, n2, n3, n4, n5, n6, n7, n8, n9 = (N[i] for i in range(1, 10))
    T: dict = {}

    T[1] = dict(
        title="Orders peak in Q1 and collapse every year - a clear annual cycle",
        file="case01_orders_stringdate.csv",
        selfcheck=f"{n1['n']} points; drops of {n1['drops_txt'][0]} and {n1['drops_txt'][1]} - matches the brief.",
        conclusion="Orders have a strong annual rhythm: they build up and then crash at the turn of each year.",
        decoy=(f"My first thought was a genuine seasonal slump, with a different mix of riders or a "
               f"different branch in the quiet months. It doesn't hold: the branch column has "
               f"{n1['rider_branch_values']} value (it is constant), and once the months are in real "
               f"calendar order there are {n1['n_fall_fixed']} falling months out of 23. The smallest "
               f"month-on-month change is a rise of {n1['min_rise']:.0f} orders and the largest "
               f"{n1['max_rise']:.0f}. A seasonal slump would have to show up as at least one fall."),
        mechanism=(f"The month column is text written YYYY-M with no zero padding, so sorting it sorts "
                   f"characters, not dates: '2024-1' is followed by '2024-10', '2024-11', '2024-12' and only "
                   f"then '2024-2'. The first six x positions are {', '.join(n1['order_txt'])}. December "
                   f"2024 therefore lands in fourth place, directly before February 2024, which is where "
                   f"the 'collapse' of {n1['drops_txt'][0]} orders comes from (5,259 down to 4,301); the "
                   f"same thing happens a year later ({n1['drops_txt'][1]}). Parsed as dates, the number of "
                   f"falling steps goes from {n1['n_fall_txt']} to {n1['n_fall_fixed']}, and orders grow "
                   f"{n1['total_rise'] * 100:.1f}% from {n1['first']:,} to {n1['last']:,} over the 23 months."),
        redesign=("The same line chart on a real date axis (month parsed with format='%Y-%m'), y from zero. "
                  "It is a straight, steady climb with no annual cycle."),
    )

    T[2] = dict(
        title="Sales grew steadily, 22%, across the quarter",
        file="case02_shop_closed.csv",
        selfcheck=f"{n2['n']} points, first {n2['first']}, last {n2['last']}, {n2['rise'] * 100:+.0f}% - matches.",
        conclusion="The shop's sales climbed at a steady pace through January, February and March.",
        decoy=(f"The obvious objection is that the 69 rows over a 90-day quarter are just the shop's "
               f"regular days off (say closed Sundays), so the row number would be close enough to the date. "
               f"The calendar says otherwise. The {n2['n_missing']} missing days are one continuous closure, "
               f"{n2['gap_start'].strftime('%d %B')} to {n2['gap_end'].strftime('%d %B')} (contiguous: "
               f"{n2['gap_contiguous']}), and nothing else is missing: all {n2['n_pre']} days before it and all "
               f"{n2['n_post']} days after it are recorded ({n2['missing_outside_block']} missing days outside the "
               f"block). A regular weekly closure would leave a gap every seven days across the whole quarter, "
               f"not a single three-week block. (Counting how often each weekday is missing would not prove "
               f"this by itself - a 21-day block hits every weekday three times whatever the cause - so the "
               f"contiguity is the evidence.)"),
        mechanism=(f"Plotting against range(len(df)) deletes the closure: the 21 closed days are not on "
                   f"the axis at all, so the shop looks as if it traded 69 days in a row. Before the closure "
                   f"the {n2['n_pre']} trading days average {n2['pre_mean']:.0f}k and are, if anything, drifting "
                   f"down ({n2['slope_pre']:+.2f}k per day). After it the {n2['n_post']} days average "
                   f"{n2['post_mean']:.0f}k - a step of {n2['step'] * 100:+.1f}% that happened across the gap. "
                   f"The straight trend line smooths that step into a ramp: it reads {n2['slope_row']:.2f}k per "
                   f"row against {n2['slope_day']:.2f}k per real day, "
                   f"{n2['row_overstates'] * 100:.0f}% too steep."),
        redesign=("Real dates on the x axis with the closure left as an empty, labelled block, the line "
                  "broken there, and the two trading stretches shown with their means. Flat, then a step - "
                  "not a ramp."),
    )

    T[3] = dict(
        title="Peak load jumped 43% overnight on 1 July",
        file="case03_bandwidth_levels.csv",
        selfcheck=(f"June daily mean {n3['jun_mean_sum']:,.0f}, July {n3['jul_mean_sum']:,.0f}, "
                   f"{n3['sum_jump'] * 100:+.0f}% - matches."),
        conclusion="Demand for the service stepped up by about 43% on 1 July (a launch, a campaign, a new customer).",
        decoy=(f"The first thing I checked was whether the jump is real, because the other column, "
               f"bytes_served, jumps by almost exactly the same amount when summed daily "
               f"({n3['bytes_sum_jump'] * 100:+.1f}%) - which looks like confirmation. It isn't: both columns "
               f"are being added up over a different number of recorded hours. Per recorded hour, bytes "
               f"change by {n3['bytes_per_hour_change'] * 100:+.1f}%, not +43%."),
        mechanism=(f"concurrent_users is a level - how many people are connected at an instant - so adding "
                   f"it up over a day counts observations, not users. June is missing "
                   f"{n3['jun_hours_possible'] - n3['jun_hours']} of its {n3['jun_hours_possible']} hours "
                   f"(an average of {n3['jun_obs_per_day']:.1f} recorded hours a day), while July is complete "
                   f"({n3['jul_obs_per_day']:.0f} a day). The 'jump' lands exactly on 1 July because that is "
                   f"when the logging became complete. Per recorded hour, users went from "
                   f"{n3['per_hour_jun']:.0f} to {n3['per_hour_jul']:.0f} "
                   f"({n3['per_hour_change'] * 100:+.1f}%); comparing the same hours of the day it is "
                   f"{n3['matched_hours_change'] * 100:+.1f}%. A level should be resampled with mean() (or "
                   f"max()), never sum()."),
        redesign=("Two stacked panels sharing the date axis (no dual axis): the daily mean of concurrent users "
                  "per recorded hour, flat across 1 July; and the number of hours logged per day, which is "
                  "what actually stepped."),
    )

    t4 = n4
    T[4] = dict(
        title="The new checkout flow started working on 7 September",
        file="case04_intervention_lag.csv",
        selfcheck=f"trailing 31-day mean bottoms out on {t4['trailing_min'].date()} - matches.",
        conclusion="Conversion only started to recover on 7 September, so the new flow took effect then.",
        decoy=(f"My first objection was that maybe the new flow really did take weeks to bite - an adoption "
               f"delay - so 7 September could still be right. The data rules it out: if the delay were real "
               f"it would not depend on the smoother, but it does, and by exactly the same arithmetic every "
               f"time. The trailing minimum arrives {t4['lags'][7][0]} days after the centred one with a 7-day "
               f"window (half-window {t4['lags'][7][1]}), {t4['lags'][15][0]} with 15 "
               f"(half {t4['lags'][15][1]}), {t4['lags'][31][0]} with 31 (half {t4['lags'][31][1]}) and "
               f"{t4['lags'][61][0]} with 61 (half {t4['lags'][61][1]})."),
        mechanism=(f"A trailing mean at day t averages days t-30 to t, so it cannot register a turn until "
                   f"enough post-turn days are inside the window. The centred 31-day mean bottoms out on "
                   f"{t4['centred_min'].strftime('%d %b')} and the centred 7-day mean on {t4['ce7_min'].strftime('%d %b')}. "
                   f"A piecewise-linear trend fitted to the raw series puts its estimated break at "
                   f"{t4['pw_break'].strftime('%d %b')} - that is where a fitted line changes slope, an estimate and "
                   f"not proof of the day the new flow began working (the file contains no launch date). Together "
                   f"they place the turn in late August. The trailing 31-day mean only bottoms out on "
                   f"{t4['trailing_min'].strftime('%d %b')}, {t4['lag31']} days after the centred minimum, which "
                   f"is the half-window lag - so the 7 September on the chart comes from the smoothing and does not "
                   f"tell us when the effect began."),
        redesign=(f"Raw in grey with both the centred and the trailing 31-day mean, their minima marked, and the "
                  f"{t4['lag31']}-day gap labelled. The honest statement is 'late August' - an estimate from the smoothed "
                  f"and fitted series, not an exact date - and the chart says which window it used."),
    )

    T[5] = dict(
        title="Revenue has fallen for six straight months",
        file="case05_revenue_window.csv",
        selfcheck=(f"{n5['n']} points, {n5['first']:.1f} down to {n5['last']:.1f}, "
                   f"{n5['fall'] * 100:+.1f}% - matches."),
        conclusion="The business is in a steep, sustained decline.",
        decoy=(f"There are two tempting objections. 'The axis is truncated' - it isn't; the recipe starts "
               f"at zero. 'Seven points is too few' - that is not the real problem either: more months from the "
               f"same stretch would still run from peak to trough, and the {n5['straight_falls']} consecutive "
               f"month-on-month falls are genuine. What matters is which seven months were picked and what the "
               f"same months do in other years; the file has {n5['n_total']} months to compare against."),
        mechanism=(f"The seven months run from a seasonal peak to a seasonal trough. In every one of "
                   f"the three years the high is in May or June (month {n5['years'][2023]['peak_month']}, "
                   f"{n5['years'][2024]['peak_month']}, {n5['years'][2025]['peak_month']}) and the low is "
                   f"November (month {n5['years'][2023]['trough_month']}, {n5['years'][2024]['trough_month']}, "
                   f"{n5['years'][2025]['trough_month']}). Comparing the same May-to-November window across the years, "
                   f"the fall is "
                   f"{n5['years'][2023]['fall'] * 100:+.1f}% in 2023, {n5['years'][2024]['fall'] * 100:+.1f}% in "
                   f"2024 and {n5['years'][2025]['fall'] * 100:+.1f}% in 2025 - about the same every year, so 2025's fall "
                   f"is the usual seasonal one. Meanwhile 2025 is "
                   f"{n5['yoy_may'] * 100:+.1f}% above 2024 in May and {n5['yoy_nov'] * 100:+.1f}% in November, "
                   f"and the full-year total is {n5['annual_growth'] * 100:+.1f}%."),
        redesign=("The same May-to-November window drawn for all three years on one axis, y from zero. The "
                  "2025 line has the same shape as 2023 and 2024 (a fall of about 42%) and sits above both."),
    )

    T[6] = dict(
        title="Orders collapsed in October",
        file="case06_monthly_partial.csv",
        selfcheck=(f"{n6['n_bars']} bars; September {n6['sep']:,}, October {n6['oct']:,} "
                   f"({n6['oct_over_sep'] * 100:.0f}% of it) - matches."),
        conclusion="Something went badly wrong in October: orders fell by nearly two-thirds.",
        decoy=(f"The natural objection is a real operational shock (a stock-out, an outage) - a 63% fall "
               f"would be a real incident. The daily rows say otherwise: the lowest single October day is "
               f"{n6['oct_daily_min']} orders, against a September average of {n6['sep_daily_mean']:.0f} a day. "
               f"There is no day that looks like a collapse."),
        mechanism=(f"The extract was taken on {n6['last_day']}, so October has {n6['oct_days']} of its "
                   f"{n6['oct_possible']} days, and resample('MS').sum() adds up whatever it finds. Per day, "
                   f"October averages {n6['oct_rate']:.0f} against {n6['sep_rate']:.0f} in September, and "
                   f"{n6['oct_rate']:.0f} is the highest rate of any month in the file "
                   f"(previous best {n6['best_prev_rate']:.0f}). Like for like, the first 11 days of October "
                   f"({n6['oct_first11']:,}) against the first 11 of September ({n6['sep_first11']:,}) is "
                   f"{n6['like_for_like'] * 100:+.1f}%."),
        redesign=("Orders per trading day by month (a rate, so months of different length compare), with "
                  "October hatched and labelled '11 days only'."),
    )

    T[7] = dict(
        title="Product D has been erratic since mid-2024",
        file="case07_stacked_products.csv",
        selfcheck=(f"stacked envelope runs {n7['tot_min']:.0f} to {n7['tot_max']:.0f} - matches "
                   f"(about 548 to 709)."),
        conclusion="Product D, the top band, has become unstable in the second half of the series.",
        decoy=(f"The first objection is that D really did become erratic and the chart is just showing it. "
               f"So I looked at D by itself: it varies by {n7['d_cv'] * 100:.1f}% of its mean "
               f"(sd {n7['sd']['product_d']:.1f} on a mean of {n7['mean']['product_d']:.0f}), moves "
               f"{n7['mad_d']:.1f} a month on average, and its month-on-month volatility is "
               f"{n7['d_vol_before']:.1f}% before July 2024 and {n7['d_vol_after']:.1f}% after - no change."),
        mechanism=(f"In a stacked area each band's edges are cumulative sums, so a band floats on everything "
                   f"beneath it. D sits on top of A+B+C, and that baseline moves "
                   f"{n7['mad_base']:.1f} a month on average, because Product B is wild "
                   f"(sd {n7['sd']['product_b']:.1f}, {n7['mad_b']:.1f} a month; month-to-month changes of the "
                   f"baseline and of B correlate at {n7['corr_base_b']:.2f}). D's own thickness changes "
                   f"{n7['mad_d']:.1f} a month. The eye reads D's wobbling upper edge as D's shape, but "
                   f"that edge is B's volatility passed upward. The column the recipe never isolates is "
                   f"product_b."),
        redesign=("Unstack it: the four products as separate lines on one shared axis, from zero, "
                  "labelled directly. D is nearly flat; B is the erratic one."),
    )

    T[8] = dict(
        title="Paid search drives 43% of our customers",
        file="case08_channel_attrib.csv",
        selfcheck=("search {:.1f}%, social {:.1f}%, email {:.1f}%, direct {:.1f}% - matches.".format(*n8["shares"].values())),
        conclusion="Paid search is the single biggest source of customers, bringing in roughly 43% of them.",
        decoy=(f"I wondered whether weighting by revenue would sort out the arithmetic. It doesn't: the "
               f"revenue-weighted shares are search {n8['rev_sh']['touch_search']:.1f}%, "
               f"social {n8['rev_sh']['touch_social']:.1f}%, email {n8['rev_sh']['touch_email']:.1f}%, "
               f"direct {n8['rev_sh']['touch_direct']:.1f}% and they add to {n8['rev_sum']:.1f}%. "
               f"Nor is it duplicate rows: all {n8['unique_ids']:,} customer ids are unique."),
        mechanism=(f"The four shares sum to {n8['sum']:.1f}%, and the first thing to do with a set of shares is "
                   f"add them. The columns are 'touched by this channel at any point', not 'came from this "
                   f"channel', so they overlap: {n8['n_multi']:,} of {n8['n']:,} customers "
                   f"({n8['pct_multi']:.1f}%) were touched by two or more channels (exclusive: "
                   f"{n8['exclusive']}). The parts therefore cannot be mutually exclusive slices of one whole "
                   f"(slide 32's first condition), and a pie chart is inappropriate for these overlapping "
                   f"categories. matplotlib hides this by normalising the slices: search is labelled 42.6% "
                   f"but drawn as {n8['pie_search_drawn']:.1f}% of the circle. Only "
                   f"{n8['sole']['touch_search']:.1f}% of customers were touched by search alone."),
        redesign=("Horizontal bars of 'reached by this channel', each split into 'this channel only' and "
                  "'this and at least one other', with the 131% total stated. Same data, but the overlap is "
                  "now visible."),
    )

    T[9] = dict(
        title="Premium is now 38% of revenue - a record",
        file="case09_premium_share.csv",
        selfcheck=f"share rises from {n9['first']:.1f}% to {n9['last']:.1f}% - matches.",
        conclusion="Premium is growing and has taken over a record share of the business.",
        decoy=(f"I rechecked the arithmetic first, in case the share was miscomputed: "
               f"{n9['prem_last']:.1f} / {n9['tot_last']:.0f} = {n9['recomputed_last']:.1f}%. It is right. "
               f"The chart isn't lying about the share; it is silent about what the share is a share of."),
        mechanism=(f"Premium revenue did not grow. It went from {n9['prem_first']:.1f} to {n9['prem_last']:.1f} "
                   f"({n9['prem_change'] * 100:+.1f}%) - highest in {n9['prem_peak_quarter']} and about 228 since "
                   f"2024Q4 - while total revenue went from {n9['tot_first']:,.0f} to {n9['tot_last']:,.0f} "
                   f"({n9['tot_change'] * 100:+.0f}%), and everything that is not premium fell "
                   f"{abs(n9['oth_change']) * 100:.0f}%. The share rose because the denominator collapsed, not "
                   f"because the numerator grew: the numerator actually fell slightly. This is the chart that is "
                   f"incomplete, not wrong."),
        redesign=("The same share line, with the two absolute series beside it: premium revenue and total "
                  "revenue in PKR m, y from zero. 'Record share' sits next to 'falling business'."),
    )
    return T


# ================================================================ published charts
def pub1(fig, spec, N):
    n = N[1]
    ax = fig.add_subplot(spec)
    ax.plot(range(n["n"]), n["txt"].orders, color=BLUE, marker="o", markersize=3.5)
    ax.set_ylim(0, None)
    ax.set_xticks(range(0, n["n"], 2), n["txt"].month[::2], rotation=60, fontsize=6.5)
    ttl(ax, '1: "Orders peak in Q1 and collapse every year"')
    ax.set_ylabel("Orders per month")
    ax.set_xlabel("month column, sorted as text")


def pub2(fig, spec, N):
    n = N[2]
    ax = fig.add_subplot(spec)
    x = np.arange(n["n"])
    ax.plot(x, n["df"].sales_pkr_k, color=BLUE, marker="o", markersize=2.5, linewidth=1)
    m, b = np.polyfit(x, n["df"].sales_pkr_k, 1)
    ax.plot(x, m * x + b, color=ORANGE, linewidth=2)
    ax.annotate(f"+{n['rise'] * 100:.0f}%", xy=(n["n"] - 1, n["last"]), xytext=(n["n"] * 0.80, n["last"] - 45),
                fontsize=9, color=INK)
    ax.set_ylim(0, 290)
    ttl(ax, '2: "Sales grew steadily, 22%, across the quarter"')
    ax.set_ylabel("Sales (PKR thousands)")
    ax.set_xlabel("row number")


def pub3(fig, spec, N):
    n = N[3]
    ax = fig.add_subplot(spec)
    ax.plot(n["dsum"].index, n["dsum"].values, color=BLUE)
    ax.set_ylim(0, None)
    kfmt(ax)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ttl(ax, '3: "Peak load jumped 43% overnight on 1 July"')
    ax.set_ylabel("concurrent_users, resampled with sum()")
    ax.tick_params(axis="x", labelsize=7)


def pub4(fig, spec, N):
    n = N[4]
    ax = fig.add_subplot(spec)
    ax.plot(n["s"].index, n["s"].values, color=GREY, linewidth=0.8)
    ax.plot(n["tr31"].index, n["tr31"].values, color=BLUE, linewidth=2)
    ax.axvline(n["trailing_min"], color=ORANGE, linestyle="--")
    ax.text(n["trailing_min"], n["s"].max() * 0.98, " 7 Sep", color=ORANGE, fontsize=8, va="top")
    ttl(ax, '4: "The new checkout started working on 7 September"')
    ax.set_ylabel("Conversion, %")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.text(0.02, 0.04, "grey: raw   blue: 31-day trailing mean", transform=ax.transAxes, fontsize=7.5, color=SOFT)


def pub5(fig, spec, N):
    n = N[5]
    ax = fig.add_subplot(spec)
    ax.plot(n["win"].d, n["win"].revenue_pkr_m, color=BLUE, marker="o")
    ax.set_ylim(0, 180)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ttl(ax, '5: "Revenue has fallen for six straight months"')
    ax.set_ylabel("Revenue (PKR m)")
    ax.set_xlabel("May to November 2025")


def pub6(fig, spec, N):
    n = N[6]
    ax = fig.add_subplot(spec)
    ax.bar(n["msum"].index.strftime("%b"), n["msum"].values, color=BLUE)
    ax.set_ylim(0, None)
    kfmt(ax)
    ttl(ax, '6: "Orders collapsed in October"')
    ax.set_ylabel("Orders per month, sum()")


def pub7(fig, spec, N):
    n = N[7]
    ax = fig.add_subplot(spec)
    ax.stackplot(n["c7"].d, [n["P"][c] for c in n["P"].columns],
                 colors=[BLUE, ORANGE, GREEN, PINK], labels=["A", "B", "C", "D"], linewidth=0)
    ax.legend(loc="lower left", ncol=4, fontsize=7)
    ttl(ax, '7: "Product D has been erratic since mid-2024"')
    ax.set_ylabel("Revenue (PKR m), stacked")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))


def pub8(fig, spec, N):
    n = N[8]
    ax = fig.add_subplot(spec)
    vals = list(n["shares"].values())
    names = [c.replace("touch_", "") for c in n["tc"]]
    ax.pie(vals, labels=[f"{nm}\n{v:.1f}%" for nm, v in zip(names, vals)],
           colors=[BLUE, ORANGE, GREEN, PINK], startangle=90, counterclock=False,
           wedgeprops=dict(edgecolor="white"), textprops=dict(fontsize=8))
    ttl(ax, '8: "Paid search drives 43% of our customers"')


def pub9(fig, spec, N):
    n = N[9]
    ax = fig.add_subplot(spec)
    ax.plot(n["c9"].quarter, n["c9"].share, color=BLUE, marker="o")
    ax.set_ylim(0, 45)
    ax.annotate(f"{n['last']:.1f}%", xy=(7, n["last"]), xytext=(5.9, n["last"] + 4), fontsize=9)
    ttl(ax, '9: "Premium is now 38% of revenue - a record"')
    ax.set_ylabel("Premium share of revenue, %")
    ax.tick_params(axis="x", labelsize=7, rotation=45)


# =================================================================== redesigns
def red1(fig, spec, N):
    n = N[1]
    f = n["fixed"]
    ax = fig.add_subplot(spec)
    ax.plot(f.d, f.orders, color=BLUE, marker="o", markersize=3.5)
    ax.set_ylim(0, None)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    ttl(ax, f"1: Orders rose every month - {n['total_rise'] * 100:+.0f}% in 23 months, no collapse")
    ax.set_ylabel("Orders per month")
    ax.set_xlabel("Month (parsed as a date, in calendar order)")
    ax.text(0.03, 0.06, f"falling months: {n['n_fall_txt']} as drawn  ->  {n['n_fall_fixed']} sorted",
            transform=ax.transAxes, fontsize=8, color=SOFT)


def red2(fig, spec, N):
    n = N[2]
    df = n["df"]
    ax = fig.add_subplot(spec)
    ax.axvspan(n["gap_start"], n["gap_end"] + pd.Timedelta(days=1), color=PALETTE["grid"], zorder=0)
    ax.text(n["gap_start"] + (n["gap_end"] - n["gap_start"]) / 2, 163,
            f"closed\n{n['n_missing']} days", ha="center", fontsize=8, color=SOFT)
    pre, post = df[df.date < n["gap_start"]], df[df.date > n["gap_end"]]
    for seg, colr in ((pre, BLUE), (post, BLUE)):
        ax.plot(seg.date, seg.sales_pkr_k, color=colr, marker="o", markersize=2.5, linewidth=1)
    ax.hlines(n["pre_mean"], pre.date.min(), pre.date.max(), color=ORANGE, linewidth=2)
    ax.hlines(n["post_mean"], post.date.min(), post.date.max(), color=ORANGE, linewidth=2)
    ax.text(pre.date.min(), n["pre_mean"] - 14, f"mean {n['pre_mean']:.0f}k", fontsize=8, color=INK)
    ax.text(post.date.min() + pd.Timedelta(days=8), n["post_mean"] + 8, f"mean {n['post_mean']:.0f}k",
            fontsize=8, color=INK)
    ax.set_ylim(150, 275)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ttl(ax, f"2: Flat, then a {n['step'] * 100:.0f}% step across the closure - not steady growth")
    ax.set_ylabel("Sales (PKR thousands)")
    ax.set_xlabel("Date (calendar days; gap kept)")


def red3(fig, spec, N):
    n = N[3]
    sub = spec.subgridspec(2, 1, height_ratios=[2.2, 1], hspace=0.12)
    a1 = fig.add_subplot(sub[0])
    a2 = fig.add_subplot(sub[1], sharex=a1)
    dm = n["daily_mean"]
    a1.plot(dm.index, dm.values, color=BLUE)
    a1.axvline(pd.Timestamp("2025-07-01"), color=GREY, linestyle=":")
    a1.set_ylim(0, None)
    a1.set_ylabel("Users per\nrecorded hour (mean)")
    ttl(a1, f"3: Users per hour barely moved ({n['per_hour_change'] * 100:+.0f}%); what jumped on 1 July "
                 f"was the hours logged")
    plt.setp(a1.get_xticklabels(), visible=False)
    a2.bar(n["cnt"].index, n["cnt"].values, color=GREY, width=0.9)
    a2.axvline(pd.Timestamp("2025-07-01"), color=GREY, linestyle=":")
    a2.set_ylabel("Hours logged\nper day")
    a2.set_ylim(0, 26)
    a2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    a2.tick_params(axis="x", labelsize=7)


def red4(fig, spec, N):
    n = N[4]
    ax = fig.add_subplot(spec)
    ax.plot(n["s"].index, n["s"].values, color=GREY, linewidth=0.8)
    ax.plot(n["ce31"].index, n["ce31"].values, color=BLUE, linewidth=2, label="31-day centred mean")
    ax.plot(n["tr31"].index, n["tr31"].values, color=ORANGE, linewidth=2, label="31-day trailing mean")
    ax.plot([n["centred_min"]], [n["ce31"].min()], marker="o", color=BLUE, markersize=6, linestyle="none")
    ax.plot([n["trailing_min"]], [n["tr31"].min()], marker="s", color=ORANGE, markersize=6, linestyle="none")
    ax.set_ylim(n["s"].min() - 0.22, None)
    y = n["s"].min() - 0.08
    ax.annotate("", xy=(n["trailing_min"], y), xytext=(n["centred_min"], y),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
    ax.text(n["centred_min"] + (n["trailing_min"] - n["centred_min"]) / 2, y - 0.05,
            f"{n['lag31']} days", ha="center", va="top", fontsize=8)
    ttl(ax, f"4: The smoothed data turn in late August - the trailing mean reports it {n['lag31']} days late")
    ax.set_ylabel("Conversion, %")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.legend(loc="upper right", fontsize=7.5)


def red5(fig, spec, N):
    n = N[5]
    ax = fig.add_subplot(spec)
    cols = {2023: BLUE, 2024: GREEN, 2025: ORANGE}
    for i, (y, c) in enumerate(cols.items()):
        s = n["years"][y]["series"].loc[5:11]
        ax.plot(s.index, s.values, color=c, marker=MARKERS[i], linewidth=2.2 if y == 2025 else 1.6,
                label=f"{y}")
        ax.text(11.12, s.loc[11], f"{y}: {n['years'][y]['fall'] * 100:+.0f}%", fontsize=8, va="center", color=INK)
    ax.set_xlim(4.8, 12.9)
    ax.set_ylim(0, 180)
    ax.set_xticks(range(5, 12), ["May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"])
    ttl(ax, "5: Every year falls ~42% from May to November - 2025 is still the highest year")
    ax.set_ylabel("Revenue (PKR m)")
    ax.legend(loc="lower left", fontsize=7.5, ncol=3)


def red6(fig, spec, N):
    n = N[6]
    ax = fig.add_subplot(spec)
    pdy = n["per_day"]
    bars = ax.bar(pdy.index.strftime("%b"), pdy.values, color=BLUE)
    bars[-1].set_hatch("///")
    bars[-1].set_edgecolor("white")
    bars[-1].set_facecolor(BLUE)
    ax.text(len(pdy) - 1, pdy.iloc[-1] + 8, f"{pdy.iloc[-1]:.0f}\n({n['oct_days']} days only)", ha="center",
            fontsize=8, color=INK)
    ax.set_ylim(0, pdy.max() * 1.25)
    ttl(ax, f"6: October is running at {n['oct_rate']:.0f} orders a day - the best month yet")
    ax.set_ylabel("Orders per trading day (mean)")


def red7(fig, spec, N):
    n = N[7]
    ax = fig.add_subplot(spec)
    cols = [BLUE, ORANGE, GREEN, PINK]
    for i, c in enumerate("abcd"):
        s = n["P"][f"product_{c}"]
        ax.plot(n["c7"].d, s, color=cols[i], marker=MARKERS[i], markersize=3, linewidth=1.6)
        dy = {"b": -9, "c": 7}.get(c, 0)
        ax.text(n["c7"].d.iloc[-1] + pd.Timedelta(days=25), s.iloc[-1] + dy, f"Product {c.upper()}",
                fontsize=8, va="center", color=INK)
    ax.set_ylim(0, None)
    ax.set_xlim(None, n["c7"].d.iloc[-1] + pd.Timedelta(days=190))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    ttl(ax, "7: Product B is the erratic one; D barely moves")
    ax.set_ylabel("Revenue (PKR m)")


def red8(fig, spec, N):
    n = N[8]
    ax = fig.add_subplot(spec)
    names = [c.replace("touch_", "") for c in n["tc"]]
    reached = np.array([n["shares"][c] for c in n["tc"]])
    sole = np.array([n["sole"][c] for c in n["tc"]])
    shared = reached - sole
    order = np.argsort(reached)
    y = np.arange(4)
    ax.barh(y, sole[order], color=BLUE, label="this channel only")
    ax.barh(y, shared[order], left=sole[order], color=GREY, label="this + at least one other")
    for yi, r in zip(y, reached[order]):
        ax.text(r + 0.8, yi, f"{r:.1f}%", va="center", fontsize=8)
    ax.set_yticks(y, [names[i] for i in order])
    ax.set_xlim(0, 55)
    ax.set_xlabel("% of customers touched by the channel")
    ttl(ax, f"8: Search reached 43% but only {n['sole']['touch_search']:.0f}% through search alone - "
                 f"reach adds to {n['sum']:.0f}%")
    ax.legend(loc="lower right", fontsize=7.5)
    ax.grid(axis="y", visible=False)


def red9(fig, spec, N):
    n = N[9]
    c9 = n["c9"]
    ax0 = fig.add_subplot(spec)
    ax0.axis("off")
    ttl(ax0, f"9: Premium share is up because the rest of the business fell - premium revenue "
             f"{n['prem_change'] * 100:+.0f}%, total {n['tot_change'] * 100:+.0f}%")
    a1 = ax0.inset_axes([0.10, 0.24, 0.34, 0.62])
    a2 = ax0.inset_axes([0.64, 0.24, 0.28, 0.62])
    a1.plot(c9.quarter, c9.share, color=BLUE, marker="o")
    a1.set_ylim(0, 45)
    a1.set_ylabel("Premium share, %")
    a1.tick_params(axis="x", labelsize=6.5, rotation=60)
    a1.set_title("the share (as published)", fontsize=8.5)
    a2.plot(c9.quarter, c9.total_revenue_pkr_m, color=GREY, marker="s", linewidth=2)
    a2.plot(c9.quarter, c9.premium_revenue_pkr_m, color=ORANGE, marker="o", linewidth=2)
    a2.text(7.2, c9.total_revenue_pkr_m.iloc[-1] + 60, f"total {n['tot_change'] * 100:+.0f}%", fontsize=7.5, va="bottom", ha="right")
    a2.text(7.2, c9.premium_revenue_pkr_m.iloc[-1] + 60, f"premium {n['prem_change'] * 100:+.0f}%", fontsize=7.5, va="bottom", ha="right")
    a2.set_ylim(0, 1100)
    a2.set_ylabel("Revenue (PKR m)")
    a2.tick_params(axis="x", labelsize=6.5, rotation=60)
    a2.set_title("what it is a share of", fontsize=8.5)


PUB = [pub1, pub2, pub3, pub4, pub5, pub6, pub7, pub8, pub9]
RED = [red1, red2, red3, red4, red5, red6, red7, red8, red9]
SRC_NOTE = {
    1: "case01_orders_stringdate.csv, n = 24 months", 2: "case02_shop_closed.csv, n = 69 trading days of 90",
    3: "case03_bandwidth_levels.csv, n = 1,237 hourly rows", 4: "case04_intervention_lag.csv, n = 214 days",
    5: "case05_revenue_window.csv, n = 36 months (7 shown in the published chart)",
    6: "case06_monthly_partial.csv, n = 284 days, to 11 Oct 2025", 7: "case07_stacked_products.csv, n = 36 months",
    8: "case08_channel_attrib.csv, n = 4,000 customers", 9: "case09_premium_share.csv, n = 8 quarters",
}


def main():
    style_defaults()
    N = compute()
    T = diagnoses(N)

    say("=" * 74)
    say("PART A - nine charts: rebuild, decoy, mechanism, redesign")
    say("=" * 74)
    for i in range(1, 10):
        t = T[i]
        say("")
        say(f"CASE {i} - \"{t['title']}\"   [{t['file']}]")
        say(f"  SELF-CHECK  {t['selfcheck']}")
        say(f"  CONCLUSION  {t['conclusion']}")
        say(f"  DECOY       {t['decoy']}")
        say(f"  MECHANISM   {t['mechanism']}")
        say(f"  REDESIGN    {t['redesign']}")

    # one Lie Factor example for the record: case 6's bar for October vs September
    lf, de, ge = lie_factor(N[6]["sep"], N[6]["oct"], N[6]["sep"], N[6]["oct"], 1)
    say("")
    say(f"(Lie Factor note, case 6: the bars are drawn honestly from zero, so LF = {lf:.2f} - the ink matches "
        f"the sum. The chart is accurate about the wrong quantity, which is why no ink-based test finds it.)")

    # ------------------------------------------------------------ figures
    for tag, funcs, fname in (("published", PUB, "partA_published_all.png"),
                              ("redesign", RED, "partA_redesigns_all.png")):
        fig = plt.figure(figsize=(19, 15), layout="constrained")
        gs = fig.add_gridspec(3, 3)
        for i, fn in enumerate(funcs):
            fn(fig, gs[i // 3, i % 3], N)
        save_fig(fig, HERE / fname,
                 note=(f"Nine charts {'as the analysts published them (rebuilt from their recipes)' if tag == 'published' else 'redesigned'}. "
                       "Synthetic data generated for CDB601220 (Data Visualization, Week 4); sources and n for each case are in "
                       "partA_output.txt."))
        plt.close(fig)
        say(f"saved {fname} at 300 dpi")

        for i, fn in enumerate(funcs, start=1):
            f1 = plt.figure(figsize=(5.6, 3.9), layout="constrained")
            fn(f1, f1.add_gridspec(1, 1)[0], N)
            save_fig(f1, FIGS / f"case{i:02d}_{tag}.png",
                     note=f"Synthetic course data (CDB601220). {SRC_NOTE[i]}.")
            plt.close(f1)
    say(f"saved 18 single-case figures in {FIGS.name}/ at 300 dpi")

    out = {str(i): {k: v for k, v in T[i].items()} for i in T}
    (HERE / "partA_diagnosis.json").write_text(json.dumps(out, indent=1))
    say.close()


if __name__ == "__main__":
    main()