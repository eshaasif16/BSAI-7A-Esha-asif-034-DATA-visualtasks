"""
Part A - the numbers behind every diagnosis. Run it; every figure quoted in
partA_diagnosis.pdf is printed here.   python3 partA_evidence.py
All data is synthetic (CDB601220).
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import signal, stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next(p for p in (HERE, os.path.dirname(HERE))
            if os.path.exists(os.path.join(p, "vizlib.py")))
D = lambda f: pd.read_csv(os.path.join(ROOT, "data", f))   # noqa: E731


def head(t):
    print("\n" + "=" * 8, t)


# ---------------------------------------------------------------- 1 helmets
head("1  helmets - Simpson's paradox")
h = D("case01_helmet_rickshaw.csv")
g = h.groupby("helmet_grade")[["head_injuries", "trips"]].sum()
print((g.head_injuries / g.trips * 1000).round(2).to_dict(), "per 1,000 trips overall")
r = h.groupby(["road_type", "helmet_grade"])[["head_injuries", "trips"]].sum()
print((r.head_injuries / r.trips * 1000).round(2).unstack())
print("share of riders on the Motorway:",
      h.groupby("helmet_grade").road_type.apply(lambda s: (s == "Motorway").mean()).round(3).to_dict())
print("mean experience (months):", h.groupby("helmet_grade").months_experience.mean().round(1).to_dict())
print("mean speed (kph):", h.groupby("helmet_grade").avg_speed_kph.mean().round(1).to_dict())

# ---------------------------------------------------------------- 2 chai
head("2  chai - shared growth in head-count")
q = D("case02_chai_quizzes.csv")
print("r(cups, failures) =", round(q.cups_doodh_patti_sold.corr(q.quiz_failures), 3),
      "  (the brief quotes 0.93; check what your chart's label says)")
print("r(enrolled, cups) =", round(q.students_enrolled.corr(q.cups_doodh_patti_sold), 3),
      " r(enrolled, failures) =", round(q.students_enrolled.corr(q.quiz_failures), 3))
cp, fp = q.cups_doodh_patti_sold / q.students_enrolled, q.quiz_failures / q.students_enrolled
print("per-student r =", round(cp.corr(fp), 3))
print("exam-month decoy: r(is_exam, cups) =", round(q.is_exam_month.corr(q.cups_doodh_patti_sold), 3),
      "| within exam months r =", round(q[q.is_exam_month == 1].cups_doodh_patti_sold.corr(
          q[q.is_exam_month == 1].quiz_failures), 3),
      "| within non-exam r =", round(q[q.is_exam_month == 0].cups_doodh_patti_sold.corr(
          q[q.is_exam_month == 0].quiz_failures), 3))

# ---------------------------------------------------------------- 3 AQI
head("3  AQI - the stations that vanished")
a = D("case03_aqi_monitors.csv")
a["date"] = pd.to_datetime(a.date)
off = a[a.station_status == "offline"]
cut = off.date.min()
post = a.date >= cut
print("first offline day:", cut.date(), "| stations offline:", off.station_id.nunique(),
      "zones:", off.zone.value_counts().to_dict() if False else sorted(off.zone.unique()))
print("headline mean before/after:", round(a[~post].aqi.mean(), 1), "->", round(a[post].aqi.mean(), 1),
      f"({a[post].aqi.mean()/a[~post].aqi.mean()-1:+.1%})")
keep = a.groupby("station_id").station_status.apply(lambda s: (s == "reporting").all())
k = a[a.station_id.isin(keep[keep].index)]
print("same 13 stations before/after:", round(k[~k.date.ge(cut)].aqi.mean(), 2), "->",
      round(k[k.date.ge(cut)].aqi.mean(), 2))
print("mean AQI of the 9 dropped stations BEFORE they vanished:",
      round(a[~post & a.station_id.isin(off.station_id.unique())].aqi.mean(), 1))
print("reporting rows:", int((a.station_status == 'reporting').sum()), "of", len(a))

# ---------------------------------------------------------------- 4 quartet
head("4  four departments - Anscombe")
d4 = D("case04_quartet_depts.csv")
for k, g in d4.groupby("cohort_group"):
    x, y = g.study_hours_per_week.values, g.final_score_out_of_20.values
    sl = stats.linregress(x, y)
    print(k, g.department.iloc[0], "n", len(g), "mean", round(x.mean(), 2), round(y.mean(), 2),
          "r", round(sl.rvalue, 3), "slope", round(sl.slope, 3))
x, y = d4[d4.cohort_group == "II"].study_hours_per_week.values, d4[d4.cohort_group == "II"].final_score_out_of_20.values
p = np.polyfit(x, y, 2)
print("II: linear R2", round(np.corrcoef(x, y)[0, 1] ** 2, 3), "quadratic R2",
      round(1 - (y - np.polyval(p, x)).var() / y.var(), 4), "peak at", round(-p[1] / (2 * p[0]), 1), "h")
g = d4[d4.cohort_group == "III"]; m = g.final_score_out_of_20.idxmax(); g2 = g.drop(m)
print("III: r without the 19.74 point =", round(g2.study_hours_per_week.corr(g2.final_score_out_of_20), 4))
g = d4[d4.cohort_group == "IV"]; g2 = g[g.study_hours_per_week < 30]
print("IV: SD of hours without the 38h student =", g2.study_hours_per_week.std())

# ---------------------------------------------------------------- 5 shapes
head("5  five cohorts, one set of statistics")
s5 = D("case05_same_stats_shapes.csv")
for k, g in s5.groupby("shape_name", sort=False):
    x, y = g.hours_on_platform, g.assessment_score
    zx, zy = (x - x.mean()) / x.std(ddof=0), (y - y.mean()) / y.std(ddof=0)
    rad = np.hypot(zx, zy)
    print(f"{k:14s} n {len(g)} mean {x.mean():.2f}/{y.mean():.2f} sd {x.std(ddof=0):.2f}/"
          f"{y.std(ddof=0):.2f} r {x.corr(y):.3f} | spearman {stats.spearmanr(x, y)[0]:.2f} | "
          f"radius sd {rad.std():.2f}")
g = s5[s5.shape_name == "two clusters"]
zx = (g.hours_on_platform - g.hours_on_platform.mean()); lab = zx > zx.median()
print("two clusters, within-cluster r:",
      round(g[lab].hours_on_platform.corr(g[lab].assessment_score), 2),
      round(g[~lab].hours_on_platform.corr(g[~lab].assessment_score), 2))

# ---------------------------------------------------------------- 6 heatmap
head("6  heatmap - one participant")
s6 = D("case06_sensor_matrix.csv")
r_all = s6.hba1c.corr(s6.creatinine)
pv = stats.pearsonr(s6.hba1c, s6.creatinine)[1]
print("r =", round(r_all, 3), "p =", f"{pv:.1e}", "| 190 pairs, Bonferroni threshold =", f"{0.05/190:.1e}")
i = s6.creatinine.idxmax()
print("extreme row:", s6.loc[i, ["study_site", "age_years", "hba1c", "creatinine"]].to_dict())
r1 = s6.drop(i)
print("r without that ONE row =", round(r1.hba1c.corr(r1.creatinine), 3),
      "| spearman with it =", round(stats.spearmanr(s6.hba1c, s6.creatinine)[0], 3))
print("r by site:", {k: round(g.hba1c.corr(g.creatinine), 2) for k, g in s6.groupby("study_site")})
print("median creatinine by site:", s6.groupby("study_site").creatinine.median().round(1).to_dict())
print("age decoy - partial r controlling for age:",
      round(np.corrcoef(*[(v - np.polyval(np.polyfit(s6.age_years, v, 1), s6.age_years)) for v in (s6.hba1c, s6.creatinine)])[0, 1], 3))
print("bonus: resting_hr vs vo2max pooled r =", round(s6.resting_hr.corr(s6.vo2max), 2),
      "| within device:", {k: round(g.resting_hr.corr(g.vo2max), 2) for k, g in s6.groupby("hr_device_model")})
print("device model = site:", (s6.groupby("hr_device_model").study_site.nunique() == 1).all())

# ---------------------------------------------------------------- 7 dual axis
head("7F  dual axis")
w = D("case07_dual_axis_series.csv"); w["profit"] = w.revenue_pkr_m - w.cost_pkr_m
print(w.to_string(index=False)); print("loss months:", int((w.profit < 0).sum()))

# ---------------------------------------------------------------- 8 bins
head("8  bin width - systolic BP")
v = D("vitals_10k.csv"); s = v.systolic
for n in (3, 5, 10, 20, 40, 100):
    hh, _ = np.histogram(s, bins=n)
    pk = signal.find_peaks(np.r_[0, hh, 0], prominence=0.05 * hh.max())[0]
    print(f"{n:>3d} bins (width {(s.max()-s.min())/n:5.1f} mmHg): {len(pk)} peak(s)")
for bw in (1, 2, 5, 10):
    hh, _ = np.histogram(s, bins=np.arange(s.min(), s.max() + bw, bw))
    pk = signal.find_peaks(np.r_[0, hh, 0], prominence=0.05 * hh.max())[0]
    print(f"width {bw:>2d} mmHg: {len(pk)} peak(s)")
print("n =", len(s), "| share >= 141:", round((s >= 141).mean(), 3))

# ---------------------------------------------------------------- 9 KDE
head("9  KDE above a physical limit - SpO2")
x = v.spo2.values.astype(float); kd = stats.gaussian_kde(x)
for adj in (1, 2, 2.6):
    kk = stats.gaussian_kde(x, bw_method=kd.factor * adj)
    print(f"bw_adjust {adj}: bandwidth {kk.factor*x.std(ddof=1):.2f} pts, "
          f"density above 100% = {kk.integrate_box_1d(100, np.inf):.1%}")
print("integers only:", np.all(x == x.round()), "| readings at exactly 100:", int((x == 100).sum()),
      f"({(x==100).mean():.1%}) | max =", x.max())
