"""
w4common.py - the cleaning that Part B, Part D and Part E all rely on.

It lives in one place on purpose: if Part B smoothed a different series from
the one Part D plotted, none of the numbers in the write-up would line up.

Every path is built from this file's own location, so the scripts run the same
way from any folder, on any machine (no /home/... paths anywhere).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

DATA_NOTE = "Synthetic data generated for CDB601220 (Data Visualization, Week 4)."


def clean_sessions() -> dict:
    """
    Load sessions_hourly.csv and fix its six faults, in the order they appear.

    Returns a dict with:
        hourly   cleaned hourly frame on a sorted DatetimeIndex
        daily    daily sessions (sum of hourly flows), reindexed to a complete
                 calendar - the 13 unrecorded days are NaN, not 0
        log      every number the write-up quotes about what was removed
    """
    raw = pd.read_csv(DATA / "sessions_hourly.csv")
    log: dict = {"n_raw": int(len(raw))}

    # ---- 1. two timestamp formats ------------------------------------------
    # ISO rows look like 2024-04-29 11:00:00; the others look like 05/10/2024
    # 09:00. Which is day-first and which is month-first? Prove it from the
    # file: a first field above 12 can only be a day, a second field above 12
    # would mean month-first.
    is_iso = raw.ts.str.contains("-", regex=False)
    slash = raw.ts[~is_iso].str.extract(r"^(\d{2})/(\d{2})/")
    first_gt12 = int((slash[0].astype(int) > 12).sum())
    second_gt12 = int((slash[1].astype(int) > 12).sum())
    log.update(n_iso=int(is_iso.sum()), n_slash=int((~is_iso).sum()),
               slash_first_gt12=first_gt12, slash_second_gt12=second_gt12)
    assert second_gt12 == 0 and first_gt12 > 0, "slash dates are not day-first"

    t = pd.Series(pd.NaT, index=raw.index, dtype="datetime64[ns]")
    t[is_iso] = pd.to_datetime(raw.ts[is_iso], format="%Y-%m-%d %H:%M:%S")
    t[~is_iso] = pd.to_datetime(raw.ts[~is_iso], format="%d/%m/%Y %H:%M")
    assert t.notna().all()

    # what the lazy parse would have done, so the write-up can say how wrong it
    mixed = pd.to_datetime(raw.ts, format="mixed")
    log.update(mixed_min=str(mixed.min().date()), mixed_max=str(mixed.max().date()),
               right_min=str(t.min().date()), right_max=str(t.max().date()),
               n_rows_moved_by_mixed=int((mixed.values != t.values).sum()))

    df = raw.assign(t=t)
    log["sorted_on_arrival"] = bool(df.t.is_monotonic_increasing)

    # ---- 2. duplicates (only visible once the index is real) ----------------
    dup = df.t.duplicated(keep="first")
    conflicting = int((df.groupby("t")[["sessions", "orders", "revenue_pkr"]]
                         .nunique().max(axis=1) > 1).sum())
    log.update(n_duplicates=int(dup.sum()), dup_with_conflicting_values=conflicting)
    df = df[~dup]

    # ---- 3. device spelled three ways ---------------------------------------
    log["device_raw"] = {k: int(v) for k, v in raw.device.value_counts().items()}
    df = df.assign(device=df.device.str.strip().str.lower())
    log["device_clean"] = {k: int(v) for k, v in df.device.value_counts().items()}

    df = df.set_index("t").sort_index()
    df.index.name = "ts"

    # ---- 4. sentinel -1 in sessions -----------------------------------------
    sent = df.sessions == -1
    log.update(n_sentinel_raw_rows=int((raw.sessions == -1).sum()),
               n_sentinel=int(sent.sum()),
               n_sentinel_days=int(df.index[sent].normalize().nunique()))
    log["total_sessions_with_sentinel"] = int(df.sessions.sum())
    log["mean_hourly_with_sentinel"] = float(df.sessions.mean())
    df["sessions"] = df.sessions.mask(sent)
    log["total_sessions_without"] = int(df.sessions.sum())
    log["mean_hourly_without"] = float(df.sessions.mean())

    # ---- 5. gaps: count them on the HOURLY index, before any resample -------
    full_h = pd.date_range(df.index.min(), df.index.max(), freq="h")
    missing_h = full_h.difference(df.index)
    miss_days = pd.Series(1, index=missing_h).groupby(missing_h.normalize()).sum()
    log.update(n_hours_expected=int(len(full_h)), n_hours_present=int(len(df)),
               n_hours_missing=int(len(missing_h)),
               missing_days=[str(d.date()) for d in miss_days.index],
               n_missing_days=int(len(miss_days)),
               missing_days_all_24h=bool((miss_days == 24).all()))

    # ---- 6. aggregation: a flow is summed ------------------------------------
    daily = df.sessions.resample("D").sum(min_count=1)
    log["n_days_expected"] = int(len(daily))
    log["n_days_recorded"] = int(daily.notna().sum())
    obs = df.sessions.resample("D").count()
    log["n_days_with_dropped_hour"] = int(((obs > 0) & (obs < 24)).sum())

    # ---- partial final month -------------------------------------------------
    last = daily.index.max()
    log.update(last_day=str(last.date()),
               tail_month=str(last.to_period("M")),
               tail_days=int(last.day),
               tail_month_days=int(last.days_in_month))

    return {"hourly": df, "daily": daily, "log": log, "obs_per_day": obs}


def fill_for_models(daily: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    A few tools (seasonal_decompose, a 31-day rolling mean) refuse NaN. For
    THOSE calls only, fill the unrecorded days by linear interpolation and
    return the filled series plus a boolean mask of which days were invented,
    so every user of it can say so on the page.
    """
    mask = daily.isna()
    return daily.interpolate(method="linear"), mask


