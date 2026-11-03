"""Part D3 - normalized choropleth, the six-step recipe from slide 50."""
from w5common import *

style_defaults()
dh, feats = load_districts()

# 2. JOIN on code and count the failures
geo_codes = {f["code"] for f in feats}
tab_codes = set(dh.code)
failed_geo, failed_tab = geo_codes - tab_codes, tab_codes - geo_codes
print(f"join: {len(geo_codes & tab_codes)} of {len(geo_codes)} polygons matched; "
      f"unmatched polygons={len(failed_geo)}, unmatched table rows={len(failed_tab)}")
assert not failed_geo and not failed_tab

# 3. NORMALISE: cases per 100,000 residents
pooled = dh.cases.sum() / dh.population.sum() * 1e5
print(f"pooled national rate {pooled:.1f} per 100,000 from {dh.cases.sum():,} cases")
rate = dict(zip(dh.code, dh.rate)); cnt = dict(zip(dh.code, dh.cases))
top_rate = dh.nlargest(3, "rate").code.tolist(); top_cnt = dh.nlargest(3, "cases").code.tolist()
print("top 3 by rate :", top_rate, "| by count:", top_cnt,
      "| overlap:", len(set(top_rate) & set(top_cnt)))
print("r(cases, population) = %.3f" % dh.cases.corr(dh.population))
print("smallest district case count:", dh.cases.min(), "(no suppression needed)")

# 4. CLASSIFY: five classes, scheme named, GVF reported
for sch in ("equal", "quantile", "natural"):
    print(f"  {sch:9s} GVF = {gvf(dh.rate.to_numpy(), breaks(dh.rate, sch, 5)):.3f}")

fig, axs = plt.subplots(1, 3, figsize=(15, 6.2),
                        gridspec_kw={"width_ratios": [1.0, 1.0, 0.9], "wspace": 0.12})
fig.subplots_adjust(bottom=0.24, top=0.82)
ax = axs[0]
edges = choropleth(ax, feats, rate, "natural", 5, cmap="Blues",
                   legend_title="Cases per 100,000 residents\n(Jenks natural breaks, 5 classes)",
                   fmt="{:.1f}", legend_loc="upper left", legend_anchor=(0.0, 0.0))
ax.set_title("Rate per 100,000 residents", loc="left")
xy = label_xy(feats)
for c in top_rate:
    ax.annotate(c, xy[c], ha="center", va="center", fontsize=8, color="white", zorder=7)
idx = class_of(dh.rate.to_numpy(), edges)
shades = class_shades(5)

# the count, put back as proportional symbols (area ~ cases)
ax = axs[1]
outlines(ax, feats, color=PALETTE["muted"], lw=0.7)
MAXPT = 1500
prop_symbols(ax, feats, cnt, max_pt=MAXPT, color=PALETTE["highlight"], alpha=0.6)
vals = dh.cases.to_numpy()
hs = [ax.scatter([], [], s=MAXPT * v / vals.max(), color=PALETTE["muted"], alpha=0.65,
                 edgecolor="white", label=f"{v:,.0f}") for v in (vals.min(), np.median(vals), vals.max())]
ax.legend(handles=hs, title="Confirmed cases (symbol AREA = count)", ncol=3, loc="upper left",
          bbox_to_anchor=(0.0, 0.0), frameon=False, fontsize=8, title_fontsize=8,
          labelspacing=1.0, columnspacing=3.4, handletextpad=1.4, borderpad=2.0)
for c in top_cnt + top_rate:
    ax.annotate(c, xy[c], ha="center", va="center", fontsize=7.5, color=PALETTE["ink"], zorder=7)
ax.set_title("Raw count (D17, D13, D09 lead)", loc="left")

# sorted bars of the rate, same five-class colours
ax = axs[2]
d = dh.sort_values("rate")
ax.barh(d.code, d.rate, color=[shades[int(c)] for c in class_of(d.rate.to_numpy(), edges)],
        edgecolor="white")
ax.axvline(pooled, color=PALETTE["ink"], lw=1, ls="--")
ax.text(pooled + 1, 0.2, f"national {pooled:.1f}", fontsize=8, va="bottom")
ax.set_xlim(0, 85); ax.tick_params(axis="y", labelsize=7)
ax.set_xlabel("Cases per 100,000 residents"); ax.grid(axis="y", visible=False)
ax.set_title("Same rate, sorted (bars from zero)", loc="left")

fig.suptitle("Normalised for population, the outbreak sits in the north-west (D19, D20, D21),\n"
             "not in the big districts that top the raw count", x=0.01, ha="left",
             fontsize=13, fontweight="bold", y=0.96)
cap = (f"Boundaries: districts.geojson, 24 districts ({SYN}); table: district_health.csv, joined on code, "
       f"24/24 matched, 0 failures. Extracted {DATE}.\n"
       "Projection: Lambert cylindrical equal-area (km), standard parallel = mean latitude of the collection, "
       "shared by every layer. Classes: Jenks natural breaks (k=5); breaks printed in legend.\n"
       f"Rate = cases / resident population x 100,000. Pooled national rate {pooled:.1f} from {dh.cases.sum():,} cases. "
       f"Suppression: none (smallest district has {dh.cases.min()} cases; no unit merged or hidden).")
save_fig(fig, HERE / "partD_choropleth.png", cap)
print("breaks:", [round(e, 1) for e in edges]); print("saved partD_choropleth.png")
