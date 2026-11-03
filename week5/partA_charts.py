"""Part A - rebuild nine published charts, then plot nine honest redesigns.
Writes figs/caseN_published.png and figs/caseN_redesign.png (300 dpi) and
partA_numbers.txt (every number quoted in the diagnosis)."""
import itertools, textwrap
from scipy import stats
from w5common import *
import json

style_defaults()
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10})
NUM = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s); NUM.append(s)
def note(t): return textwrap.fill(t, 190)
def title(ax, t, pub=False):
    ax.set_title(textwrap.fill(("PUBLISHED, rebuilt: " if pub else "") + t, 78), loc="left", fontsize=9.5)

hi = load_health()
dh, feats = load_districts()
ix = dh.set_index('code')
codes = [f["code"] for f in feats]
PUB = PALETTE["highlight"]
BLUE = PALETTE["series"][0]
pooled_d = dh.cases.sum() / dh.population.sum() * 1e5
edges_nat = breaks(dh.rate, "natural", 5)
S = lambda case, kind: FIGS / f"case{case}_{kind}.png"

def hav(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))

# =============================================================== CASE 1
say("\n=== CASE 1  size = pop_m ** 2 ===")
s_bad = hi.pop_m ** 2
say(f"marks {len(hi)}; largest/smallest AREA ratio {s_bad.max()/s_bad.min():,.0f}x; DIAMETER ratio {math.sqrt(s_bad.max()/s_bad.min()):.0f}x "
    f"(brief's '589x' is the diameter ratio, not the area ratio)")
say(f"countries under 2.0 M: {(hi.pop_m<2).sum()}; with s < 4 pt^2 (under 2 pt across): {(s_bad<4).sum()}; with s < 1 pt^2 (under 1 pt across): {(s_bad<1).sum()}")
big3 = s_bad.nlargest(3).sum() / s_bad.sum()
say(f"the three biggest countries own {big3:.1%} of all the ink; Wessant's bubble is {math.sqrt(s_bad.max()):.0f} pt = {math.sqrt(s_bad.max())/72:.1f} in across (matplotlib: diameter = sqrt(s))")
rho = stats.spearmanr(hi.pop_m, hi.healthcare_access)
say(f"decoy check: Spearman(pop_m, healthcare_access) = {rho.statistic:.2f} (p={rho.pvalue:.2f}); the 6 most populous countries span access "
    f"{hi.nlargest(6,'pop_m').healthcare_access.min():.1f}-{hi.nlargest(6,'pop_m').healthcare_access.max():.1f}; "
    f"Spearman(gdp_pc, access) = {stats.spearmanr(hi.gdp_pc, hi.healthcare_access).statistic:.2f}")
fig, ax = plt.subplots(figsize=(8, 3.9))
ax.scatter(hi.gdp_pc, hi.healthcare_access, s=s_bad, color=BLUE, alpha=0.3, edgecolor="none")
ax.set_xscale("log"); ax.set_xlabel("GDP per capita (USD, log scale)"); ax.set_ylabel("Healthcare access (0-100)")
title(ax, "\"Population and healthcare access are unrelated\" - s = pop_m**2", pub=True)
save_fig(fig, S(1, "published"), note("Rebuilt from the recipe ax.scatter(gdp, access, s=pop_m**2). Source: health_indicators.csv (synthetic, CDB601220 Week 5), n=60. NOT a recommended chart.")); plt.close(fig)
# the redesign is the D1 bubble chart
import shutil; shutil.copy(HERE / "partD_bubble.png", S(1, "redesign")) if (HERE / "partD_bubble.png").exists() else say("run partD_bubble.py first")

