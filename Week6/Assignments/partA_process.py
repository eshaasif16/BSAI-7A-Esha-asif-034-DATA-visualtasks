"""
Week 6 - Task A: make the files trustworthy.

    python3 partA_process.py

Reads the three raw CSVs and the GeoJSON from data/ (never touches them),
prints an audit, fixes what it finds, and writes:

    clean/district_grid_clean.csv     24 rows, one per code
    clean/grid_daily_clean.csv        one row per reported zone-day, ISO dates,
                                      with the meter turned into energy
    clean/zone_month_energy.csv       energy delivered per zone per month
    clean/generation_parts.csv        the 144 rows that are parts (no Total row)
    partA_audit.txt                   everything printed below, saved
    partA_decisions.md                what / how I found it / rule / rows

Nothing in clean/ is edited by hand. If a number in the decisions table is
wrong, the fix goes in this file and the table regenerates.

My own habit for this file: look first, decide second. Every fix below has a
detection step printed right above it, so the audit reads like the story of
how I found things.
"""
from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geolib   # noqa: E402  (week 5's toolkit, unchanged)
import tslib    # noqa: E402  (week 4's toolkit, unchanged)

DATA = HERE / "data"
CLEAN = HERE / "clean"
CLEAN.mkdir(exist_ok=True)

# ------------------------------------------------------------------ plumbing
_log = io.StringIO()
decisions = []          # one dict per decision, becomes partA_decisions.md


def say(*a):
    """print and remember, so partA_audit.txt is exactly what scrolled by"""
    line = " ".join(str(x) for x in a)
    print(line)
    _log.write(line + "\n")


def head(title):
    say("")
    say("=" * 74)
    say(title)
    say("=" * 74)


def decide(file, what, detected, rule, rows):
    decisions.append(dict(file=file, what=what, detected=detected,
                          rule=rule, rows=rows))


# =========================================================================
# 1. THE DISTRICT REGISTER   (25 rows - short enough to read, so I did)
# =========================================================================
head("district_grid.csv  (the register)")
reg_raw = pd.read_csv(DATA / "district_grid.csv")
reg = reg_raw.copy()

say("rows:", len(reg), "| columns:", reg.shape[1])
say("dtypes of the ones that matter:")
for c in ["population", "households", "area_km2", "electrification_pct",
          "outages", "outage_minutes"]:
    say(f"   {c:<22}{reg[c].dtype}")

# ---- key uniqueness ------------------------------------------------------
dup_codes = reg.code[reg.code.duplicated(keep=False)].unique().tolist()
say(f"\nkey `code` unique? {reg.code.is_unique}   duplicated codes: {dup_codes}")
if dup_codes:
    say(reg[reg.code.isin(dup_codes)].to_string(index=False))

# ---- text where a number should be --------------------------------------
ele_txt = reg.electrification_pct.astype("string")
pct_rows = reg.code[ele_txt.str.contains("%", na=False)].tolist()
blank_rows = reg.code[reg.electrification_pct.isna()].tolist()
say(f"\nelectrification_pct is {reg.electrification_pct.dtype}, not numeric.")
say(f"   rows carrying a '%' sign: {pct_rows}")
say(f"   rows that are genuinely blank: {blank_rows}")

# ---- operator codes -----------------------------------------------------
sent_reg = reg.code[reg.outage_minutes == -1].tolist()
say(f"\noutage_minutes == -1 in: {sent_reg}   (a code, not a duration)")

# ---- the things I am going to divide by ---------------------------------
reg["_pph"] = reg.population / reg.households
say("\nranges of everything I will divide by:")
say(f"   population   {reg.population.min():>12,} .. {reg.population.max():,}")
say(f"   households   {reg.households.min():>12,} .. {reg.households.max():,}")
say(f"   area_km2     {reg.area_km2.min():>12,.1f} .. {reg.area_km2.max():,.1f}")
say(f"   outages      {reg.outages.min():>12,} .. {reg.outages.max():,}")
say("   persons per household (population / households), sorted:")
srt = reg.sort_values("_pph")[["code", "district", "population",
                               "households", "_pph"]]
say(srt.iloc[[0, 1, 2, -3, -2, -1]].to_string(index=False,
                                               float_format="{:,.2f}".format))

