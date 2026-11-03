"""
Week 6 - Task B: three charts, three different questions.

    python3 partA_process.py      # once, writes clean/
    python3 partB_charts.py       # writes partB_1.png, partB_2.png, partB_3.png

I picked three kinds of question on purpose, so no two charts are doing the
same job:

    partB_1   TREND         grid_daily     -> how does demand move through the year?
    partB_2   COMPOSITION   generation_mix -> is the solar shift real, or arithmetic?
    partB_3   RELATIONSHIP  district_grid  -> where does rooftop solar actually go?

Everything the picture depends on (window, aggregation, exclusions, the
"everything else" bucket) is printed in the source note under each figure.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import vizlib                       # noqa: E402
from vizlib import PALETTE          # noqa: E402

CLEAN = HERE / "clean"
for need in ("grid_daily_clean.csv", "zone_month_energy.csv",
             "generation_parts.csv", "district_grid_clean.csv"):
    if not (CLEAN / need).exists():
        sys.exit(f"clean/{need} is missing - run partA_process.py first.")

import textwrap


def wrap(txt, width):
    """wrap each paragraph of a source note so it never widens the figure"""
    return "\n".join(textwrap.fill(p, width) for p in txt.split("\n"))


vizlib.style_defaults()
BLUE, ORANGE, GREEN = PALETTE["series"]
GREY, INK, SOFT = PALETTE["muted"], PALETTE["ink"], PALETTE["ink_soft"]

# ---------------------------------------------------------------- colour check
# I do not trust "it came from Okabe-Ito". Test every pair I actually put on a
# chart, under all three colour-vision simulations, and print it.
print("colour-vision check on the pairs these charts use")
for name, pal in [("B1  blue + orange (line, peak marker)", [BLUE, ORANGE]),
                  ("B2  orange + grey (solar vs the rest)", [ORANGE, GREY]),
                  ("B3  blue + orange + grey (points, flagged, fit)",
                   [BLUE, ORANGE, GREY])]:
    for kind in ("protan", "deutan", "tritan"):
        i, j, a, b, d = vizlib.worst_pair(pal, kind)
        print(f"   {name:<52}{kind:<7} worst pair dE {d:5.1f}  "
              f"{vizlib.verdict(d)}")
print("   (anything under 8 gets a second channel: a direct label, a marker "
      "shape or a gap - see each chart)\n")


# =========================================================================
# B1  TREND - how does demand move through the year?
# =========================================================================
me = pd.read_csv(CLEAN / "zone_month_energy.csv")
daily = pd.read_csv(CLEAN / "grid_daily_clean.csv", parse_dates=["date"])

# Sept 2026 is only 11 days long in the file, so it stays out of a chart of
# MONTHLY totals. A partial month drawn like a full one is a deduction.
full = me[me.complete].copy()
full["month"] = pd.to_datetime(full.month + "-01")
piv = (full.pivot(index="month", columns="zone", values="energy_mwh") / 1e6)
n_part = int((~me.complete).sum() // 6)

# how many month-boundary readings were not on file and had to be interpolated
_firsts = daily[daily.date.dt.day == 1]
first_of_month = set(zip(_firsts.zone, _firsts.date))
need = {(z, m) for z in piv.columns
        for m in pd.date_range("2025-04-01", "2026-09-01", freq="MS")}
n_interp = len(need - first_of_month)

peak = piv.max()
peak_month = piv.idxmax()
trough = piv.min()
drop = (1 - trough / peak) * 100
print("B1 peak / trough per zone")
print(pd.DataFrame({"peak_month": peak_month.dt.strftime("%Y-%m"),
                    "peak_TWh": peak.round(2), "trough_TWh": trough.round(2),
                    "trough_below_peak_%": drop.round(1)}).to_string())
all_july = bool((peak_month.dt.month == 7).all())
assert all_july, "the title says every zone peaks in July - it does not"

fig, axes = plt.subplots(2, 3, figsize=(11.2, 6.4), sharex=True)
for ax, z in zip(axes.ravel(), piv.columns):
    s = piv[z]
    ax.plot(s.index, s.values, color=BLUE, marker="o", ms=3.5, lw=1.8)
    # peak, marked in orange AND labelled, so the colour is never the only cue
    pm = peak_month[z]
    ax.plot([pm], [peak[z]], marker="s", ms=7, color=ORANGE, zorder=5,
            linestyle="none")
    ax.annotate(f"{peak[z]:.2f}", (pm, peak[z]), xytext=(0, 8),
                textcoords="offset points", ha="center", fontsize=8,
                color=ORANGE, fontweight="bold")
    ax.set_title(f"{z}", fontsize=10.5, color=INK)
    ax.set_ylim(0, peak[z] * 1.22)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.tick_params(axis="x", labelsize=7.5)
    if s.isna().any():
        gap = s.index[s.isna()][0]
        ax.annotate("meter replaced\n17 Feb: no figure", (gap, 0),
                    xytext=(0, 18), textcoords="offset points", ha="center",
                    fontsize=7, color=SOFT,
                    arrowprops=dict(arrowstyle="-", color=SOFT, lw=0.7))
for ax in axes[:, 0]:
    ax.set_ylabel("TWh per month", fontsize=8.5)
lo, hi = drop.min(), drop.max()
fig.suptitle(f"Every zone peaks in July and sinks {lo:.0f}-{hi:.0f}% lower in "
             "winter, with the same shape each time",
             x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK,
             y=1.0)
fig.text(0.01, 0.945,
         "Supports: schedule planned maintenance outages for Dec-Feb, when "
         "every zone is furthest from its July peak.",
         fontsize=9.5, color=SOFT, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.93))
note1 = (
    "Source: grid_daily.csv, 6 zones, cleaned by partA_process.py (3,046 zone-days; 128 never reported). Synthetic data, CDB601220 Week 6.\n"
    "Energy per month = meter reading on the 1st of next month minus reading on the 1st of this month (a reading is a level, never summed). "
    f"{n_interp} boundary readings were not on file and are interpolated within the same meter.\n"
    f"Window: Apr 2025 - Aug 2026, {len(piv)} complete months. Sep 2026 left out: only 11 days in the file (partial). "
    "P4 Feb 2026 left blank: the meter was replaced on 17 Feb and the step is unknowable. Each panel has its own y scale starting at 0. "
    "Orange square = that zone's peak month.")
vizlib.save_fig(fig, HERE / "partB_1.png", note=wrap(note1, 190))
plt.close(fig)
print("wrote partB_1.png\n")


# =========================================================================
# B2  COMPOSITION - is the shift to renewables real, or is it arithmetic?
# =========================================================================
g = pd.read_csv(CLEAN / "generation_parts.csv")
mx = g.pivot_table(index="month", columns="subsource", values="mwh",
                   aggfunc="sum")
solar = mx["Solar"]
rest = mx.drop(columns="Solar").sum(axis=1)
total = solar + rest

a, b = "2025-04", "2026-09"
tot_chg = total[b] / total[a] - 1
sol_chg = solar[b] / solar[a] - 1
sh0, sh1 = solar[a] / total[a], solar[b] / total[b]
share_if_flat = solar[b] / total[a]         # share if the total had not moved
real_pp = (share_if_flat - sh0) * 100       # the part that is solar growing
arith_pp = (sh1 - share_if_flat) * 100      # the part that is the total shrinking

# the two numbers the brief says must both be true
assert round(tot_chg * 100, 1) == -5.0, tot_chg
assert round(sol_chg * 100, 1) == 82.1, sol_chg
assert round(sh0 * 100, 1) == 4.1 and round(sh1 * 100, 1) == 7.9
yo_a, yo_b = "2025-09", "2026-09"
yoy_tot = total[yo_b] / total[yo_a] - 1
yoy_sol = solar[yo_b] / solar[yo_a] - 1
print("B2 numbers")
print(f"   total {tot_chg * 100:+.1f}%, solar {sol_chg * 100:+.1f}% ({a} -> {b})")
print(f"   solar share {sh0 * 100:.1f}% -> {sh1 * 100:.1f}% = "
      f"+{(sh1 - sh0) * 100:.1f} pp: {real_pp:.1f} pp is solar growing, "
      f"{arith_pp:.1f} pp is the total shrinking")
print(f"   same-month check {yo_a} -> {yo_b}: total {yoy_tot * 100:+.1f}%, "
      f"solar {yoy_sol * 100:+.1f}%\n")

x = pd.to_datetime(mx.index + "-01")
fig, ax = plt.subplots(figsize=(10.6, 6.0))
w = 22
ax.bar(x, solar / 1e6, width=w, color=ORANGE, label="Solar", zorder=3)
ax.bar(x, rest / 1e6, width=w, bottom=solar / 1e6, color=GREY, alpha=0.55,
       label="All other sources (7 categories)", zorder=3)
ax.set_ylim(0, 17.5)
ax.set_yticks([0, 2, 4, 6, 8, 10, 12])
ax.set_ylabel("Energy generated, TWh per month")
ticks = list(x[::2]) + [x[-1]]
ax.set_xticks(ticks)
ax.set_xticklabels([d.strftime("%b\n%Y") for d in ticks])
ax.set_xlim(x[0] - pd.Timedelta(days=22), x[-1] + pd.Timedelta(days=60))

# selective labels: the first and the last bar carry the numbers, no others
for mon, sh, ha, dx in [(a, sh0, "left", -9), (b, sh1, "right", 9)]:
    xm = pd.to_datetime(mon + "-01") + pd.Timedelta(days=dx)
    top = total[mon] / 1e6
    # a thin leader from the label down to the bar it describes
    ax.plot([pd.to_datetime(mon + "-01")] * 2, [top + 0.15, 13.0],
            color=SOFT, lw=0.7, zorder=2)
    ax.text(xm, 14.15, f"{top:.2f} TWh total", ha=ha, va="bottom",
            fontsize=9, color=INK, fontweight="bold")
    ax.text(xm, 13.15, f"solar {solar[mon] / 1e6:.2f} TWh = {sh * 100:.1f}%",
            ha=ha, va="bottom", fontsize=9, color=ORANGE, fontweight="bold")
ax.grid(axis="x", visible=False)
ax.text(0.33, 0.985,
        f"Solar   {sol_chg * 100:+.0f}% in MWh     Total   {tot_chg * 100:+.0f}% in MWh\n"
        f"Share  {sh0 * 100:.1f}% -> {sh1 * 100:.1f}%  (+{(sh1 - sh0) * 100:.1f} percentage points)\n"
        f"   {real_pp:.1f} pp of that is solar growing\n"
        f"   {arith_pp:.1f} pp is the total shrinking (the arithmetic)",
        transform=ax.transAxes, va="top", ha="left", fontsize=9, color=INK,
        linespacing=1.55,
        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec=PALETTE["grid"]))
ax.legend(loc="upper left", frameon=False, bbox_to_anchor=(0.0, 0.985))
fig.suptitle("Mostly real: solar's share rose from 4.1% to 7.9% because solar "
             "grew, not because the total shrank",
             x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK,
             y=0.99)
fig.text(0.01, 0.925,
         "Supports: the communications line can say solar is growing in "
         "absolute terms, and should not quote the share alone.",
         fontsize=9.5, color=SOFT, ha="left")
note2 = (
    "Source: generation_mix.csv (ministry publication), cleaned by partA_process.py: the 18 'All sources / Total' rows are removed so the 144 part-rows are mutually exclusive (they match the published total to within 2 MWh).\n"
    "Window: Apr 2025 - Sep 2026, 18 months. Percentages compare the first and last month (Apr 2025 vs Sep 2026), which are different seasons; "
    f"same-month check Sep 2025 vs Sep 2026: solar {yoy_sol * 100:+.0f}%, total {yoy_tot * 100:+.1f}%, share {solar[yo_a] / total[yo_a] * 100:.1f}% -> {sh1 * 100:.1f}%.\n"
    "'All other sources' = Gas, Coal, Furnace oil, Dam, Run-of-river, Wind, Imported (7 categories). Bars start at zero. Share = solar MWh / total MWh of the month. Synthetic data, CDB601220 Week 6.")
fig.tight_layout(rect=(0, 0, 1, 0.9))
vizlib.save_fig(fig, HERE / "partB_2.png", note=wrap(note2, 165))
plt.close(fig)
print("wrote partB_2.png\n")


# =========================================================================
# B3  RELATIONSHIP - where does rooftop solar actually go?
# =========================================================================
reg = pd.read_csv(CLEAN / "district_grid_clean.csv")
reg["solar_w_hh"] = reg.solar_kw_installed * 1000 / reg.households
reg["rate"] = reg.outages / reg.households * 1000
r_pear = np.corrcoef(reg.income_pc_usd, reg.solar_w_hh)[0, 1]
r_spear = stats.spearmanr(reg.income_pc_usd, reg.solar_w_hh)[0]
raw_r = np.corrcoef(reg.population, reg.solar_kw_installed)[0, 1]
mid = reg[~reg.code.isin(["D13", "D22"])]
r_wo = np.corrcoef(mid.income_pc_usd, mid.solar_w_hh)[0, 1]
med = reg.solar_w_hh.median()
worst3 = reg.nlargest(3, "rate").code.tolist()   # highest interruption rates (Part C)
assert set(worst3) == {"D12", "D11", "D13"}, worst3
assert (reg.set_index("code").loc[worst3, "solar_w_hh"] < med).all()
assert set(reg.nsmallest(2, "solar_w_hh").code) == {"D13", "D22"}
assert set(reg.nsmallest(2, "income_pc_usd").code) == {"D13", "D22"}
print("B3 numbers")
print(f"   r(income, solar W/household)   Pearson {r_pear:+.2f}  Spearman "
      f"{r_spear:+.2f}  Pearson without D13/D22 {r_wo:+.2f}")
print(f"   (the raw-count version, solar kW vs population, would give "
      f"r = {raw_r:+.2f} and just say 'big districts have big totals')")
print(f"   median solar per household {med:,.0f} W; D12/D11/D13 are "
      f"{reg.set_index('code').loc[worst3, 'solar_w_hh'].round(0).tolist()}\n")

fig, ax = plt.subplots(figsize=(9.4, 6.0))
flag = reg.code.isin(["D13", "D22"])
ax.scatter(reg.income_pc_usd[~flag], reg.solar_w_hh[~flag], s=46,
           color=BLUE, marker="o", edgecolor="white", linewidth=0.8, zorder=4,
           label="other 22 districts")
ax.scatter(reg.income_pc_usd[flag], reg.solar_w_hh[flag], s=64, color=ORANGE,
           marker="D", edgecolor="white", linewidth=0.8, zorder=5,
           label="two lowest-income districts")
ring = reg[reg.code.isin(worst3)]
ax.scatter(ring.income_pc_usd, ring.solar_w_hh, s=210, facecolors="none",
           edgecolors=INK, linewidths=1.2, zorder=6,
           label="ringed = 3 highest interruption rates")
slope, icpt = np.polyfit(reg.income_pc_usd, reg.solar_w_hh, 1)
xs = np.array([reg.income_pc_usd.min(), reg.income_pc_usd.max()])
ax.plot(xs, icpt + slope * xs, color=GREY, lw=1.3, ls="--", zorder=2)
ax.axhline(med, color=GREY, lw=0.8, ls=":", zorder=1)
ax.text(10750, med + 40, f"median {med:,.0f}", ha="right", va="bottom",
        fontsize=8, color=SOFT)
labels = {"D13": "D13 Mehrabad", "D22": "D22 Virkabad",
          "D05": "D05 Emnabad", "D15": "D15 Orakcha", "D12": "D12 Lashkar",
          "D11": "D11 Kotla"}
offs = {"D13": (12, -4), "D22": (12, -4), "D05": (-8, 10), "D15": (-8, 8),
        "D12": (-14, -3), "D11": (-14, -3)}
for code, text in labels.items():
    row = reg[reg.code == code].iloc[0]
    ha = "right" if offs[code][0] < 0 else "left"
    ax.annotate(text, (row.income_pc_usd, row.solar_w_hh), xytext=offs[code],
                textcoords="offset points", ha=ha, fontsize=8.5,
                color=ORANGE if code in ("D13", "D22") else INK)
ax.set_xlabel("Income per person, USD per year")
ax.set_ylabel("Rooftop solar installed, watts per household")
ax.set_xlim(2000, 11000)
ax.set_ylim(0, 2700)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
    lambda v, _: f"{v:,.0f}"))
ax.text(0.02, 0.97, f"r = {r_pear:+.2f}  (24 districts)\nSpearman {r_spear:+.2f}; "
        f"without the two orange points {r_wo:+.2f}",
        transform=ax.transAxes, va="top", fontsize=9, color=INK,
        linespacing=1.5)
ax.legend(loc="lower right", frameon=False, fontsize=8.5,
          labelspacing=0.8)
ax.grid(axis="x", visible=False)
fig.suptitle("Rooftop solar follows income: the two poorest districts have "
             "the least solar per household",
             x=0.01, ha="left", fontsize=13, fontweight="bold", color=INK,
             y=0.99)
fig.text(0.01, 0.925,
         "Supports: do not sell rooftop solar as a fix for unreliable supply. "
         "D12, D11 and D13, the three worst on interruptions per household,\n"
         "all sit below the median solar per household.",
         fontsize=9.5, color=SOFT, ha="left", va="top", linespacing=1.4)
note3 = (
    "Source: district_grid.csv, cleaned by partA_process.py (24 districts; D21 households repaired from 182 to 182,000). Synthetic data, CDB601220 Week 6.\n"
    "Solar per household = solar_kw_installed x 1000 / households (denominator: billed domestic connections). Dashed line = ordinary least-squares fit, descriptive only. "
    "No districts excluded.\n"
    f"For scale: raw solar kW against population gives r = {raw_r:+.2f}, which only says big districts hold big totals, so the chart divides first. Correlation is not cause.")
fig.tight_layout(rect=(0, 0, 1, 0.88))
vizlib.save_fig(fig, HERE / "partB_3.png", note=wrap(note3, 150))
plt.close(fig)
print("wrote partB_3.png")