# =============================================================== CASE 2
say("\n=== CASE 2  choropleth of cases ===")
say(f"{len(dh)} districts, {dh.cases.sum():,} cases, population {dh.population.sum():,}")
tc = dh.nlargest(3, "cases"); tr = dh.nlargest(3, "rate")
say("top 3 by count: " + ", ".join(f"{r.code} {r.district} ({r.cases:,} cases, rate {r.rate:.1f})" for r in tc.itertuples()))
say("top 3 by rate : " + ", ".join(f"{r.code} {r.district} ({r.cases:,} cases, rate {r.rate:.1f})" for r in tr.itertuples()))
say(f"national pooled rate {pooled_d:.1f}; r(cases, population) = {dh.cases.corr(dh.population):.3f}; population varies {dh.population.max()/dh.population.min():.1f}x")
ix = dh.set_index("code")
dd = {(a, b): hav(ix.loc[a, ["lat", "lon"]], ix.loc[b, ["lat", "lon"]]) for a, b in itertools.combinations(["D17", "D13", "D09"], 2)}
say("distances between the three count leaders (km): " + ", ".join(f"{a}-{b} {d:,.0f}" for (a, b), d in dd.items()))
say(f"count leaders' ranks by rate: " + ", ".join(f"{c} #{int(dh.rate.rank(ascending=False)[dh.code==c].iloc[0])}" for c in ["D17", "D13", "D09"]))
cnt = dict(zip(dh.code, dh.cases)); rate = dict(zip(dh.code, dh.rate)); xy = label_xy(feats)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
choropleth(ax, feats, cnt, "natural", 5, legend_title="Confirmed cases (count)\nnatural breaks", fmt="{:,.0f}", legend_loc="center left", legend_anchor=(1.0, 0.5))
for c in ["D17", "D13", "D09"]: ax.annotate(c, xy[c], ha="center", va="center", color="white", fontsize=8, fontweight="bold")
title(ax, "\"The outbreak is concentrated in three districts around the capital\"", pub=True)
save_fig(fig, S(2, "published"), note("Rebuilt: join on code, natural breaks, Blues. Boundaries: districts.geojson; data: district_health.csv (synthetic, CDB601220 Week 5). Equal-area projection.")); plt.close(fig)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 3.9), gridspec_kw={"width_ratios": [1.1, 1]})
a1.scatter(dh.population / 1e6, dh.cases, s=22, color=PALETTE["muted"], zorder=3)
xx = np.linspace(0, dh.population.max() / 1e6, 50); a1.plot(xx, xx * 1e6 * pooled_d / 1e5, color=PALETTE["ink"], lw=1, ls="--")
a1.text(0.2, 5000, f"national rate {pooled_d:.1f}/100k", fontsize=8, rotation=0)
for c in ["D17", "D13", "D09"]: a1.scatter(ix.population[c] / 1e6, ix.cases[c], s=40, facecolor="white", edgecolor=PALETTE["ink"], zorder=4); a1.annotate(c, (ix.population[c] / 1e6, ix.cases[c]), xytext=(5, -9), textcoords="offset points", fontsize=8)
for c in ["D19", "D20", "D21"]: a1.scatter(ix.population[c] / 1e6, ix.cases[c], s=40, color=PUB, zorder=4); a1.annotate(c, (ix.population[c] / 1e6, ix.cases[c]), xytext=(5, 3), textcoords="offset points", fontsize=8, color=PUB)
a1.set_xlabel("Population (millions)"); a1.set_ylabel("Cases"); a1.set_title("Cases ride on population\n(r = 0.986). Orange = top 3 by rate", loc="left", fontsize=9.5)
choropleth(a2, feats, rate, "natural", 5, legend_title="Cases per 100,000 residents\nnatural breaks", fmt="{:.1f}", legend_loc="center left", legend_anchor=(1.0, 0.5))
a2.set_title("Normalised: the hot zone is north-west", loc="left", fontsize=9.5)
save_fig(fig, S(2, "redesign"), note("Redesign: rate = cases / population x 100,000 on the right; the left panel shows why the count map is a population map. Source: district_health.csv (synthetic, CDB601220 Week 5). Equal-area projection.")); plt.close(fig)

# =============================================================== CASE 3
say("\n=== CASE 3  min-max PCP, 'GDP barely varies' ===")
mm = scale_frame(hi, PCP_COLS, "minmax")["gdp_pc"]
say(f"after min-max: {(mm<0.10).sum()} of 60 below 0.10; median {mm.median():.3f}")
g2 = hi.gdp_pc.nlargest(2)
say(f"gdp_pc {hi.gdp_pc.min()} to {hi.gdp_pc.max():,} = {hi.gdp_pc.max()/hi.gdp_pc.min():.0f}x; max is {g2.iloc[0]/g2.iloc[1]:.1f}x the second ({g2.iloc[1]:,}, {hi.country[g2.index[1]]})")
wo = hi[hi.country != "Aldonia"]; mmw = (wo.gdp_pc - wo.gdp_pc.min()) / (wo.gdp_pc.max() - wo.gdp_pc.min())
say(f"decoy check: without Aldonia the remaining 59 still span {wo.gdp_pc.max()/wo.gdp_pc.min():.0f}x (IQR {wo.gdp_pc.quantile(.25):,.0f} to {wo.gdp_pc.quantile(.75):,.0f}); min-max median becomes {mmw.median():.2f}")
rk = scale_frame(hi, PCP_COLS, "rank")["gdp_pc"]
say(f"after RANK scaling: gdp_pc median {rk.median():.2f}, {(rk<0.10).sum()} below 0.10 (uniform by construction)")
FILE_ORDER = list(PCP_COLS)
def pcp_small(df, order, how, mask, ttl, decl, pub=False):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    pcp(ax, df, order, how, highlight=mask); ax.tick_params(length=0)
    ax.set_title(textwrap.fill(("PUBLISHED, rebuilt: " if pub else "") + ttl, 80), loc="left", fontsize=9.5, pad=18)
    fig.subplots_adjust(bottom=0.27, top=0.84)
    fig.text(0.125, 0.07, textwrap.fill(decl, 140), fontsize=7.5, va="top", color=PALETTE["ink_soft"])
    return fig