# ---- join to the boundaries ---------------------------------------------
feats = geolib.read_geojson(Path(__file__).parent / "regions.geojson")
geo_codes = {f["code"]: f["name"] for f in feats}
missing_in_geo = sorted(set(reg.code) - set(geo_codes))
missing_in_reg = sorted(set(geo_codes) - set(reg.code))
say(f"\njoin register -> GeoJSON: {len(set(reg.code) & set(geo_codes))} matched, "
    f"{len(missing_in_geo)} register codes with no polygon, "
    f"{len(missing_in_reg)} polygons with no register row")

# ------------------------------- the fixes ---------------------------------
# (a) duplicate D11. Two rows, same code, near-identical numbers, two
#     spellings of the name. The boundary file is the authority on names, and
#     it says "Kotla", so that is the row I keep.
for code in dup_codes:
    n_before = len(reg)
    keep_name = geo_codes[code]
    reg = reg[~((reg.code == code) & (reg.district != keep_name))]
    dropped = n_before - len(reg)
    decide("district_grid", f"Duplicate key {code} (two rows, 'Kotla' and "
           f"'Kotla City')",
           "code.is_unique == False; the rows differ only in solar_kw (+12), "
           "outages (-3) and outage_minutes (-410)",
           f"Keep the row whose name matches regions.geojson ('{keep_name}'); "
           "drop the other. I cannot tell from the data alone which filing "
           "is the truer one, so this is a drop, not a repair",
           dropped)

# (b) '%' text and blanks in electrification_pct
before_nan = reg.electrification_pct.isna().sum()
reg["electrification_pct"] = pd.to_numeric(
    reg.electrification_pct.astype("string").str.replace("%", "", regex=False)
    .str.strip(), errors="coerce")
decide("district_grid", "electrification_pct stored as text; two rows carry a "
       "'%' sign",
       "dtype is object/str; str.contains('%') hit " + ", ".join(pct_rows),
       "Strip the '%' and convert to float. Blank cells stay missing (NaN), "
       "they are not zero and I do not fill them",
       len(pct_rows))
decide("district_grid", "electrification_pct genuinely blank",
       "isna() on the raw column: " + ", ".join(blank_rows),
       "Left as NaN. Any chart that uses this column has to say 3 districts "
       "are missing",
       int(before_nan))

# (c) -1 in outage_minutes
n_sent = int((reg.outage_minutes == -1).sum())
reg["outage_minutes"] = reg.outage_minutes.where(reg.outage_minutes != -1)
decide("district_grid", "outage_minutes carries -1 (operator's not-available "
       "code) for two districts",
       "min() was -1, a negative duration, on D09 and D20 only",
       "-1 -> NaN. Not 0 (zero would say 'no outage time'), and not imputed. "
       "Mean interruption length is therefore known for 22 of 24",
       n_sent)

# (d) households of D21 is 182
reg["_pph"] = reg.population / reg.households
others = reg.loc[reg.code != "D21", "_pph"]
bad = reg[(reg._pph < others.min() * 0.5) | (reg._pph > others.max() * 2)]
for _, r in bad.iterrows():
    fixed = r.households * 1000
    new_pph = r.population / fixed
    ok = others.min() <= new_pph <= others.max()
    say(f"\n{r.code}: households={r.households} -> persons/household "
        f"{r._pph:,.0f}.  x1000 gives {new_pph:.2f}  "
        f"(other districts {others.min():.2f}-{others.max():.2f}): "
        f"{'fits' if ok else 'DOES NOT FIT'}")
    if ok:
        reg.loc[reg.code == r.code, "households"] = fixed
        decide("district_grid", f"{r.code} ({r.district}) households = "
               f"{r.households}, for a district of {r.population:,} people",
               f"persons per household = {r._pph:,.0f}; every other "
               f"district is {others.min():.2f}-{others.max():.2f}",
               "REPAIR, not drop: the figure is the real count written in "
               "thousands (182 -> 182,000). I can state the true value and "
               f"the check: x1000 gives {new_pph:.2f} persons/household, "
               "inside the range of the other 23",
               1)
reg = reg.drop(columns="_pph")
reg = reg.sort_values("code").reset_index(drop=True)

