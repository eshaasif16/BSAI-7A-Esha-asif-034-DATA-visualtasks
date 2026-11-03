"""Part C - the two-map activity: build both maps, then score the readers.

Run once to build the maps (partC_mapA.png / partC_mapB.png / side-by-side).
Show readers partC_mapA.png ALONE first, then partC_mapB.png (see the protocol file).
Fill partC_reader_results.csv with your REAL readers, then run again: it scores them.
"""
import csv, sys
from w5common import *

style_defaults()
cc = pd.read_csv(DATA / "county_crime.csv")
cc["rate"] = cc.crimes_reported / cc.population * 1e5
geo = read_geojson(DATA / "districts.geojson")

# join on code; four polygons (D21-D24) have no county and are LEFT OUT
by_code = {f["code"]: f for f in geo}
feats = [by_code[c] for c in cc.code if c in by_code]
unmatched_geo = sorted(set(by_code) - set(cc.code))
unmatched_tab = sorted(set(cc.code) - set(by_code))
print(f"join: {len(feats)} counties matched; polygons with no county (left out): {unmatched_geo}; "
      f"table rows with no polygon: {unmatched_tab}")
name = dict(zip(cc.code, cc.county))
cnt, rate = dict(zip(cc.code, cc.crimes_reported)), dict(zip(cc.code, cc.rate))

# self-check numbers
print("r(crimes_reported, population) = %.3f" % cc.crimes_reported.corr(cc.population))
t_cnt = cc.nlargest(3, "crimes_reported").county.tolist(); t_rate = cc.nlargest(3, "rate").county.tolist()
print("top 3 by count:", t_cnt, "| by rate:", t_rate, "| overlap:", len(set(t_cnt) & set(t_rate)))
rc = cc.crimes_reported.rank(ascending=False); rr = cc.rate.rank(ascending=False)
mv = (rc - rr).abs()
print("counties that move >=3 places between the two rankings:", int((mv >= 3).sum()))
for c in ("Elmsworth", "Hollowfield"):
    i = cc.index[cc.county == c][0]
    print(f"{c}: population {cc.population[i]:,}, count rank {int(rc[i])} of 20 -> rate rank {int(rr[i])} of 20")

SCHEME = "natural"
def draw(ax, vals, title_leg, fmt, labels=True):
    e = choropleth(ax, feats, vals, SCHEME, 5, cmap=PALETTE["sequential"], legend_title=title_leg,
                   fmt=fmt, legend_loc="upper left", legend_anchor=(0.0, 0.0))
    if labels:
        xy = label_xy(feats)
        idx = class_of([vals[f["code"]] for f in feats], e)
        for f, c in zip(feats, idx):
            ax.annotate(name[f["code"]], xy[f["code"]], ha="center", va="center", fontsize=5.5,
                        color="white" if c >= 3 else PALETTE["ink"], zorder=7)
    return e

cap = ("Boundaries: districts.geojson (24 polygons, synthetic, CDB601220 Week 5); county_crime.csv joined on code. "
       f"{len(feats)} counties mapped; the {len(unmatched_geo)} polygons {', '.join(unmatched_geo)} have no county data and are left out (blank). "
       f"Same five-class Jenks natural breaks and Blues ramp on both maps. Equal-area projection. Extracted {DATE}.")
figA, ax = plt.subplots(figsize=(6, 7.2)); figA.subplots_adjust(bottom=0.27)
eA = draw(ax, cnt, "Crimes reported (count)\nJenks natural breaks, 5 classes", "{:,.0f}")
ax.set_title("Map A: crimes reported by county", loc="left")
save_fig(figA, HERE / "partC_mapA.png", cap)
figB, ax = plt.subplots(figsize=(6, 7.2)); figB.subplots_adjust(bottom=0.27)
eB = draw(ax, rate, "Crimes reported per 100,000 residents\nJenks natural breaks, 5 classes", "{:,.0f}")
ax.set_title("Map B: crimes per 100,000 residents", loc="left")
save_fig(figB, HERE / "partC_mapB.png", cap)
fig, axs = plt.subplots(1, 2, figsize=(12, 7.4)); fig.subplots_adjust(bottom=0.27, wspace=0.05)
draw(axs[0], cnt, "Crimes reported (count)\nJenks natural breaks, 5 classes", "{:,.0f}")
draw(axs[1], rate, "Crimes reported per 100,000 residents\nJenks natural breaks, 5 classes", "{:,.0f}")
axs[0].set_title("Map A: the count", loc="left"); axs[1].set_title("Map B: the rate", loc="left")
fig.suptitle("Same counties, same classes, same ramp: only the denominator differs, and the dark counties are different ones",
             x=0.01, ha="left", fontsize=12, fontweight="bold", y=0.97)
save_fig(fig, HERE / "partC_maps_side_by_side.png", cap)
print("A breaks:", [round(x) for x in eA], "| B breaks:", [round(x) for x in eB])
print("Map A is a map of where the people are; Map B is a map of how much reported crime there is per resident.")

# ---------------- reader results (REAL readers only) -----------------------------
FIELDS = ["reader_id", "a1", "a2", "a3", "b1", "b2", "b3", "overlap_count", "notes"]
path = HERE / "partC_reader_results.csv"
if not path.exists():
    with open(path, "w", newline="") as fh:
        csv.writer(fh).writerow(FIELDS)
rows = list(csv.DictReader(open(path)))
rows = [r for r in rows if r.get("reader_id", "").strip()]
valid = set(cc.county)
if not rows:
    print("\nNo reader rows yet. Run the experiment with REAL people (see partC_reader_protocol.md), "
          "fill partC_reader_results.csv, then rerun this script.")
    sys.exit(0)
ov = []
for r in rows:
    A = {r[k].strip() for k in ("a1", "a2", "a3")}; B = {r[k].strip() for k in ("b1", "b2", "b3")}
    bad = (A | B) - valid
    if bad: print(f"WARNING reader {r['reader_id']}: not county names: {sorted(bad)}")
    o = len(A & B); ov.append(o)
    if r.get("overlap_count", "").strip() and int(r["overlap_count"]) != o:
        print(f"WARNING reader {r['reader_id']}: recorded overlap {r['overlap_count']} but picks give {o}")
print(f"\nreaders: {len(rows)}   overlap per reader: {ov}   MEAN overlap = {np.mean(ov):.2f} of 3")
if len(rows) < 5: print("!! fewer than 5 readers - the brief needs at least five real ones.")
cnt_hit = np.mean([len({r[k].strip() for k in ('a1','a2','a3')} & set(t_cnt)) for r in rows])
rate_hit = np.mean([len({r[k].strip() for k in ('b1','b2','b3')} & set(t_rate)) for r in rows])
print(f"readers' Map A picks that were the top-3 by count: {cnt_hit:.2f}/3; Map B picks that were top-3 by rate: {rate_hit:.2f}/3")
