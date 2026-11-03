"""Part B - the five spatial and channel decisions, computed not asserted.
Prints everything and also writes partB_output.txt."""
import io, contextlib
from scipy import stats
from scipy.stats import gaussian_kde
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from w5common import *
from vizlib import lie_factor, lie_verdict

style_defaults()
OUT = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s); OUT.append(s)
def head(t):
    say("\n" + "=" * 74); say(t); say("=" * 74)

# ------------------------------------------------------------------ B1
head("B1  The size range (health_indicators.csv)")
hi = load_health()
lo_pt, hi_pt = K_AREA * hi.pop_m.min(), K_AREA * hi.pop_m.max()
say(f"I use area = {K_AREA:g} pt^2 per million people, i.e. sizes=({lo_pt:.1f}, {hi_pt:,.0f}) in points^2.")
say("  (matplotlib's s is the marker's diameter squared, so diameter = sqrt(s) points; area is proportional to s.)")
say(f"  smallest mark: {hi.pop_m.min()} M -> {lo_pt:.1f} pt^2 -> diameter {math.sqrt(lo_pt):.2f} pt = "
    f"{math.sqrt(lo_pt)*0.3528:.2f} mm. About 1 mm is the smallest dot I trust to survive print.")
say(f"  largest mark : {hi.pop_m.max()} M -> {hi_pt:,.0f} pt^2 -> diameter {math.sqrt(hi_pt):.1f} pt = "
    f"{math.sqrt(hi_pt)/72:.2f} in")
say(f"  population ratio {hi.pop_m.max()/hi.pop_m.min():.0f}x -> AREA ratio {hi_pt/lo_pt:.0f}x -> "
    f"DIAMETER ratio {math.sqrt(hi_pt/lo_pt):.1f}x  (= sqrt of 589)")
say(f"  area vs radius: if population drove the RADIUS the diameter ratio would be 589x and the area ratio "
    f"{589**2:,}x. I used area, so it is {math.sqrt(hi_pt/lo_pt):.1f}x.")
lf, de, ge = lie_factor(hi.pop_m.min(), hi.pop_m.max(), lo_pt, hi_pt, ink_dimension=1)
say(f"  Lie Factor of the size channel (ink = area): {lf:.2f} -> {lie_verdict(lf)}")
lf2, *_ = lie_factor(hi.pop_m.min(), hi.pop_m.max(), 1.0, 589.0 ** 2 / 1.0, ink_dimension=1)
# swallowing test on the real D1 canvas
fig, ax = plt.subplots(figsize=(9.6, 6.2)); bubble(ax, hi, legend=False)
fig.subplots_adjust(right=0.78); fig.canvas.draw()
px = ax.transData.transform(np.column_stack([hi.gdp_pc, hi.healthcare_access]))
big = hi.pop_m.idxmax(); r_pt = math.sqrt(hi_pt) / 2 * fig.dpi / 72
inside = [hi.country[i] for i in range(len(hi)) if i != big and np.hypot(*(px[i] - px[big])) < r_pt]
say(f"  swallow test: centres of other marks inside the largest bubble ({hi.country[big]}): {len(inside)} {inside}")
plt.close(fig)
say("  candidate scales (area = k pt^2 per million), smallest dot vs neighbours under the biggest bubble:")
for kk in (8, 10, 12, 14, 16):
    fg, ax2 = plt.subplots(figsize=(9.6, 6.2)); bubble(ax2, hi, legend=False, k=kk)
    fg.subplots_adjust(right=0.78); fg.canvas.draw()
    p2 = ax2.transData.transform(np.column_stack([hi.gdp_pc, hi.healthcare_access]))
    rr = math.sqrt(kk * hi.pop_m.max()) / 2 * fg.dpi / 72
    n_in = sum(np.hypot(*(p2[i] - p2[big])) < rr for i in range(len(hi)) if i != big)
    plt.close(fg)
    say(f"    k={kk:2d}: smallest dot {math.sqrt(kk*hi.pop_m.min())*0.3528:.2f} mm, "
        f"largest {math.sqrt(kk*hi.pop_m.max())/72:.2f} in, {n_in} other centres inside the largest bubble")
say(f"  I keep k={int(K_AREA)}: it is the smallest k whose 0.6 M dot is ~1 mm across, and the biggest bubble stays under an inch. "
    "The largest bubble does overlap neighbours (alpha 0.62 keeps them visible), and the size legend carries real populations.")

