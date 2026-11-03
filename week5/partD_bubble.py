"""Part D1 - four-variable bubble chart.
x = gdp_pc (log), y = healthcare_access, AREA = pop_m, hue+shape = region."""
from w5common import *
from vizlib import lie_factor

style_defaults()
df = load_health()
fig, ax = plt.subplots(figsize=(9.6, 6.2))
s = bubble(ax, df)

# the three or four countries the title is about, labelled directly
picks = {  # name: (dx, dy) label offset in points
    "Aldonia": (-8, 26), "Wessant": (-95, -60),
    "Vornath": (-70, 30), "Tarrowin": (45, -42)}
for name, off in picks.items():
    r = df[df.country == name].iloc[0]
    ax.annotate(f"{name} ({r.pop_m:g} M)", (r.gdp_pc, r.healthcare_access),
                xytext=off, textcoords="offset points", fontsize=8,
                color=PALETTE["ink"], ha="center",
                arrowprops=dict(arrowstyle="-", color=PALETTE["ink_soft"], lw=0.7))

second = df.gdp_pc.nlargest(2).iloc[1]
ax.text(0.015, 0.035,
        f"Outlier decision: Aldonia (${df.gdp_pc.max():,}, {df.gdp_pc.max()/second:.1f}x the next "
        f"richest) is KEPT. The log axis\nabsorbs it, and it is the one rich micro-state (1.9 M people) in the data.",
        transform=ax.transAxes, fontsize=7.5, color=PALETTE["ink_soft"], va="bottom")
ax.set_title("Healthcare access climbs steadily with GDP per capita; population size\n"
             "tells you little about either", loc="left")

lf, *_ = lie_factor(df.pop_m.min(), df.pop_m.max(), s.min(), s.max(), ink_dimension=1)
note = (f"Source: health_indicators.csv ({SYN}); n={len(df)} countries, none excluded. "
        f"Area = {K_AREA:g} pt\u00b2 per million people (mark area exactly proportional to population; "
        f"radius goes as the square root). Size legend shows real populations.\n"
        f"Hue = region (6 Okabe-Ito hues; worst colour-blind pair is green/pink, \u0394E 7.5, so Dravira carries a dark outline as a second channel). "
        f"Extracted {DATE}.")
save_fig(fig, HERE / "partD_bubble.png", note)
print("saved partD_bubble.png; area ratio max/min =", round(s.max()/s.min()), "diameter ratio =", round((s.max()/s.min())**.5, 1))