ald = (hi.country == "Aldonia").to_numpy()
f = pcp_small(hi, FILE_ORDER, "minmax", ald, "\"GDP per capita barely varies across the sample\"", "Min-max scaled, axes in file order. Orange = Aldonia ($120,219). Grey = the other 59 countries.", pub=True)
save_fig(f, S(3, "published"), "Rebuilt from the recipe. Source: health_indicators.csv (synthetic, CDB601220 Week 5), n=60."); plt.close(f)
f = pcp_small(hi, FILE_ORDER, "rank", ald, "gdp_pc is not flat: on a rank scale it fills its whole axis", "Percentile-RANK scaled (outlier-proof), axes in file order, so the only change from the published chart is the scaling. Orange = Aldonia: rank 60, nothing special once the outlier cannot set the scale. Real min/max printed on each axis.")
save_fig(f, S(3, "redesign"), "Redesign. Source: health_indicators.csv (synthetic, CDB601220 Week 5), n=60, none excluded."); plt.close(f)

# =============================================================== CASE 4
say("\n=== CASE 4  PCP in file order ===")
r_ac = hi.healthcare_access.corr(hi.cases_per_100k)
say(f"file order: {' -> '.join(FILE_ORDER)}; healthcare_access is axis {FILE_ORDER.index('healthcare_access')+1}, cases_per_100k is axis {FILE_ORDER.index('cases_per_100k')+1}: "
    f"{abs(FILE_ORDER.index('healthcare_access')-FILE_ORDER.index('cases_per_100k'))} apart")
say(f"r(healthcare_access, cases_per_100k) = {r_ac:.3f}; Spearman = {stats.spearmanr(hi.healthcare_access, hi.cases_per_100k).statistic:.3f}")
chain = safe_corr_chain(hi, PCP_COLS)
say("greedy chain: " + " -> ".join(chain) + "; adjacent-pair r: " + ", ".join(f"{a[:6]}/{b[:6]} {hi[a].corr(hi[b]):+.2f}" for a, b in zip(chain, chain[1:])))
fo_pairs = [abs(hi[a].corr(hi[b])) for a, b in zip(FILE_ORDER, FILE_ORDER[1:])]; ch_pairs = [abs(hi[a].corr(hi[b])) for a, b in zip(chain, chain[1:])]
say(f"sum of |r| across adjacent axis pairs: file order {sum(fo_pairs):.2f}, greedy chain {sum(ch_pairs):.2f}")
hiq = (hi.cases_per_100k >= hi.cases_per_100k.quantile(.75)).to_numpy()
f = pcp_small(hi, FILE_ORDER, "minmax", hiq, "\"Healthcare access and case rate are unrelated: no crossing pattern\"", "Min-max scaled, axes in the order they appear in the file. Orange = top quartile of cases_per_100k (15 countries).", pub=True)
save_fig(f, S(4, "published"), "Rebuilt from the recipe. Source: health_indicators.csv (synthetic, CDB601220 Week 5), n=60."); plt.close(f)
f = pcp_small(hi, chain, "minmax", hiq, "Move the two columns next to each other and the X appears (r = \u22120.80)", "Min-max scaled (unchanged) so the only change is axis order: greedy |r| chain computed in code, not by eye. Orange = same 15 high-case-rate countries.")
save_fig(f, S(4, "redesign"), "Redesign. Source: health_indicators.csv (synthetic, CDB601220 Week 5), n=60."); plt.close(f)