# ---- the register's own area vs the polygon's area ----------------------
geo_area = {f["code"]: geolib.polygon_area_km2(f["ring"]) for f in feats}
ratio = reg.set_index("code").area_km2 / pd.Series(geo_area)
say(f"\nregister area_km2 vs polygon area (spherical): "
    f"{(ratio.min() - 1) * 100:+.3f}% .. {(ratio.max() - 1) * 100:+.3f}%")

say("\nregister after cleaning:")
say(f"   rows {len(reg)}, unique codes {reg.code.is_unique}")
say(f"   population {reg.population.sum():,}   households {reg.households.sum():,}")
pph = reg.population / reg.households
say(f"   persons per household {pph.min():.2f} - {pph.max():.2f}")
say(f"   electrification_pct {reg.electrification_pct.min():.1f} - "
    f"{reg.electrification_pct.max():.1f}, "
    f"{int(reg.electrification_pct.isna().sum())} missing")
usable = reg.outage_minutes.notna()
mil = (reg.outage_minutes / reg.outages)[usable]
say(f"   usable outage_minutes {int(usable.sum())} of {len(reg)}, "
    f"mean interruption {mil.min():.0f} - {mil.max():.0f} minutes")
say(f"   interruptions, all districts {reg.outages.sum():,}")
reg.to_csv(CLEAN / "district_grid_clean.csv", index=False)

# =========================================================================
# 2. THE DAILY RETURNS   (3,061 rows, nothing here is visible by reading)
# =========================================================================
head("grid_daily.csv  (six zones, daily)")
raw = pd.read_csv(DATA / "grid_daily.csv", dtype={"date": "string",
                                                   "zone": "string"})
say("rows:", len(raw), "| dtypes:", dict(raw.dtypes.astype(str)))
say("zones:", {k: int(v) for k, v in raw.zone.value_counts().sort_index().items()})

# ---- is the date column a date? -----------------------------------------
shape = raw.date.str.replace(r"\d", "9", regex=True).value_counts()
say("\nshape of the `date` strings:", {k: int(v) for k, v in shape.items()})
as_text = tslib.audit_index(raw.set_index("date"), "D")
say("audit_index on the raw text dates:",
    {k: as_text[k] for k in ("dtype_ok", "monotonic", "n_rows")})

slash = raw.date.str.contains("/", regex=False)
parts = raw.loc[slash, "date"].str.split("/", expand=True).astype(int)
say(f"\n{int(slash.sum())} rows are written dd/mm/yyyy-looking (with slashes).")
say(f"   middle field takes values {[int(v) for v in sorted(parts[1].unique())]}; "
    f"first field reaches {parts[0].max()}, so it can only be the day")
say(f"   year(s): {[int(v) for v in sorted(parts[2].unique())]}")

iso = ~slash
d_iso = pd.to_datetime(raw.loc[iso, "date"], format="%Y-%m-%d")
nov25 = int(((d_iso >= "2025-11-01") & (d_iso <= "2025-11-30")).sum())
say(f"   ISO-format rows that fall in Nov 2025: {nov25}  "
    f"(so the slash rows ARE November, the whole month)")

daily = raw.copy()
daily["date"] = pd.NaT
daily.loc[iso, "date"] = d_iso
daily.loc[slash, "date"] = pd.to_datetime(raw.loc[slash, "date"],
                                          format="%d/%m/%Y")
daily["date"] = pd.to_datetime(daily["date"])
decide("grid_daily", "Dates in two formats: 2,887 ISO (yyyy-mm-dd) and 174 "
       "written dd/mm/yyyy, all in November 2025",
       "str shape counts; the slash rows' first field goes up to 30 so it is "
       "the day, and no ISO row falls in Nov 2025 so they are the whole month",
       "Parse each format explicitly (never format='mixed', never guess "
       "dayfirst). 09/11/2025 is 9 November. Dates are datetime64 from here "
       "on",
       int(slash.sum()))

# ---- duplicates ---------------------------------------------------------
key = ["zone", "date"]
n_keydup = int(daily.duplicated(key, keep="first").sum())
full_dup = int(daily.duplicated(key + ["cumulative_mwh", "peak_load_mw",
                                       "outage_minutes"],
                                keep="first").sum())