# ------------------------------------------------------------------ B2
head("B2  Overplotting (scatter_dense.csv, 9,000 points)")
sd = pd.read_csv(DATA / "scatter_dense.csv")
CX, CY, RAD = 3.1, 3.0, 0.5
inc = np.hypot(sd.x - CX, sd.y - CY) < RAD
ALPHA, GRID = 0.06, 35
say(f"points within {RAD} of (3.1, 3.0): {inc.sum()}  (the planted cluster is 800)")
fig, axs = plt.subplots(2, 2, figsize=(10, 9))
lim = (-4.2, 4.6)
def prep(ax, t):
    ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect("equal"); ax.set_title(t, fontsize=10)
axs[0, 0].scatter(sd.x, sd.y, s=14, color=PALETTE["series"][0], linewidths=0); prep(axs[0, 0], "Opaque (s=14)")
axs[0, 1].scatter(sd.x, sd.y, s=14, color=PALETTE["series"][0], alpha=ALPHA, linewidths=0); prep(axs[0, 1], f"Transparent (alpha={ALPHA})")
hb = axs[1, 0].hexbin(sd.x, sd.y, gridsize=GRID, cmap="Blues", mincnt=1, extent=(*lim, *lim)); prep(axs[1, 0], f"Hexbin (gridsize={GRID})")
gx = np.linspace(*lim, 120); GX, GY = np.meshgrid(gx, gx)
kde = gaussian_kde(np.vstack([sd.x, sd.y]))(np.vstack([GX.ravel(), GY.ravel()])).reshape(GX.shape)
axs[1, 1].contourf(GX, GY, kde, levels=12, cmap="Blues"); prep(axs[1, 1], "2-D KDE (scipy gaussian_kde, Scott bandwidth)")
for ax in axs.ravel():
    ax.add_patch(plt.Circle((CX, CY), 0.75, fill=False, ec=PALETTE["highlight"], lw=1, ls="--"))
fig.suptitle("Same 9,000 points, four ways: all show a blob at (3.1, 3.0), only hexbin shows it is the densest spot",
             x=0.01, ha="left", fontweight="bold", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.97))
fig.canvas.draw()
# measure visibility on the rendered pixels: darkness inside the cluster disc vs. the ring around it
def ink(ax, cx, cy, r0, q=90):
    """q-th percentile pixel darkness inside a disc (peak ink, not diluted by the edge)."""
    im = np.asarray(fig.canvas.buffer_rgba())[..., :3].astype(float).mean(axis=2)
    fh = fig.canvas.get_width_height()[1]
    X0, Y0 = ax.transData.transform((cx, cy)); X1, _ = ax.transData.transform((cx + r0, cy))
    yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]
    d = np.hypot(xx - X0, yy - (fh - Y0))
    return float(np.percentile(255 - im[d < (X1 - X0)], q))
say(f"{'view':12s} {'peak ink: cluster':>18s} {'peak ink: core':>15s} {'cluster/core':>13s}   reading")
res = {}
for name, ax in zip(["opaque", "transparent", "hexbin", "KDE"], axs.ravel()):
    a_, c_ = ink(ax, CX, CY, 0.5), ink(ax, 0.0, 0.0, 0.5)
    ratio = a_ / c_; res[name] = ratio
    read = ("same ink as the core: cannot tell it is denser" if 0.9 <= ratio <= 1.1
            else "reads DENSER than the core" if ratio > 1.1 else "reads WEAKER than the core (smoothing)")
    say(f"{name:12s} {a_:18.0f} {c_:15.0f} {ratio:13.2f}   {read}")
say("In all four views the cluster shows up as a separate blob, because it sits clear of the main mass. "
    "Whether the picture also tells you it is the densest thing in the data differs by view - see the last column.")
save_fig(fig, HERE / "partB_overplot.png",
         f"Source: scatter_dense.csv ({SYN}); n=9,000. Dashed ring marks the cluster. alpha={ALPHA}, hexbin gridsize={GRID}.")
plt.close(fig)
say(f"I would publish: hexbin (gridsize={GRID}) with a colourbar of counts per bin: the reader can read how many points a cell holds, "
    f"and there is no smoothing bandwidth to defend. alpha={ALPHA} shows presence but the reader cannot recover counts; "
    "the KDE needs a bandwidth I would have to declare and, at the default, it flattens the compact cluster.")

# ------------------------------------------------------------------ B3
head("B3  Scaling and dimension reduction (health_indicators.csv)")
X = hi[PCP_COLS]
say(f"gdp_pc: min {hi.gdp_pc.min():,}  median {hi.gdp_pc.median():,.0f}  max {hi.gdp_pc.max():,}; "
    f"max is {hi.gdp_pc.max()/hi.gdp_pc.nlargest(2).iloc[1]:.1f}x the second largest")
