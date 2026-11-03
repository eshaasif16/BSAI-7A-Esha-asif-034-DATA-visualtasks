"""Part D2 - parallel coordinates: scaling, axis order, brushing, all declared."""
from w5common import *

style_defaults()
df = load_health()
COLS = PCP_COLS

# 1. axis order: computed by the greedy |r| rule, BEFORE looking at the plot
order = safe_corr_chain(df, COLS)
spear = safe_corr_chain(df.rank(numeric_only=True), COLS)
print("greedy order (Pearson |r|):", " -> ".join(order))
print("greedy order on ranks     :", " -> ".join(spear))
print("r(healthcare_access, cases_per_100k) = %.3f" % df.healthcare_access.corr(df.cases_per_100k))

# 3. brushed group: rule fixed in code = the region with the highest mean case rate
reg_mean = df.groupby("region").cases_per_100k.mean().sort_values(ascending=False)
brush = reg_mean.index[0]
print("brushed region (highest mean cases_per_100k): %s (%.1f)" % (brush, reg_mean.iloc[0]))
print(df[df.region == brush][["country", "gdp_pc", "healthcare_access", "cases_per_100k"]].to_string(index=False))

# 2. scaling: percentile rank. min-max leaves 58/60 below 0.10 on gdp_pc.
decl = ("Scaling: percentile RANK on every axis (min-max would flatten gdp_pc: 58 of 60 countries below 0.10). "
        "Real min and max printed at each axis foot and head.\n"
        "Axis order: greedy |r| chain computed in code (geolib.corr_chain rule), not chosen by eye. "
        f"Grey = all {len(df)} countries; orange = {brush}, the region with the highest mean case rate.")
fig, ax = pcp_figure(df, order, "rank", (df.region == brush).to_numpy(), decl,
                     "Where access is high, case rates are low: the lines cross in a tight X\n"
                     "between healthcare_access and cases_per_100k (r = \u22120.80)")
save_fig(fig, HERE / "partD_pcp.png",
         f"Source: health_indicators.csv ({SYN}); n={len(df)}, none excluded. Extracted {DATE}.")
print("saved partD_pcp.png")