say(f"\nduplicate (zone, date) keys: {n_keydup} extra rows "
    f"({full_dup} identical copies, {n_keydup - full_dup} conflicting)")
g = daily[daily.duplicated(key, keep=False)].groupby(key)
conflict = [k for k, x in g
            if len(x.drop_duplicates(["cumulative_mwh", "peak_load_mw",
                                      "outage_minutes"])) > 1]
for k in conflict:
    say(f"   conflicting filing {k[0]} {k[1].date()}:")
    say(g.get_group(k)[["cumulative_mwh", "peak_load_mw",
                        "outage_minutes"]].to_string(index=False))
# keep the larger peak. peak_load is a daily maximum: if one filing saw a
# higher instantaneous demand, the lower one cannot have been the whole day.
daily = (daily.sort_values(key + ["peak_load_mw"])
         .drop_duplicates(key, keep="last").reset_index(drop=True))
decide("grid_daily", "Duplicate zone-days: 15 extra rows (12 exact copies, "
       "3 conflicting refilings)",
       f"duplicated(['zone','date']) -> {n_keydup}; the 3 conflicts have the "
       "same meter reading but different peak and outage_minutes",
       "One row per zone-day. Exact copies: drop one, no information lost. "
       "Conflicts: keep the filing with the higher peak_load_mw, because a "
       "daily maximum can only be revised upwards. This is a judgement, it "
       "touches 3 zone-days of 3,046, and the energy numbers do not depend "
       "on it",
       n_keydup)

# ---- sentinel in peak_load ----------------------------------------------
say("\nvalue counts at the bottom of peak_load_mw:",
    {k: int(v) for k, v in daily.peak_load_mw.value_counts().sort_index().head(3).items()})
n_neg_raw = int((raw.peak_load_mw == -1).sum())
n_neg = int((daily.peak_load_mw == -1).sum())
say(f"peak_load_mw == -1: {n_neg_raw} raw rows, {n_neg} after de-duplicating")
daily["peak_load_mw"] = daily.peak_load_mw.where(daily.peak_load_mw != -1)
for c in ("cumulative_mwh", "outage_minutes"):
    assert (daily[c] >= 0).all(), f"unexpected negative values in {c}"
say("no -1 (or any negative) in cumulative_mwh or outage_minutes.")
say(f"outage_minutes == 0 on {(daily.outage_minutes == 0).mean() * 100:.1f}% "
    "of zone-days, spread across all six zones: real quiet days, kept.")
decide("grid_daily", "peak_load_mw uses -1 as the operator's not-available "
       "code",
       f"min() == -1 on {n_neg_raw} raw rows ({n_neg} after removing "
       "duplicates); a peak demand cannot be negative",
       "-1 -> NaN. Not 0, not the zone's mean. The row stays, because its "
       "meter reading and outage minutes are still good; only the peak is "
       "missing. Charts using peak_load say 'n days excluded'",
       n_neg_raw)

# ---- calendar gaps ------------------------------------------------------
say("\ncalendar: every zone should report every day.")
daily = daily.sort_values(["zone", "date"]).reset_index(drop=True)
span = (daily.date.min(), daily.date.max())
n_days = (span[1] - span[0]).days + 1
slots = n_days * daily.zone.nunique()
say(f"span {span[0].date()} -> {span[1].date()} = {n_days} days x "
    f"{daily.zone.nunique()} zones = {slots} slots; rows kept {len(daily)}; "
    f"never reported {slots - len(daily)}")
gap_by_zone = {}
for z, gz in daily.groupby("zone"):
    a = tslib.audit_index(gz.set_index("date"), "D")
    gap_by_zone[z] = a["n_missing"]
    say(f"   {z}: audit_index dtype_ok={a['dtype_ok']} monotonic={a['monotonic']}"
        f" dup={a['n_duplicated']} missing={a['n_missing']} "
        f"partial_tail={a['partial_tail']}")
say("   missing zone-days by zone:", gap_by_zone)
all_slots = pd.MultiIndex.from_product(
    [pd.date_range(*span, freq="D"), sorted(daily.zone.unique())],
    names=["date", "zone"])