say(f"{'scaling':10s} {'min':>7s} {'median':>8s} {'max':>8s} {'# |scaled|<0.10':>16s}   what it did to the gdp_pc axis")
zs = scale_frame(hi, PCP_COLS, "zscore")["gdp_pc"]; zo = zs.drop(zs.idxmax())
for how, txt in [("minmax", "58 of 60 crushed into the bottom tenth; one outlier sets the whole scale"),
                 ("zscore", f"outlier sits at +{zs.max():.1f} sd, the other 59 live between {zo.min():.1f} and {zo.max():+.1f}; shape kept, still outlier-dominated"),
                 ("rank", "uniform by construction; the outlier is just 'rank 60'; gap sizes are gone")]:
    s = scale_frame(hi, PCP_COLS, how)["gdp_pc"]
    say(f"{how:10s} {s.min():7.3f} {s.median():8.3f} {s.max():8.3f} {(s.abs() < 0.10).sum():16d}   {txt}")
Z = StandardScaler().fit_transform(X)
p = PCA().fit(Z)
evr = p.explained_variance_ratio_
say("PCA on the standardised columns, explained variance ratio: " + ", ".join(f"PC{i+1}={v:.3f}" for i, v in enumerate(evr)))
say(f"first two components: {evr[:2].sum():.3f} -> a two-axis picture of this dataset misses {1-evr[:2].sum():.1%} of its variance.")
say("loadings of PC1: " + ", ".join(f"{c}={v:+.2f}" for c, v in zip(PCP_COLS, p.components_[0])))

# ------------------------------------------------------------------ B4
head("B4  Project before you measure (districts.geojson)")
dh, feats = load_districts()
sph = np.array([polygon_area_km2(f["ring"]) for f in feats])
def shoelace(ring):
    x = np.array([p[0] for p in ring]); y = np.array([p[1] for p in ring])
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
deg = np.array([shoelace(f["ring"]) for f in feats])
latm = np.array([np.mean([p[1] for p in f["ring"]]) for f in feats])
north = np.argsort(-latm)[:4]
codes = np.array([f["code"] for f in feats])
sh_s, sh_d = sph / sph.sum(), deg / deg.sum()
say(f"four northernmost districts (by mean vertex latitude): {[str(c) for c in codes[north]]}")
say(f"  share of total area, spherical (correct) : {sh_s[north].sum():.2%}")
say(f"  share of total area, shoelace on degrees : {sh_d[north].sum():.2%}  "
    f"(over-states by {sh_d[north].sum()/sh_s[north].sum()-1:+.1%})")
dist = sh_d / sh_s - 1; k = int(np.argmax(np.abs(dist)))
say(f"most distorted single district: {codes[k]} ({feats[k]['name']}) at lat {latm[k]:.1f}: "
    f"true share {sh_s[k]:.2%}, degree-space share {sh_d[k]:.2%} ({dist[k]:+.1%})")
mer = []
for f in feats:
    x, y = geolib.mercator_xy([p[0] for p in f["ring"]], [p[1] for p in f["ring"]])
    mer.append(shoelace(list(zip(x, y))))
mer = np.array(mer); infl = mer / sph
say(f"Mercator area inflation (projected area / true area): min {infl.min():.3f} (south) .. max {infl.max():.3f} (north); "
    f"whole federation {mer.sum()/sph.sum():.3f}x")
say(f"  so the north is drawn {infl.max()/infl.min()-1:.1%} larger than the south for the same real land.")
say(f"  (Mercator's AREA factor is sec^2(latitude): sec^2(24 deg)=1.20, sec^2(36 deg)=1.53. geolib's docstring says sec(lat), "
    f"which is the LINEAR scale factor, so I measured the areas directly instead of trusting either.)")
say("Why that number matters: a choropleth encodes the value in colour AND in the district's drawn area. Mercator draws "
    f"every district {infl.min():.2f}-{infl.max():.2f}x too big and the north {infl.max()/infl.min()-1:.0%} bigger than the south, "
    "so the northern districts shout louder for the same real land. Only an equal-area projection keeps the drawn area honest. (slide 34)")