# =============================================================== CASE 5
say("\n=== CASE 5  quantile classes on flat rates ===")
c5 = pd.read_csv(DATA / "case05_flat_rates.csv"); c5["rate"] = c5.cases / c5.population * 1e5
geo5 = {f["code"] for f in feats}; say(f"join: {len(geo5 & set(c5.code))} of 24 matched, {len(geo5 ^ set(c5.code))} failures")
p5 = c5.cases.sum() / c5.population.sum() * 1e5
say(f"{len(c5)} districts; rate {c5.rate.min():.2f} to {c5.rate.max():.2f}; spread = {(c5.rate.max()-c5.rate.min())/c5.rate.mean():.1%} of the mean; pooled {p5:.2f}")
eq = breaks(c5.rate, "quantile", 5); say("quantile breaks: " + ", ".join(f"{e:.2f}" for e in eq) + f"; smallest class width {min(np.diff(eq)):.2f}, i.e. {min(np.diff(eq))/p5:.1%} of the pooled rate")
cv_obs = c5.rate.std(ddof=0) / c5.rate.mean(); cv_pois = np.sqrt(np.mean(1 / c5.cases))
say(f"decoy check: observed CV of the rates {cv_obs:.1%}; CV expected from pure Poisson noise at these case counts {cv_pois:.1%} -> the districts vary LESS than chance alone predicts")
lam = p5 / 1e5 * c5.population; z_ = (c5.cases - lam) / np.sqrt(lam)
say(f"districts outside 95% funnel: {(np.abs(z_)>1.96).sum()} of 24; largest |z| = {np.abs(z_).max():.2f}")
rate5 = dict(zip(c5.code, c5.rate))
fig, ax = plt.subplots(figsize=(6.4, 4.2))
choropleth(ax, feats, rate5, "quantile", 5, legend_title="Cases per 100,000\nquantile classes (n=4-5 each)", fmt="{:.2f}", legend_loc="center left", legend_anchor=(1.0, 0.5))
title(ax, "\"A clear five-level gradient in incidence across the federation\"", pub=True)
save_fig(fig, S(5, "published"), note("Rebuilt: cases/population x 1e5, five quantile classes, Blues. Source: case05_flat_rates.csv, districts.geojson (synthetic, CDB601220 Week 5). Equal-area projection.")); plt.close(fig)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 4.6), gridspec_kw={"width_ratios": [1, 1.15]})
fig.subplots_adjust(bottom=0.34, top=0.86, wspace=0.4)
idx5, _ = choropleth_fixed(a1, feats, rate5, edges_nat, legend_title="Cases per 100,000, SAME classes as the\ncase 2 outbreak (natural breaks)", fmt="{:.1f}", legend_loc="upper left", legend_anchor=(0.0, 0.0))
a1.set_title(f"All {int((idx5==0).sum())} districts sit in the\nlightest national class", loc="left", fontsize=9.5)
gp = np.linspace(c5.population.min() * .9, c5.population.max() * 1.05, 200); fl5 = funnel_limits(gp, p5)
a2.fill_between(fl5.population / 1e6, fl5.lo, fl5.hi, color=PALETTE["grid"], label="95% Poisson limits")
a2.axhline(p5, color=PALETTE["ink_soft"], ls="--", lw=1)
a2.scatter(c5.population / 1e6, c5.rate, s=24, color=BLUE, zorder=3)
a2.set_ylim(0, 80); a2.set_xlabel("Population (millions)"); a2.set_ylabel("Cases per 100,000")
a2.set_title("Funnel: all 24 districts inside the limits\n(0 outside), axis from zero", loc="left", fontsize=9.5)
a2.legend(loc="upper right", fontsize=8)
save_fig(fig, S(5, "redesign"), note("Redesign. Left: class edges borrowed from the district_health.csv rate map (30.4/33.8/47.5/54.4/64.8/76.5) so the two outbreaks share a scale. Right: pooled rate +/- 1.96 sqrt(expected). Synthetic, CDB601220 Week 5.")); plt.close(fig)

