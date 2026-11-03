"""Shared helpers for the Week 5 scripts (loaders, bubble chart, PCP wrapper,
fixed-break choropleth, areal weighting). Everything sits on geolib/vizlib."""
from __future__ import annotations
import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Patch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path as MplPath

import geolib
from geolib import (PALETTE, style_defaults, save_fig, read_geojson, breaks,
                    gvf, choropleth, outlines, prop_symbols, size_legend,
                    scale_frame, pcp, funnel_limits, polygon_area_km2,
                    equal_area_xy, representative_point, class_of,
                    _project_ring, _collection_lat_ts)
from vizlib import worst_pair, verdict, delta_e

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
FIGS = HERE / "figs"
FIGS.mkdir(exist_ok=True)
DATE = "2 Nov 2026"
SYN = "synthetic data generated for CDB601220 Week 5"
PCP_COLS = ["gdp_pc", "healthcare_access", "urban_pct", "median_age",
            "cases_per_100k"]

# six regions: Okabe-Ito hues + a different marker each, so hue is never alone
REGIONS = ["Andara", "Borealis", "Caldera", "Dravira", "Esperia", "Fenwick"]
REGION_COL = dict(zip(REGIONS, ["#0072B2", "#D55E00", "#009E73",
                                "#CC79A7", "#E69F00", "#56B4E9"]))
REGION_MK = dict(zip(REGIONS, ["o", "s", "^", "D", "v", "P"]))


def load_health():
    return pd.read_csv(DATA / "health_indicators.csv")


def load_districts():
    dh = pd.read_csv(DATA / "district_health.csv")
    dh["rate"] = dh.cases / dh.population * 1e5
    dh["density"] = dh.population / dh.area_km2
    return dh, read_geojson(DATA / "districts.geojson")


def safe_corr_chain(df, cols):
    """geolib.corr_chain() with a .copy(): on pandas 3 the original tries to
    write into a read-only array. Same rule, same answer."""
    cols = list(cols)
    r = df[cols].corr().abs().to_numpy().copy()
    np.fill_diagonal(r, 0.0)
    i, j = np.unravel_index(np.argmax(r), r.shape)
    order = [i, j]
    while len(order) < len(cols):
        rest = [k for k in range(len(cols)) if k not in order]
        order.append(max(rest, key=lambda k: r[order[-1], k]))
    return [cols[k] for k in order]


def label_xy(feats):
    lat_ts = _collection_lat_ts(feats)
    pts = [representative_point(f["ring"]) for f in feats]
    x, y = equal_area_xy([p[0] for p in pts], [p[1] for p in pts], lat_ts=lat_ts)
    return {f["code"]: (a, b) for f, a, b in zip(feats, x, y)}


def choropleth_fixed(ax, feats, values, edges, cmap="Blues", legend_title="",
                     fmt="{:.1f}", edgecolor="white", lw=0.35,
                     legend_loc="upper left", legend_anchor=(1.0, 1.0)):
    """geolib.choropleth, but with class edges handed in (shared scale)."""
    k = len(edges) - 1
    vals = np.array([values[f["code"]] for f in feats], float)
    idx = class_of(vals, edges)
    cm = plt.get_cmap(cmap)
    shades = [cm(0.18 + 0.78 * c / max(k - 1, 1)) for c in range(k)]
    lat_ts = _collection_lat_ts(feats)
    patches, cols = [], []
    for f, c in zip(feats, idx):
        x, y = _project_ring(list(f["ring"]), "equal_area", lat_ts)
        patches.append(MplPolygon(np.column_stack([x, y]), closed=True))
        cols.append(shades[int(c)])
    ax.add_collection(PatchCollection(patches, facecolors=cols,
                                      edgecolors=edgecolor, linewidths=lw))
    ax.autoscale_view(); ax.set_aspect("equal"); ax.set_axis_off()
    n_in = [(idx == c).sum() for c in range(k)]
    labels = [f"{fmt.format(edges[c])} – {fmt.format(edges[c+1])}  (n={n_in[c]})"
              for c in range(k)]
    ax.legend(handles=[Patch(facecolor=shades[c], edgecolor=edgecolor,
                             label=labels[c]) for c in range(k)],
              title=legend_title, loc=legend_loc, bbox_to_anchor=legend_anchor,
              fontsize=8, title_fontsize=8, frameon=False)
    return idx, shades


def class_shades(k=5, cmap="Blues"):
    cm = plt.get_cmap(cmap)
    return [cm(0.18 + 0.78 * c / max(k - 1, 1)) for c in range(k)]


# ------------------------------------------------------------- bubble chart
K_AREA = 12.0   # points^2 per million people -> area exactly proportional


