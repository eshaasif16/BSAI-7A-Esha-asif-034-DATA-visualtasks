"""
Week 6 - Task C: the figure the board will actually see.

    python3 partA_process.py     # once
    python3 partC_figure.py      # writes partC_figure.png and prints the numbers

The question: WHERE IS SUPPLY LEAST RELIABLE?  (not: where are there the most
interruptions)

The figure is a map and a sorted bar chart that share one colour legend:
    left   equal-area choropleth, interruptions per 1,000 households
    right  the same 24 numbers as bars, sorted, so every district gets the
           same amount of ink (the map gives the 5 biggest districts 12.6% of
           the land for 59.9% of the people)
and the raw count sits in grey beside each bar, so the reader can see the
counterfactual without doing any arithmetic.

Everything partC_note.md quotes is printed by this script.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.patches import Patch, Polygon as MplPolygon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geolib                       # noqa: E402
import vizlib                       # noqa: E402
from vizlib import PALETTE          # noqa: E402

CLEAN, DATA = HERE / "clean", HERE / "data"
if not (CLEAN / "district_grid_clean.csv").exists():
    sys.exit("clean/district_grid_clean.csv is missing - run partA_process.py first.")

vizlib.style_defaults()
ORANGE, INK, SOFT = PALETTE["highlight"], PALETTE["ink"], PALETTE["ink_soft"]

# ------------------------------------------------------------------ the numbers
reg = pd.read_csv(CLEAN / "district_grid_clean.csv")
feats = geolib.read_geojson(Path(__file__).parent / "regions.geojson")
assert len(reg) == 24 and set(reg.code) == {f["code"] for f in feats}

K = 1000                                    # "per 1,000 households"
reg["rate"] = reg.outages / reg.households * K
pooled = reg.outages.sum() / reg.households.sum() * K
rate = dict(zip(reg.code, reg.rate))
reg["rank_rate"] = reg.rate.rank(ascending=False).astype(int)
reg["rank_cnt"] = reg.outages.rank(ascending=False).astype(int)

top_rate = reg.nlargest(3, "rate").code.tolist()
top_cnt = reg.nlargest(3, "outages").code.tolist()
both = sorted(set(top_rate) & set(top_cnt))
r_count = np.corrcoef(reg.outages, reg.households)[0, 1]
r_rate = np.corrcoef(reg.rate, reg.households)[0, 1]
top5pop = reg.nlargest(5, "population")
area = {f["code"]: geolib.polygon_area_km2(f["ring"]) for f in feats}
land5 = sum(area[c] for c in top5pop.code) / sum(area.values()) * 100
pop5 = top5pop.population.sum() / reg.population.sum() * 100

# anchors from the brief
assert round(r_count, 3) == 0.991 and round(r_rate, 3) == 0.175
assert top_cnt == ["D17", "D13", "D24"], top_cnt
assert top_rate == ["D12", "D11", "D13"], top_rate
assert both == ["D13"]
assert round(pooled, 1) == 43.7
assert round(land5, 1) == 12.6 and round(pop5, 1) == 59.9

print("=" * 70)
print("the numbers behind partC_note.md")
print("=" * 70)
print(f"national pooled rate        {pooled:.1f} interruptions per 1,000 households")
print(f"r(interruptions, households)               {r_count:+.3f}")
print(f"r(rate per 1,000 households, households)   {r_rate:+.3f}")
print(f"top 3 by COUNT   {top_cnt}   top 3 by RATE   {top_rate}   on both: {both}")
print(f"5 most populous districts {top5pop.code.tolist()}: "
      f"{land5:.1f}% of the land, {pop5:.1f}% of the people")

# ---- class breaks: print them, and argue the scheme with a number -------------
K_CLASSES = 5
print("\nclass breaks for the rate (printed, as required) and goodness of fit")
edges_by = {}
for scheme in ("natural", "quantile", "equal"):
    e = geolib.breaks(reg.rate, scheme, K_CLASSES)
    edges_by[scheme] = e
    print(f"   {scheme:<9} {[round(float(v), 1) for v in e]}   "
          f"GVF {geolib.gvf(reg.rate, e):.3f}")
edges = edges_by["natural"]
cls = dict(zip(reg.code, geolib.class_of(reg.rate, edges)))
n_top_class = sum(1 for c in cls.values() if c == K_CLASSES - 1)
print(f"   -> Jenks, k=5. The darkest class holds {n_top_class} districts "
      f"({', '.join(sorted(c for c, v in cls.items() if v == K_CLASSES - 1))})")

# ---- the denominator argument --------------------------------------------------
reg["rate_pop"] = reg.outages / reg.population * K
print("\ndenominator check")
print(f"   persons per household spans "
      f"{(reg.population / reg.households).min():.2f} - "
      f"{(reg.population / reg.households).max():.2f}")
print(f"   top 3 per 1,000 HOUSEHOLDS: {top_rate}   "
      f"top 3 per 1,000 PEOPLE: {reg.nlargest(3, 'rate_pop').code.tolist()}")

# ---- duration, as a second opinion on "where is service worst" ----------------
ok = reg.outage_minutes.notna()
reg["min_per_hh"] = reg.outage_minutes / reg.households
reg["mean_len"] = reg.outage_minutes / reg.outages
rk = reg.loc[ok, "min_per_hh"].rank(ascending=False).astype(int)
rk = pd.Series(rk.values, index=reg.loc[ok, "code"])
print("\nduration check (22 districts with usable outage_minutes)")
print(f"   top 3 by interruption-minutes per household: "
      f"{reg.loc[ok].nlargest(3, 'min_per_hh').code.tolist()}")
for c in top_rate:
    ml = reg.set_index("code").mean_len[c]
    print(f"   {c}: rank {rk.get(c, 'n/a')} of 22 on minutes per household, "
          f"mean interruption {ml:.0f} min" if c in rk.index else f"   {c}: n/a")
print(f"   mean interruption length, all usable districts: "
      f"{reg.mean_len.min():.0f} - {reg.mean_len.max():.0f} min "
      f"(median {reg.mean_len.median():.0f})")

# ---- noise: do I need to suppress anyone? ------------------------------------------
fl = geolib.funnel_limits(reg.households, pooled, per=K)
m = reg.sort_values("households").reset_index(drop=True)
m["lo"], m["hi"] = fl.lo.values, fl.hi.values
m["outside"] = (m.rate < m.lo) | (m.rate > m.hi)
half = 1.96 / np.sqrt(reg.outages.min()) * 100
print("\nsuppression / merging")
print(f"   smallest interruption count {reg.outages.min():,} "
      f"(+/-{half:.1f}% of its rate at 95% under Poisson)")
print(f"   {int(m.outside.sum())} of 24 districts sit outside the 95% funnel; "
      f"the funnel is narrow because every count is in the thousands")
print("   districts suppressed or merged: 0")

# ---- the counterfactual -------------------------------------------------------------
tot = reg.outages.sum()
reg["share_count"] = reg.outages / tot * 100
reg["excess"] = (reg.rate - pooled).clip(lower=0) * reg.households / K
reg["share_excess"] = reg.excess / reg.excess.sum() * 100
cnt3 = reg.set_index("code").loc[top_cnt]
print("\nCOUNTERFACTUAL: the raw-count version")
print(f"   top 3 by count {top_cnt} hold {cnt3.share_count.sum():.1f}% of all "
      f"interruptions; their rates: "
      f"{[round(float(v), 1) for v in cnt3.rate]} vs national {pooled:.1f}")
below = [c for c in top_cnt if rate[c] < pooled]
print(f"   of those, below the national rate: {below}")
cnt_cls = geolib.class_of(reg.outages, geolib.breaks(reg.outages, 'natural', 5))
reg["cnt_class"] = cnt_cls
print("   a Jenks map of the raw counts would shade darkest:",
      reg[reg.cnt_class >= 3].sort_values("outages", ascending=False).code.tolist())
lost = reg[(reg.rank_rate <= 7) & (reg.rank_cnt - reg.rank_rate >= 5)
           ].sort_values("rank_rate")
print("   high-rate districts the count map would push down the list:")
for _, r in lost.iterrows():
    print(f"      {r.code} {r.district:<14} rate rank {r.rank_rate:>2}, count rank "
          f"{r.rank_cnt:>2}  ({int(r.outages):,} interruptions, "
          f"{r.share_count:.1f}% of the national count)")
print(f"   budget illustration (my rule, NOT the board's): split by raw count vs "
      f"split by interruptions above the national rate")
five = [c for c in lost.code]
sub = reg.set_index("code")
print(f"      {five}: {sub.loc[five].share_count.sum():.1f}% by count, "
      f"{sub.loc[five].share_excess.sum():.1f}% by excess")
for c in ["D13", "D11", "D12", "D17", "D24", "D09"]:
    print(f"      {c} {sub.at[c, 'district']:<10} {sub.at[c, 'share_count']:>5.1f}% by "
          f"count  {sub.at[c, 'share_excess']:>5.1f}% by excess   "
          f"(rate {sub.at[c, 'rate']:.1f})")
print(f"   {int((reg.rate < pooled).sum())} of 24 districts are below the "
      f"national rate; {int((reg.rate > pooled).sum())} above.\n")

# =========================================================================
# THE FIGURE
# =========================================================================
cm = plt.get_cmap(PALETTE["sequential"])
shades = [cm(0.18 + 0.78 * c / (K_CLASSES - 1)) for c in range(K_CLASSES)]
shade_hex = ["#{:02x}{:02x}{:02x}".format(*(int(round(255 * v)) for v in s[:3]))
             for s in shades]
print("colour check on the five sequential shades (order is carried by "
      "lightness, and every bar and polygon is also labelled with its number)")
vizlib.cvd_report(shade_hex, "deutan")
i, j, a, b, d = vizlib.worst_pair(shade_hex, "deutan")
print(f"   worst adjacent pair after deutan simulation: S{i}/S{j} dE {d:.1f} "
      f"({vizlib.verdict(d)})\n")

fig = plt.figure(figsize=(12.6, 7.6))
axm = fig.add_axes([0.015, 0.13, 0.37, 0.65])
axb = fig.add_axes([0.575, 0.13, 0.30, 0.65])

# ---- left: the map --------------------------------------------------------
geolib.choropleth(axm, feats, rate, scheme="natural", k=K_CLASSES, legend=False)
lat_ts = geolib._collection_lat_ts(feats)
hl = []
for f in feats:
    if f["code"] in top_rate:
        x, y = geolib._project_ring(list(f["ring"]), "equal_area", lat_ts)
        hl.append(MplPolygon(np.column_stack([x, y]), closed=True))
axm.add_collection(PatchCollection(hl, facecolors="none", edgecolors=ORANGE,
                                   linewidths=2.6, zorder=6))
for f in feats:
    px, py = geolib.representative_point(f["ring"])
    x, y = geolib.equal_area_xy([px], [py], lat_ts=lat_ts)
    c = f["code"]
    dark = cls[c] >= 3
    axm.text(x[0], y[0], f"{c}\n{rate[c]:.1f}", ha="center", va="center",
             fontsize=8.6 if c in top_rate else 7.4,
             fontweight="bold" if c in top_rate else "normal",
             color="white" if dark else INK, zorder=7, linespacing=1.05)
axm.set_title("Each district shaded by its rate", fontsize=10, loc="left",
              color=SOFT, fontweight="normal", pad=6)

# ---- right: the sorted bars ---------------------------------------------------
order = reg.sort_values("rate", ascending=True).reset_index(drop=True)
ypos = np.arange(len(order))
bars = axb.barh(ypos, order.rate, color=[shades[cls[c]] for c in order.code],
                edgecolor=["#ffffff" if c not in top_rate else ORANGE
                           for c in order.code],
                linewidth=[0.6 if c not in top_rate else 2.0 for c in order.code],
                height=0.78, zorder=3)
axb.set_yticks(ypos)
axb.set_yticklabels([f"{c}  {n}" for c, n in zip(order.code, order.district)],
                    fontsize=8.6)
for t, c in zip(axb.get_yticklabels(), order.code):
    if c in top_rate:
        t.set_color(ORANGE)
        t.set_fontweight("bold")
axb.set_xlim(0, 62)
axb.set_xlabel("Interruptions per 1,000 households, 12 months", fontsize=9.5)
axb.grid(axis="y", visible=False)
axb.axvline(pooled, color=INK, lw=1.1, ls=(0, (4, 3)), zorder=4)
axb.text(pooled + 0.6, len(order) - 0.35, f"national rate {pooled:.1f}",
         fontsize=8.5, color=INK, va="bottom", ha="left")
for y, c, v in zip(ypos, order.code, order.rate):
    axb.text(v + 0.7, y, f"{v:.1f}", va="center", ha="left", fontsize=8.2,
             color=ORANGE if c in top_rate else INK,
             fontweight="bold" if c in top_rate else "normal", zorder=6,
             bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="none"))
# the raw count, in grey, in its own column to the right of the axes
axb.text(1.03, len(order) - 0.35, "interruptions\n(raw count,\nfor contrast)", fontsize=8,
         color=SOFT, ha="left", va="bottom", transform=axb.get_yaxis_transform(),
         linespacing=1.15)
for y, c, n in zip(ypos, order.code, order.outages):
    axb.text(1.03, y, f"{int(n):,}", fontsize=8, color=SOFT, ha="left",
             va="center", transform=axb.get_yaxis_transform(),
             fontweight="bold" if c in top_cnt else "normal")
axb.set_title("Same numbers, sorted: every district gets one bar",
              fontsize=10, loc="left", color=SOFT, fontweight="normal", pad=6)

# ---- one shared legend, under both panels ----------------------------------------
handles = [Patch(facecolor=shades[c], edgecolor="white",
                 label=f"{edges[c]:.1f} - {edges[c + 1]:.1f}")
           for c in range(K_CLASSES)]
fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.012, 0.045),
           ncol=K_CLASSES, frameon=False, fontsize=8.6, columnspacing=1.4,
           handlelength=1.4, title="Interruptions per 1,000 households (billed "
           "domestic connections), 12 months  |  Jenks natural breaks, 5 classes",
           title_fontsize=8.6, alignment="left")

# ---- title, reader, message --------------------------------------------------------
top_names = [dict(zip(reg.code, reg.district))[c] for c in top_rate]
fig.suptitle(
    f"Supply is least reliable in {top_names[0]}, {top_names[1]} and "
    f"{top_names[2]}:\nabout 50 interruptions per 1,000 households a year, "
    f"against {pooled:.1f} nationally",
    x=0.012, ha="left", fontsize=13.2, fontweight="bold", color=INK, y=0.995,
    linespacing=1.3)
fig.text(0.012, 0.895,
         "For: a board member deciding where the reliability budget goes.  "
         "Qilabad and Zhobara have the most interruptions in total (grey column)\n"
         "but rates below the national figure, because they are the biggest districts. "
         "Only Mehrabad (D13) is on both lists: it is large and genuinely worse than "
         "average.\nOrange outline = the three highest rates.",
         fontsize=9.2, color=SOFT, ha="left", va="top", linespacing=1.45)

note = (
    "Source: district_grid.csv and regions.geojson, cleaned by partA_process.py (24 districts, 0 unmatched; D21 households repaired from 182 to 182,000; duplicate D11 row removed). "
    "Rate = interruptions in the 12-month register / billed households x 1,000. National rate = all interruptions / all households = "
    f"{pooled:.1f}. Colour classes: Jenks natural breaks, k=5 (edges printed in the legend; goodness of fit "
    f"{geolib.gvf(reg.rate, edges):.2f}), one-hue sequential scale. Map: equal-area projection (Lambert cylindrical, km), areas from the sphere. "
    "No district suppressed or merged (smallest count 3,234). Duration is not part of this figure (2 of 24 districts have no usable minutes). Synthetic data, CDB601220 Week 6.")
fig.text(0.012, 0.008, "", fontsize=1)           # keep the canvas stable for tight bbox
vizlib.save_fig(fig, HERE / "partC_figure.png",
                note="\n".join(textwrap.fill(p, 205) for p in note.split("\n")))
plt.close(fig)
print("wrote partC_figure.png (300 dpi)")