# ------------------------------------------------------------------ B5
head("B5  Small-area stability (smallarea_cases.csv)")
sm = pd.read_csv(DATA / "smallarea_cases.csv"); sm["rate"] = sm.cases / sm.population * 1e5
pooled = sm.cases.sum() / sm.population.sum() * 1e5
fl = funnel_limits(sm.population, pooled)
lam = pooled / 1e5 * sm.population
lo_l = (lam - 1.96 * np.sqrt(lam)) / sm.population * 1e5; hi_l = (lam + 1.96 * np.sqrt(lam)) / sm.population * 1e5
out = (sm.rate < lo_l) | (sm.rate > hi_l)
say(f"pooled rate {pooled:.2f} per 100,000 from {sm.cases.sum()} cases / {sm.population.sum():,} people, 40 units")
say(f"units outside the 95% Poisson funnel: {int(out.sum())} of 40 -> {list(sm.unit[out])}")
say(f"  by chance alone about 5% of 40 = 2 would fall outside, so {int(out.sum())} is fewer than noise alone would give - "
    "but the one that does is U32 itself, so I also ran the exact test:")
pex = stats.poisson.sf(8, pooled / 1e5 * 22000)
say(f"  exact Poisson check on U32: P(>=9 cases | expected {pooled/1e5*22000:.2f}) = {pex:.5f}; across 40 units ~{min(1,40*pex):.3f}. "
    "The data's own dictionary says the true rate is the same everywhere, so U32 is a rare tail draw, not a hotspot.")
dev = (sm.rate - pooled).abs()
ext = sm.loc[dev.nlargest(10).index]
rho = stats.spearmanr(sm.population, dev)
say("what it tells me about the case 6 map: the extreme ranks are filled by the smallest populations. "
    f"Of the 10 units furthest from {pooled:.2f}, {int((ext.population < 50000).sum())} have fewer than 50,000 people "
    f"(the median population of all 40 is {sm.population.median():,.0f}, so about 5 would be expected if size did not matter). "
    f"The rank correlation between population and distance from the pooled rate is only {rho.statistic:+.2f}, because many small units "
    "are also close to the pooled rate; the signature of small numbers is the SPREAD, not the average distance: "
    f"the standard deviation of the rates is {sm[sm.population<30000].rate.std():.1f} for the {int((sm.population<30000).sum())} units under 30,000 people "
    f"against {sm[sm.population>=100000].rate.std():.1f} for the {int((sm.population>=100000).sum())} units over 100,000. "
    f"The units over 100,000 all sit between {sm[sm.population>1e5].rate.min():.1f} and {sm[sm.population>1e5].rate.max():.1f}, "
    f"while the units under 30,000 range from {sm[sm.population<30000].rate.min():.1f} to {sm[sm.population<30000].rate.max():.1f}.")
rate_a, rate_b = 9.0, 18.0
Nmin1 = (1.96 / (rate_b - rate_a)) ** 2 * rate_a * 1e5
Nmin2 = (1.96 / (rate_b - rate_a)) ** 2 * (rate_a + rate_b) * 1e5
say(f"minimum population to tell 9 from 18 per 100,000:")
say(f"  one unit against a KNOWN rate of 9 (18 outside its 95% upper limit): N >= {Nmin1:,.0f}")
say(f"  two units, each with its own sampling error (the realistic case):   N >= {Nmin2:,.0f} each")
say(f"  {(sm.population >= Nmin2).sum()} of the 40 units reach the second threshold; {(sm.population >= Nmin1).sum()} reach the first.")
fig, ax = plt.subplots(figsize=(9, 5.6))
grid = funnel_limits(np.linspace(3000, 280000, 300), pooled)
ax.fill_between(grid.population, grid.lo, grid.hi, color=PALETTE["grid"], label="95% Poisson limits")
ax.axhline(pooled, color=PALETTE["ink_soft"], lw=1, ls="--", label=f"pooled rate {pooled:.2f}")
ax.scatter(sm.population[~out], sm.rate[~out], s=26, color=PALETTE["series"][0], zorder=3, label="inside limits")
ax.scatter(sm.population[out], sm.rate[out], s=50, color=PALETTE["highlight"], zorder=4, label="outside limits")
for _, r in sm[out].iterrows():
    ax.annotate(f"{r.unit}: {r.cases:.0f} cases in {r.population:,.0f}", (r.population, r.rate), xytext=(12, -4), textcoords="offset points", fontsize=8)
ax.set_xlabel("Population of unit"); ax.set_ylabel("Cases per 100,000"); ax.set_ylim(0, 48)
ax.legend(loc="upper right")
ax.set_title("The wild rates sit where populations are small; only U32 leaves the funnel", loc="left")
save_fig(fig, HERE / "partB_funnel.png", f"Source: smallarea_cases.csv ({SYN}); n=40 units, none excluded. Limits: pooled rate +/- 1.96 sqrt(expected) (geolib.funnel_limits).")
plt.close(fig)
(HERE / "partB_output.txt").write_text("\n".join(OUT) + "\n")