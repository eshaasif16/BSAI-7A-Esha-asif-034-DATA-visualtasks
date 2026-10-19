
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next(p for p in (HERE, os.path.dirname(HERE))
            if os.path.exists(os.path.join(p, "vizlib.py")))
sys.path.insert(0, ROOT)
from vizlib import MARKERS, PALETTE, save_fig, style_defaults   # noqa: E402

style_defaults()
C = PALETTE["series"]
D = lambda f: pd.read_csv(os.path.join(ROOT, "data", f))   # noqa: E731

fig, ax = plt.subplots(3, 3, figsize=(15, 12.5))

# 1 - Simpson's paradox: rate per 1,000 trips, split by road type -----------------
h = D("case01_helmet_rickshaw.csv")
g = (h.groupby(["road_type", "helmet_grade"])[["head_injuries", "trips"]].sum()
       .assign(rate=lambda x: x.head_injuries / x.trips * 1000).reset_index())
sns.barplot(data=g, x="road_type", y="rate", hue="helmet_grade",
            order=["Inner-city lanes", "City arterial", "Motorway"],
            palette=[C[0], C[1]], ax=ax[0, 0])
ax[0, 0].set(title="1. On every road type Premium has FEWER head injuries",
             xlabel="", ylabel="Head injuries per 1,000 trips")

# 2 - per-student rates, not raw counts ------------------------------------------
q = D("case02_chai_quizzes.csv")
sns.scatterplot(x=q.cups_doodh_patti_sold / q.students_enrolled,
                y=q.quiz_failures / q.students_enrolled * 100, hue=q.is_exam_month,
                style=q.is_exam_month, markers=MARKERS[:2], palette=[C[0], C[1]],
                s=60, ax=ax[0, 1])
ax[0, 1].set(title="2. Per student, chai and failures barely relate (r = 0.29)",
             xlabel="Cups per enrolled student", ylabel="Quiz failures per 100 students")

# 3 - like-for-like stations ------------------------------------------------------
a = D("case03_aqi_monitors.csv").assign(date=lambda x: pd.to_datetime(x.date))
always = a.groupby("station_id").station_status.apply(lambda s: (s == "reporting").all())
a["group"] = np.where(a.station_id.isin(always[always].index),
                      "13 stations that reported all 4 months", "9 stations that went offline 2 Mar")
a["week"] = a.date.dt.to_period("W").dt.start_time
w = a.dropna(subset=["aqi"]).groupby(["week", "group"]).aqi.mean().reset_index()
sns.lineplot(data=w, x="week", y="aqi", hue="group", palette=[C[0], C[1]], ax=ax[0, 2])
ax[0, 2].set(title="3. Same 13 stations: AQI did not move (137.1 vs 137.2)",
             xlabel="", ylabel="Weekly mean AQI")
ax[0, 2].tick_params(axis="x", rotation=30)
ax[0, 2].legend(fontsize=7.5, loc="center left")

# 4 - the quartet, one small panel each (full version: sns.lmplot col_wrap=2) ---------
d4 = D("case04_quartet_depts.csv")
ax[1, 0].axis("off")
ax[1, 0].set_title("4. Same line, four stories: plot each department on its own",
                   fontsize=9.5)
pos = [(0.0, 0.5), (0.52, 0.5), (0.0, 0.0), (0.52, 0.0)]
for (name, gdf), (x0, y0), col in zip(d4.groupby("cohort_group"), pos, C + [PALETTE["muted"]]):
    ins = ax[1, 0].inset_axes([x0 + 0.1, y0 + 0.1, 0.38, 0.33])
    sns.regplot(data=gdf, x="study_hours_per_week", y="final_score_out_of_20", ci=None,
                color=col, scatter_kws={"s": 18}, line_kws={"lw": 1.5}, ax=ins)
    ins.set_title(f"{name}: {gdf.department.iloc[0]}", fontsize=7.5)
    ins.set_xlabel(""); ins.set_ylabel("")
    ins.tick_params(labelsize=6.5)

# 5 - five shapes ---------------------------------------------------------------------
s5 = D("case05_same_stats_shapes.csv")
for (name, gdf), mk in zip(s5.groupby("shape_name", sort=False), MARKERS + ["v"]):
    ax[1, 1].scatter(gdf.hours_on_platform, gdf.assessment_score, s=8, alpha=0.5,
                     marker=mk, label=name)
ax[1, 1].set(title="5. Same stats, five shapes (full redesign: sns.relplot col=shape)",
             xlabel="Hours on platform", ylabel="Assessment score")
ax[1, 1].legend(fontsize=7, markerscale=2)

# 6 - one participant -------------------------------------------------------------------
s6 = D("case06_sensor_matrix.csv")
sns.scatterplot(data=s6, x="hba1c", y="creatinine", hue="study_site", style="study_site",
                markers=MARKERS, palette=C + [PALETTE["muted"]], s=40, ax=ax[1, 2])
ax[1, 2].set(title="6. One participant (HbA1c 15.8, creatinine 1,050) makes r = 0.77",
             xlabel="HbA1c (%)", ylabel="Creatinine (umol/L)")
ax[1, 2].legend(fontsize=7)

# 7 - one axis, one unit -----------------------------------------------------------------
t = D("case07_dual_axis_series.csv")
lt = t.melt(id_vars="month", value_vars=["revenue_pkr_m", "cost_pkr_m"],
            var_name="measure", value_name="pkr_m")
sns.lineplot(data=lt, x="month", y="pkr_m", hue="measure", style="measure",
             markers=True, dashes=False, palette=[C[0], C[1]], ax=ax[2, 0])
ax[2, 0].fill_between(range(len(t)), t.cost_pkr_m, t.revenue_pkr_m, color=C[2], alpha=0.2)
ax[2, 0].set_ylim(0, 85)
ax[2, 0].set(title="7. One axis, one unit: profit every month, 8 -> 25 PKR m",
             xlabel="", ylabel="PKR millions")

# 8 - a declared bin width -----------------------------------------------------------------
v = D("vitals_10k.csv")
sns.histplot(v.systolic, binwidth=2, color=C[0], ax=ax[2, 1])
ax[2, 1].set(title="8. Declare ONE binwidth (2 mmHg): two humps, every time",
             xlabel="Systolic BP (mmHg)", ylabel="Patients per bin")

# 9 - integers with a ceiling -----------------------------------------------------------------
sns.histplot(v.spo2, discrete=True, stat="percent", color=C[0], ax=ax[2, 2])
ax[2, 2].set_xlim(80, 101)
ax[2, 2].axvline(100.5, color=C[1], lw=1.5)
ax[2, 2].set(title="9. SpO2 is whole numbers capped at 100: draw bars, not a KDE",
             xlabel="SpO2 (%)", ylabel="% of readings")

import textwrap
for p in ax.flat:
    p.set_title(textwrap.fill(p.get_title(), 44), fontsize=9.5, loc="left")
fig.suptitle("Part A - the nine redesigns", x=0.006, ha="left", fontsize=14,
             fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.97])
print("wrote", save_fig(fig, os.path.join(HERE, "partA_redesigns.png"),
                        "Synthetic data generated for CDB601220."))