# =============================================================== CASE 6
say("\n=== CASE 6  small-area ranking ===")
sm = pd.read_csv(DATA / "smallarea_cases.csv"); sm["rate"] = sm.cases / sm.population * 1e5
p6 = sm.cases.sum() / sm.population.sum() * 1e5; u = sm[sm.unit == "U32"].iloc[0]
say(f"{len(sm)} units; pooled {p6:.2f}; U32 {u.rate:.1f} = {u.rate/p6:.1f}x national, from {u.cases:.0f} cases in {u.population:,.0f} people")
big_ = sm[sm.population > 1e5]; say(f"{len(big_)} units over 100,000 people: rates {big_.rate.min():.1f} to {big_.rate.max():.1f}")
lo_ci = stats.chi2.ppf(.025, 2 * u.cases) / 2; hi_ci = stats.chi2.ppf(.975, 2 * (u.cases + 1)) / 2
say(f"U32 exact 95% interval: {lo_ci:.1f}-{hi_ci:.1f} cases = {lo_ci/u.population*1e5:.1f}-{hi_ci/u.population*1e5:.1f} per 100,000 (wide: nine cases)")
say(f"one case fewer or more moves U32 by {1/u.population*1e5:.1f} per 100,000 (rate {(u.cases-1)/u.population*1e5:.1f} / {(u.cases+1)/u.population*1e5:.1f}); pooled rate without U32 {(sm.cases.sum()-u.cases)/(sm.population.sum()-u.population)*1e5:.2f}")
pex = stats.poisson.sf(u.cases - 1, p6 / 1e5 * u.population)
say(f"exact P(>= 9 | expected {p6/1e5*u.population:.2f}) = {pex:.5f}; x40 units = {min(1,40*pex):.3f}")
lam = p6 / 1e5 * sm.population; lo_l = (lam - 1.96 * np.sqrt(lam)) / sm.population * 1e5; hi_l = (lam + 1.96 * np.sqrt(lam)) / sm.population * 1e5
out = ((sm.rate < lo_l) | (sm.rate > hi_l)).to_numpy(); say(f"outside 95% funnel: {out.sum()} of 40 ({list(sm.unit[out])}); expected by chance ~2")
tops = sm.sort_values("rate", ascending=False)
fig, ax = plt.subplots(figsize=(8, 3.9))
d = sm.sort_values("rate", ascending=False)
ax.bar(range(len(d)), d.rate, color=[PUB if x == "U32" else PALETTE["muted"] for x in d.unit])
ax.axhline(p6, color=PALETTE["ink"], ls="--", lw=1); ax.text(39.5, p6 + 0.8, f"national {p6:.2f}", ha="right", fontsize=8)
ax.set_xticks(range(len(d))); ax.set_xticklabels(d.unit, rotation=90, fontsize=6); ax.set_ylabel("Cases per 100,000"); ax.grid(axis="x", visible=False)
ax.annotate("U32: 9 cases / 22,000 people = 40.9", (0, u.rate), xytext=(3, u.rate - 2), fontsize=8)
title(ax, "\"U32 is a hotspot, nearly five times the national rate\"", pub=True)
save_fig(fig, S(6, "published"), note("Rebuilt: cases/population x 1e5, ranked. Source: smallarea_cases.csv (synthetic, CDB601220 Week 5), n=40.")); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 3.9))
gp = np.linspace(3000, 280000, 300); fg = funnel_limits(gp, p6)
ax.fill_between(fg.population, fg.lo, fg.hi, color=PALETTE["grid"], label="95% Poisson limits")
ax.axhline(p6, color=PALETTE["ink_soft"], ls="--", lw=1)
ax.scatter(sm.population[~out], sm.rate[~out], s=22, color=BLUE, zorder=3)
ax.scatter(sm.population[out], sm.rate[out], s=40, color=PUB, zorder=4)
ax.errorbar([u.population], [u.rate], yerr=[[u.rate - lo_ci / u.population * 1e5], [hi_ci / u.population * 1e5 - u.rate]], color=PUB, capsize=3, lw=1, zorder=2)
ax.annotate(f"U32 (95% interval {lo_ci/u.population*1e5:.0f}-{hi_ci/u.population*1e5:.0f})", (u.population, u.rate), xytext=(10, 2), textcoords="offset points", fontsize=8)
ax.set_xlabel("Population of unit"); ax.set_ylabel("Cases per 100,000"); ax.set_ylim(0, 85); ax.legend(loc="upper right", fontsize=8)
title(ax, "Rates swing wildly below ~50,000 people and settle above 100,000: U32 is the single point outside the funnel")
save_fig(fig, S(6, "redesign"), note("Redesign: funnel plot, pooled rate 8.72 +/- 1.96 sqrt(expected); U32 whisker is the exact Poisson interval. Source: smallarea_cases.csv (synthetic, CDB601220 Week 5), n=40.")); plt.close(fig)