missing = all_slots.difference(pd.MultiIndex.from_frame(daily[["date", "zone"]]))
mm = pd.DataFrame(index=missing).reset_index()
by_month = mm.groupby(mm.date.dt.to_period("M")).size()
say(f"   missing per month ranges {by_month.min()}-{by_month.max()}; "
    f"P5 alone is {gap_by_zone['P5']} of {len(mm)} "
    f"({gap_by_zone['P5'] / len(mm) * 100:.0f}%), P1 is {gap_by_zone['P1']}")
say("   the last month is partial: the file stops on "
    f"{span[1].date()} ({span[1].day} days of September 2026)")
decide("grid_daily", "Calendar gaps: 128 zone-days never reported "
       "(P5 36, P4 24, P2 21, P6 20, P3 15, P1 12; not evenly spread). The "
       "span is 2025-04-01 -> 2026-09-11, so September 2026 is partial",
       "reindexed to the full 529-day x 6-zone calendar and counted what "
       "was missing (tslib.audit_index per zone)",
       "NOT filled and NOT dropped from anything: a missing day stays "
       "missing. Daily lines break at NaN. Monthly energy is read from the "
       "meter at month boundaries, which is unaffected by a missing day in "
       "the middle. Sept 2026 is flagged partial everywhere",
       len(mm))

# ---- the meter is a level, not a quantity -------------------------------
say("\ncumulative_mwh is a meter READING. Summing it is a deduction; the "
    "energy is the change.")
daily["days_since_prev"] = daily.groupby("zone").date.diff().dt.days
daily["_step"] = daily.groupby("zone").cumulative_mwh.diff()
reset = daily["_step"] < 0
say(f"zone-days where the reading goes DOWN: {int(reset.sum())}")
for _, r in daily[reset].iterrows():
    prev = daily[(daily.zone == r.zone) & (daily.date < r.date)].iloc[-1]
    say(f"   {r.zone} {r.date.date()}: {prev.cumulative_mwh:,.1f} on "
        f"{prev.date.date()} -> {r.cumulative_mwh:,.1f}")
    say("   a new meter was installed: the counter restarted near zero and "
        "the next days climb normally from there")
daily["meter_reset"] = reset
daily["energy_since_prev_mwh"] = daily["_step"].where(~reset)
daily = daily.drop(columns="_step")
sum_trap = daily[(daily.zone == "P1") &
                 (daily.date.dt.to_period("M") == "2026-06")
                 ].cumulative_mwh.sum()
decide("grid_daily", "cumulative_mwh is a meter reading (a level that only "
       "climbs), not energy delivered",
       "values run 1e6-6e7 and climb every day (bar one reset); the data "
       "dictionary says so; sum() of P1 for June 2026 gives "
       f"{sum_trap:,.0f} MWh",
       "Energy = difference between readings. Daily table gets "
       "energy_since_prev_mwh and days_since_prev (so a step that spans a "
       "gap says so). Monthly energy = reading on the 1st of next month "
       "minus reading on the 1st of this month (see zone_month_energy). "
       "Readings are never summed or resampled with sum()",
       len(daily))
decide("grid_daily", "One meter reset: P4 on 2026-02-17 reads 1,180 MWh "
       "after 21,444,255 the day before (new meter)",
       "diff() < 0 on exactly 1 zone-day",
       "The step across the reset is unknowable (the old meter's last "
       "reading is not on file), so energy_since_prev_mwh is NaN for that "
       "row, meter_reset=True, and P4's Feb-2026 monthly energy is NaN. "
       "Dropping would hide it, adding the two readings would invent a "
       "number: I leave it missing",
       int(reset.sum()))