def bubble(ax, df, legend=True, k=K_AREA, alpha=0.62):
    """Four channels: x=gdp (log), y=access, AREA=pop (s = k*pop), hue=region.
    Circles only: matplotlib's `s` gives different visible areas to different
    marker glyphs, so mixing shapes would break 'area means area'. Dravira
    (pink) gets a dark outline as the second channel against green under
    deuteranopia (worst pair, delta E 7.5). Returns the sizes used."""
    s_all = k * df.pop_m.to_numpy()
    for reg in REGIONS:
        d = df[df.region == reg]
        ax.scatter(d.gdp_pc, d.healthcare_access, s=k * d.pop_m,
                   color=REGION_COL[reg], alpha=alpha,
                   edgecolor=_edge(reg), linewidth=_lw(reg), zorder=3)
    ax.set_xscale("log")
    ax.set_xlim(200, 2.2e5); ax.set_ylim(0, 100)
    ticks = [300, 1000, 3000, 10000, 30000, 100000]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"${t:,}" for t in ticks])
    ax.minorticks_off()
    ax.set_xlabel("GDP per capita, USD per person per year (log scale)")
    ax.set_ylabel("Healthcare access index (0\u2013100)")
    if legend:
        hue = [ax.scatter([], [], s=55, color=REGION_COL[r], label=r,
                          edgecolor=_edge(r), linewidth=_lw(r)) for r in REGIONS]
        l1 = ax.legend(handles=hue, title="Region (hue)", loc="upper left",
                       bbox_to_anchor=(1.01, 1.0), fontsize=8, title_fontsize=8,
                       frameon=False)
        ax.add_artist(l1)
        refs = [5, 50, 300]
        sz = [ax.scatter([], [], s=k * v, color=PALETTE["muted"], alpha=0.65,
                         edgecolor="white", label=f"{v} M people") for v in refs]
        ax.legend(handles=sz, title="Mark AREA = population", loc="upper left",
                  bbox_to_anchor=(1.01, 0.64), labelspacing=3.1, borderpad=1.0,
                  handletextpad=1.6, fontsize=8, title_fontsize=8, frameon=False)
    return s_all


def _edge(reg):
    return "#16202E" if reg == "Dravira" else "white"


def _lw(reg):
    return 1.1 if reg == "Dravira" else 0.7


# -------------------------------------------------------------- PCP wrapper
def pcp_figure(df, order, how, highlight, decl, title, figsize=(10, 6.6)):
    import textwrap
    fig, ax = plt.subplots(figsize=figsize)
    pcp(ax, df, order, how, highlight=highlight)
    ax.set_title(title, loc="left", pad=22)
    ax.tick_params(length=0)
    fig.subplots_adjust(bottom=0.30, top=0.86)
    wrapped = "\n".join(textwrap.fill(p, 130) for p in decl.split("\n"))
    fig.text(0.125, 0.115, wrapped, fontsize=8, va="top",
             color=PALETTE["ink_soft"])
    return fig, ax


# ------------------------------------------------------ areal re-aggregation
def areal_weights(src, dst, n=700):
    """W[d, s] = share of source unit s that lies inside destination unit d.
    Grid sampling in the equal-area plane (no GIS library); error < 0.1%."""
    lat_ts = _collection_lat_ts(src)

    def rings(fs):
        out = []
        for f in fs:
            x, y = _project_ring(list(f["ring"]), "equal_area", lat_ts)
            out.append(MplPath(np.column_stack([x, y])))
        return out
    ps, pd_ = rings(src), rings(dst)
    allv = np.vstack([p.vertices for p in ps])
    gx = np.linspace(allv[:, 0].min(), allv[:, 0].max(), n + 2)[1:-1]
    gy = np.linspace(allv[:, 1].min(), allv[:, 1].max(), n + 2)[1:-1]
    X, Y = np.meshgrid(gx, gy)
    pts = np.column_stack([X.ravel(), Y.ravel()])
    sid = np.full(len(pts), -1)
    did = np.full(len(pts), -1)
    for i, p in enumerate(ps):
        sid[p.contains_points(pts)] = i
    for i, p in enumerate(pd_):
        did[p.contains_points(pts)] = i
    W = np.zeros((len(dst), len(src)))
    for s in range(len(src)):
        m = sid == s
        for d in range(len(dst)):
            W[d, s] = (m & (did == d)).sum() / max(m.sum(), 1)
    return W


def radar_area(v):
    v = np.asarray(v, float)
    return 0.5 * math.sin(2 * math.pi / len(v)) * float(np.sum(v * np.roll(v, -1)))