# =============================================================== CASE 7
say("\n=== CASE 7  income vs rate, r across districts ===")
r24 = dh.income_pc_usd.corr(dh.rate); say(f"r across 24 districts = {r24:.3f}")
loo = [dh.drop(i).income_pc_usd.corr(dh.drop(i).rate) for i in dh.index]; say(f"leave-one-out range of r: {min(loo):.3f} to {max(loo):.3f} (no single district drives it)")
say(f"decoy check (density confounding): r(income, density) = {dh.income_pc_usd.corr(dh.density):.3f}; r(rate, density) = {dh.rate.corr(dh.density):.3f}")
w = dh.population / dh.population.sum(); mx = (w * dh.income_pc_usd).sum(); my = (w * dh.rate).sum()
rw = (w * (dh.income_pc_usd - mx) * (dh.rate - my)).sum() / math.sqrt((w * (dh.income_pc_usd - mx) ** 2).sum() * (w * (dh.rate - my) ** 2).sum())
say(f"population-weighted r across the same 24 districts = {rw:.3f}")
zones = dh.groupby("zone").apply(lambda g: pd.Series({"cases": g.cases.sum(), "pop": g.population.sum(), "inc": np.average(g.income_pc_usd, weights=g.population)}), include_groups=False)
zones["rate"] = zones.cases / zones["pop"] * 1e5; rz = zones.inc.corr(zones.rate)
say(f"aggregated to the 6 coarse zones (income = population-weighted mean): r = {rz:.3f}; with a plain mean of district incomes r = "
    f"{dh.groupby('zone').income_pc_usd.mean().corr(zones.rate):.3f} (also a modelling choice)")
alt = read_geojson(DATA / "districts_alt.geojson")
Wm = areal_weights(feats, alt, n=600)
Cc, Pp, IP = Wm @ dh.cases.to_numpy(), Wm @ dh.population.to_numpy(), Wm @ (dh.population * dh.income_pc_usd).to_numpy()
al_rate = Cc / Pp * 1e5; al_inc = IP / Pp; ra = np.corrcoef(al_inc, al_rate)[0, 1]
say(f"re-cut into the 24 ALTERNATIVE units (areal interpolation, assumes even spread inside each district): r = {ra:.3f}; cases conserved: {Cc.sum():,.0f}")
say(f"scale effect: 24 -> 6 units moves r from {r24:.2f} to {rz:.2f}; zoning effect at the same scale (24 vs 24 alt) moves it {ra-r24:+.2f}")
fig, ax = plt.subplots(figsize=(8, 3.9))
ax.scatter(dh.income_pc_usd, dh.rate, s=28, color=BLUE, zorder=3)
m, b = np.polyfit(dh.income_pc_usd, dh.rate, 1); xx = np.array([dh.income_pc_usd.min(), dh.income_pc_usd.max()]); ax.plot(xx, m * xx + b, color=PUB, lw=1.4)
ax.text(0.97, 0.95, f"r = {r24:.3f}  (n = 24 districts)", transform=ax.transAxes, ha="right", va="top", fontsize=10, color=PUB)
ax.set_xlabel("District income per head (USD)"); ax.set_ylabel("Cases per 100,000")
title(ax, "\"Income and case rate are only weakly related: r is about -0.31\"", pub=True)
save_fig(fig, S(7, "published"), note("Rebuilt: Pearson r of income_pc_usd vs cases/population x 1e5 across 24 districts. Source: district_health.csv (synthetic, CDB601220 Week 5).")); plt.close(fig)
fig, axs = plt.subplots(1, 3, figsize=(9, 3.6), sharey=True)
panels = [("24 districts (published)", dh.income_pc_usd, dh.rate, r24, None), ("24 alternative units", al_inc, al_rate, ra, None), ("6 coarse zones", zones.inc, zones.rate, rz, list(zones.index))]
for a, (t, xv, yv, rr, lab) in zip(axs, panels):
    a.scatter(xv, yv, s=28, color=BLUE, zorder=3)
    mm_, bb_ = np.polyfit(np.asarray(xv, float), np.asarray(yv, float), 1); xx = np.array([np.min(xv), np.max(xv)]); a.plot(xx, mm_ * xx + bb_, color=PUB, lw=1.4)
    a.set_title(f"{t}\nr = {rr:.2f}", loc="left", fontsize=9); a.set_xlabel("Income per head (USD)", fontsize=8)
    if lab:
        for l_, x_, y_ in zip(lab, xv, yv): a.annotate(l_, (x_, y_), xytext=(4, 3), textcoords="offset points", fontsize=7)
axs[0].set_ylabel("Cases per 100,000")
fig.suptitle("The correlation is a property of the zoning: r = \u22120.31 at 24 districts becomes \u22120.75 at 6 zones", x=0.01, ha="left", fontsize=10, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.93))
save_fig(fig, S(7, "redesign"), note("Redesign: same data re-aggregated. Zone income = population-weighted mean; alternative units by areal interpolation on districts_alt.geojson (assumes uniform spread within a district). Synthetic, CDB601220 Week 5.")); plt.close(fig)