# ---- monthly energy per zone --------------------------------------------
def month_energy(g):
    """energy per month from the meter, read on the 1st of each month.

    A reading missing on the 1st is linearly interpolated between the
    neighbouring readings OF THE SAME METER (a reset breaks the line). This is
    legitimate for a counter that rises steadily, and only used for the two
    boundary readings, never for a sum."""
    g = g.set_index("date").sort_index()
    seg = g.meter_reset.cumsum()                 # which meter are we on
    first_idx = pd.date_range(g.index.min().replace(day=1),
                              g.index.max(), freq="MS")
    rows = []
    for m0, m1 in zip(first_idx[:-1], first_idx[1:]):
        def at(day):
            if day in g.index:
                return g.at[day, "cumulative_mwh"], seg.at[day]
            lo = g.loc[:day]
            hi = g.loc[day:]
            if lo.empty or hi.empty:
                return np.nan, None
            if seg.at[lo.index[-1]] != seg.at[hi.index[0]]:
                return np.nan, None
            t = (day - lo.index[-1]) / (hi.index[0] - lo.index[-1])
            v = lo.cumulative_mwh.iloc[-1] + t * (hi.cumulative_mwh.iloc[0]
                                                  - lo.cumulative_mwh.iloc[-1])
            return v, seg.at[lo.index[-1]]
        a, sa = at(m0)
        b, sb = at(m1)
        e = b - a if (sa is not None and sa == sb) else np.nan
        rows.append((m0, e, (m1 - m0).days, True))
    # September 2026 is only partly in the file: first reading to last reading
    last_m = first_idx[-1]
    a, sa = (g.at[last_m, "cumulative_mwh"], seg.at[last_m]) \
        if last_m in g.index else (np.nan, None)
    b = g.cumulative_mwh.iloc[-1]
    rows.append((last_m, b - a if sa == seg.iloc[-1] else np.nan,
                 (g.index.max() - last_m).days, False))
    return pd.DataFrame(rows, columns=["month", "energy_mwh", "n_days",
                                       "complete"])


me = pd.concat([month_energy(g).assign(zone=z)
                for z, g in daily.groupby("zone")], ignore_index=True)
me["month"] = me.month.dt.to_period("M").astype(str)
me = me[["zone", "month", "energy_mwh", "n_days", "complete"]]
p1_jun = me[(me.zone == "P1") & (me.month == "2026-06")].energy_mwh.iloc[0]
say(f"\nenergy delivered, zone P1, June 2026: {p1_jun:,.0f} MWh")
say(f"   the same month if I sum() the column: {sum_trap:,.0f} MWh "
    f"({sum_trap / p1_jun:,.0f}x too big)")
say("   months with no usable energy figure:",
    me[me.energy_mwh.isna()][["zone", "month"]].values.tolist())
say("   partial final month (flagged complete=False):",
    me[~me.complete].month.unique().tolist())
decide("zone_month_energy", "Month boundary convention for energy delivered",
       "a reading is stamped with a date, a month needs two boundaries",
       "Energy in month M = reading on 1 M+1 minus reading on 1 M. If the "
       "reading on the 1st is missing it is interpolated between the "
       "neighbouring readings of the same meter. The other plausible "
       "convention (last day of the month) moves P1 June 2026 by about 0.09%. "
       "Stated so nobody has to guess which one I used",
       len(me))

# ---- final daily file ----------------------------------------------------
out_daily = daily.copy()
out_daily["date"] = out_daily.date.dt.strftime("%Y-%m-%d")
out_daily.to_csv(CLEAN / "grid_daily_clean.csv", index=False)
me.to_csv(CLEAN / "zone_month_energy.csv", index=False)

say(f"\ndaily after cleaning: {len(daily):,} zone-days kept, "
    f"{len(mm)} never reported, {int(daily.peak_load_mw.isna().sum())} "
    f"peak readings missing, {int(daily.meter_reset.sum())} meter reset")

# join to the register -------------------------------------------------------
zr = set(reg.zone)
zd = set(daily.zone)
say(f"join daily.zone -> register.zone: {len(zd & zr)} matched, "
    f"{len(zd - zr)} unmatched zones in daily, {len(zr - zd)} in register")

# =========================================================================
# 3. GENERATION MIX
# =========================================================================
head("generation_mix.csv  (monthly, 18 months)")
gen = pd.read_csv(DATA / "generation_mix.csv", dtype={"month": "string"})
say("rows:", len(gen), "| months:", gen.month.nunique(),
    "| rows per month:", [int(v) for v in sorted(gen.groupby("month").size().unique())])
say("key (month, source, subsource) unique?",
    not gen.duplicated(["month", "source", "subsource"]).any())
say("sources:", gen.source.unique().tolist())
say("month column parses as year-month:",
    bool(pd.to_datetime(gen.month, format="%Y-%m", errors="coerce").notna().all()))
say("mwh range:", f"{gen.mwh.min():,} .. {gen.mwh.max():,}", "(no zero, no negative)")