def clean_catalogue() -> dict:
    """
    Load revenue_catalogue.csv and make it a tree: every SKU once, no negative
    area. Returns the positive-net frame, the negative rows, and a log.
    """
    c = pd.read_csv(DATA / "revenue_catalogue.csv")
    log: dict = {"n_raw": int(len(c))}

    # a duplicated SKU lands in two different parents, so the tree has a node
    # with two parents - and the sub-category shares drift by ~0.9 points.
    dup_mask = c.sku.duplicated(keep="first")
    dups = c[c.sku.isin(c.sku[dup_mask])].sort_values("sku")
    log["n_dup_sku"] = int(dup_mask.sum())
    log["dup_rows"] = dups.to_dict("records")
    # SKU-0127 is called AUDI-04, so it belongs to Audio. keep="first" keeps
    # exactly that row (the Wearables copy sits at the bottom of the file).
    c = c[~dup_mask]
    log["dup_kept_parent"] = str(dups.iloc[0].subcategory) if len(dups) else None

    # SKU-name prefix must agree with its sub-category (a sanity check on the
    # choice above, not a rule that changes any number)
    prefix = {"PHON": "Phones", "ACCE": "Accessories", "LAPT": "Laptops",
              "AUDI": "Audio", "CAME": "Cameras", "DRON": "Drones",
              "WEAR": "Wearables", "FOOT": "Footwear"}
    mism = c[c.sku_name.str[:4].map(prefix) != c.subcategory]
    log["n_prefix_mismatch_after_dedupe"] = int(len(mism))

    # each sub-category must sit under exactly one category
    parents = c.groupby("subcategory").category.nunique()
    log["subcats_with_two_parents"] = int((parents > 1).sum())

    neg = c[c.net_revenue_pkr_m < 0].sort_values("net_revenue_pkr_m")
    zero = c[c.net_revenue_pkr_m == 0]
    pos = c[c.net_revenue_pkr_m > 0]
    log.update(n_negative=int(len(neg)), negative_total=float(neg.net_revenue_pkr_m.sum()),
               n_zero=int(len(zero)), total_net_before=float(c.net_revenue_pkr_m.sum()),
               total_net_after=float(pos.net_revenue_pkr_m.sum()),
               n_after=int(len(pos)))
    return {"pos": pos, "neg": neg, "all": c, "log": log}


class Tee:
    """Print to the screen and keep a copy for <script>_output.txt."""

    def __init__(self, path):
        import io
        self.buf = io.StringIO()
        self.path = Path(path)

    def __call__(self, *a):
        line = " ".join(str(x) for x in a)
        print(line)
        self.buf.write(line + "\n")

    def close(self):
        self.path.write_text(self.buf.getvalue(), encoding="utf-8")