# =============================================================== CASE 8
say("\n=== CASE 8  'rural outbreak' ===")
dh["cl"] = class_of(dh.rate.to_numpy(), edges_nat)
t5 = dh.nlargest(5, "population")
say(f"five most populous districts: {t5.area_km2.sum()/dh.area_km2.sum():.1%} of land, {t5.population.sum()/dh.population.sum():.1%} of population; their classes: " + ", ".join(f"{r.code}=class {r.cl+1}" for r in t5.itertuples()))
cl = dh.groupby("cl").agg(n=("code", "count"), area=("area_km2", "sum"), pop=("population", "sum"))
cl["a"] = cl.area / cl.area.sum(); cl["p"] = cl["pop"] / cl["pop"].sum()
say("share of LAND vs share of PEOPLE by class: " + "; ".join(f"class {i+1}: {r.a:.1%} land / {r.p:.1%} people" for i, r in cl.iterrows()))
tt = dh[dh.cl >= 3]
say(f"top two classes: {len(tt)} districts, {tt.area_km2.sum()/dh.area_km2.sum():.1%} of land, {tt.population.sum()/dh.population.sum():.1%} of people; their pooled density {tt.population.sum()/tt.area_km2.sum():.0f}/km2 vs {dh[dh.cl<3].population.sum()/dh[dh.cl<3].area_km2.sum():.0f}/km2 for the rest")
say(f"decoy check: r(rate, density) = {dh.rate.corr(dh.density):.3f} (Spearman {stats.spearmanr(dh.rate, dh.density).statistic:.2f}); lightest class contains the densest districts? densest 3: " + ", ".join(f"{r.code} ({r.density:.0f}/km2, class {r.cl+1})" for r in dh.nlargest(3, 'density').itertuples()))
say(f"dark districts include D13 (density {ix.density['D13']:.0f}/km2) and sparse D04 ({ix.density['D04']:.1f}/km2) is class {int(dh.cl[dh.code=='D04'].iloc[0])+1}")
fig, ax = plt.subplots(figsize=(6.4, 4.2))
choropleth(ax, feats, rate, "natural", 5, legend_title="Cases per 100,000\nnatural breaks", fmt="{:.1f}", legend_loc="center left", legend_anchor=(1.0, 0.5))
title(ax, "\"This is a rural outbreak: look how much of the map is dark\"", pub=True)
save_fig(fig, S(8, "published"), note("Rebuilt: rate choropleth, five natural breaks, Blues. Source: district_health.csv, districts.geojson (synthetic, CDB601220 Week 5). Equal-area projection.")); plt.close(fig)
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(9.6, 4.2), gridspec_kw={"width_ratios": [1.0, 1.0, 1.0]})
choropleth(a1, feats, rate, "natural", 5, legend=False); a1.set_title("Map: land area", loc="left", fontsize=9)
sh = class_shades(5); d = dh.sort_values("rate")
a2.barh(d.code, d.rate, color=[sh[int(c)] for c in d.cl], edgecolor="white"); a2.axvline(pooled_d, color=PALETTE["ink"], ls="--", lw=1)
a2.tick_params(axis="y", labelsize=6); a2.set_xlabel("Cases per 100,000"); a2.grid(axis="y", visible=False); a2.set_title("Sorted rate (from zero)", loc="left", fontsize=9)
xs = np.arange(5); a3.bar(xs - 0.2, cl.a * 100, 0.4, color=PALETTE["muted"], label="share of land"); a3.bar(xs + 0.2, cl.p * 100, 0.4, color=PUB, label="share of people")
a3.set_xticks(xs); a3.set_xticklabels([f"class {i+1}" for i in xs], fontsize=7); a3.set_ylabel("% of country"); a3.legend(fontsize=7.5, loc="upper left")
a3.set_title("Land vs people, by class", loc="left", fontsize=9)
fig.suptitle("Colour measures land, not people: 5 districts hold 60% of residents on 13% of the land, and rate shows no urban-rural pattern", x=0.01, ha="left", fontsize=9.5, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.92))
save_fig(fig, S(8, "redesign"), note("Redesign: sorted bars (from zero) beside the map, plus land share vs population share per class. Source: district_health.csv (synthetic, CDB601220 Week 5). Natural breaks as in D3. Equal-area projection.")); plt.close(fig)