is_total = gen.source == "All sources"
parts_df = gen[~is_total].copy()
tot_pub = gen[is_total].set_index("month").mwh
parts_sum = parts_df.groupby("month").mwh.sum()
diff = (parts_sum - tot_pub).abs()
every = gen.groupby("month").mwh.sum()
say(f"\nexclusivity: is every row a part of the whole?")
say(f"   rows that are the 'All sources / Total' line: {int(is_total.sum())}")
say(f"   rows that are parts: {len(parts_df)} = "
    f"{parts_df.month.nunique()} months x {parts_df.groupby('month').size().iloc[0]} categories")
say(f"   parts summed vs published total: worst month off by {diff.max():.0f} MWh")
say(f"   every row summed vs the published total: "
    f"{(every / tot_pub * 100).min():.2f}% .. {(every / tot_pub * 100).max():.2f}%  "
    f"(a pie of the raw file would add to 200%)")
parts_df = parts_df.sort_values(["month", "source", "subsource"])
parts_df.to_csv(CLEAN / "generation_parts.csv", index=False)
decide("generation_mix", "The file contains its own total: 18 'All sources / "
       "Total' rows sitting beside the 144 parts",
       "summing every row gives 200% of the published total in every month "
       "(exclusivity test: parts are not mutually exclusive with the whole)",
       "Remove the Total rows from the table that gets plotted as parts "
       "(clean/generation_parts.csv, 144 rows). Keep the published total only "
       "as a check: the parts agree with it to within "
       f"{diff.max():.0f} MWh in all 18 months",
       int(is_total.sum()))

# =========================================================================
# 4. JOIN SUMMARY + WRITE
# =========================================================================
head("join summary")
say(f"GeoJSON features -> district register: "
    f"{len(set(reg.code) & set(geo_codes))} matched, "
    f"{len(missing_in_geo)} + {len(missing_in_reg)} unmatched")
bad_name = [(c, n) for c, n in geo_codes.items()
            if reg.set_index('code').district.get(c) != n]
say(f"names that disagree with the GeoJSON after cleaning: {bad_name or 'none'}")

head("expected-number checks (from the brief) vs what this script produced")
checks = [
    ("district rows", len(reg), 24),
    ("population", int(reg.population.sum()), 57_857_000),
    ("households", int(reg.households.sum()), 8_908_512),
    ("interruptions", int(reg.outages.sum()), 388_879),
    ("usable outage_minutes", int(usable.sum()), 22),
    ("zone-days kept", len(daily), 3_046),
    ("zone-days never reported", len(mm), 128),
    ("slots", slots, 3_174),
    ("unusable peak readings (raw rows)", n_neg_raw, 46),
    ("meter resets", int(daily.meter_reset.sum()), 1),
    ("P1 June 2026 energy MWh", round(p1_jun), 1_200_239),
    ("sum() of the meter column MWh", round(sum_trap), 574_845_315),
    ("generation part rows", len(parts_df), 144),
]
all_ok = True
for name, got, want in checks:
    ok = got == want
    all_ok &= ok
    say(f"   {'ok ' if ok else 'XX '} {name:<36}{got:>14,}   expected {want:,}")
say("\nall checks agree." if all_ok else "\nSOMETHING DISAGREES - look above.")

# ---- partA_audit.txt and partA_decisions.md ---------------------------------
(HERE / "partA_audit.txt").write_text(_log.getvalue(), encoding="utf-8")

lines = ["# Part A - decisions table", "",
         "Generated by `partA_process.py`; the row counts are computed, not "
         "typed. *Drop* = I could not state the true value. *Repair* = I "
         "could, and the rule says why.", "",
         "| # | File | What | How I detected it | The rule I applied | Rows affected |",
         "|---|---|---|---|---|---|"]
for i, d in enumerate(decisions, 1):
    esc = lambda s: str(s).replace("|", "/")  # noqa: E731
    lines.append(f"| {i} | {d['file']} | {esc(d['what'])} | "
                 f"{esc(d['detected'])} | {esc(d['rule'])} | {d['rows']:,} |")
(HERE / "partA_decisions.md").write_text("\n".join(lines) + "\n",
                                         encoding="utf-8")
print("\nwrote clean/*.csv, partA_audit.txt, partA_decisions.md")