# =============================================================== CASE 9
say("\n=== CASE 9  radar chart ===")
rp = pd.read_csv(DATA / "region_profiles.csv")
A, B = rp.region_a.to_numpy(), rp.region_b.to_numpy()
say(f"means {A.mean():.1f} and {B.mean():.1f}: difference {A.mean()-B.mean():.2f} on a 0-100 scale; enclosed areas in file order {radar_area(A):,.0f} and {radar_area(B):,.0f}")
diffs = []
for perm in itertools.permutations(range(1, 6)):
    o = (0,) + perm
    if o[1] > o[-1]: continue
    diffs.append(radar_area(A[list(o)]) - radar_area(B[list(o)]))
diffs = np.array(diffs)
say(f"all {len(diffs)} distinct axis orders: A wins in {(diffs>0).sum()}, B wins in {(diffs<0).sum()}; (A-B) area ranges {diffs.min():,.0f} to {diffs.max():,.0f}")
wins = (A > B).sum(); say(f"indicator by indicator: A higher on {wins}, B higher on {6-wins}; sum of scores {A.sum():.0f} vs {B.sum():.0f}")
say("decoy check: the area gap is not a size effect in the data: " + f"A-B per indicator = " + ", ".join(f"{i} {a-b:+.1f}" for i, a, b in zip(rp.indicator, A, B)))
ang = np.linspace(0, 2 * np.pi, 7)
fig, ax = plt.subplots(figsize=(5.2, 3.9), subplot_kw={"projection": "polar"})
for v, c, lab in [(A, PALETTE["series"][0], "Region A"), (B, PALETTE["series"][1], "Region B")]:
    vv = np.r_[v, v[0]]; ax.fill(ang, vv, color=c, alpha=0.3); ax.plot(ang, vv, color=c, lw=1.5, label=lab)
ax.set_xticks(ang[:-1]); ax.set_xticklabels(rp.indicator, fontsize=8); ax.set_ylim(0, 100); ax.set_yticks([25, 50, 75]); ax.tick_params(axis="y", labelsize=6)
ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8); ax.set_title("PUBLISHED, rebuilt: \"Region A is\nthe stronger: more enclosed area\"", loc="left", fontsize=9.5, pad=14)
ax.text(0.5, -0.12, f"enclosed area: A {radar_area(A):,.0f}  B {radar_area(B):,.0f}", transform=ax.transAxes, ha="center", fontsize=8)
save_fig(fig, S(9, "published"), "Rebuilt: radar, six axes in file order, fill alpha 0.3. Source: region_profiles.csv (synthetic, CDB601220 Week 5)."); plt.close(fig)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 3.9), gridspec_kw={"width_ratios": [1.15, 1]})
o = np.argsort(A - B); y = np.arange(6)
a1.hlines(y, np.minimum(A, B)[o], np.maximum(A, B)[o], color=PALETTE["grid"], lw=3, zorder=1)
a1.scatter(A[o], y, s=50, color=PALETTE["series"][0], zorder=3, label=f"Region A (mean {A.mean():.1f})"); a1.scatter(B[o], y, s=50, color=PALETTE["series"][1], zorder=3, label=f"Region B (mean {B.mean():.1f})")
a1.set_yticks(y); a1.set_yticklabels(rp.indicator[o]); a1.set_xlim(0, 100); a1.set_xlabel("Rating (0-100)"); a1.legend(loc="lower right", fontsize=8)
a1.set_title("Each indicator on a common scale:\n3 wins each, means 62.3 vs 62.0", loc="left", fontsize=9.5)
a2.hist(diffs, bins=14, color=PALETTE["muted"], edgecolor="white"); a2.axvline(0, color=PALETTE["ink"], lw=1)
a2.axvline(radar_area(A) - radar_area(B), color=PUB, lw=1.5); a2.text(radar_area(A) - radar_area(B) + 40, a2.get_ylim()[1] * .9, "file order", color=PUB, fontsize=8)
a2.set_xlabel("Enclosed area A minus B"); a2.set_ylabel("Number of axis orders (of 60)"); a2.set_title(f"Reorder the axes and the winner flips:\nA wins {(diffs>0).sum()} orders, B wins {(diffs<0).sum()}", loc="left", fontsize=9.5)
save_fig(fig, S(9, "redesign"), note("Redesign: dumbbell on a common axis; histogram of area(A) - area(B) over all 60 distinct six-axis orders. Source: region_profiles.csv (synthetic, CDB601220 Week 5).")); plt.close(fig)

(HERE / "partA_numbers.txt").write_text("\n".join(NUM) + "\n")
print("\nwrote 18 figures to figs/ and partA_numbers.txt")
