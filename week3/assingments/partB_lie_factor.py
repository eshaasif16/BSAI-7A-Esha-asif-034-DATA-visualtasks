
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = next(p for p in (HERE, os.path.dirname(HERE))
            if os.path.exists(os.path.join(p, "vizlib.py")))
sys.path.insert(0, ROOT)
from vizlib import lie_factor, lie_verdict   # noqa: E402

d = pd.read_csv(os.path.join(ROOT, "data", "case07_lie_factor.csv"))

rows = []
for _, r in d.iterrows():
    lf, de, ge = lie_factor(r.value_start, r.value_end, r.ink_start, r.ink_end,
                            ink_dimension=int(r.ink_dimension))
    # what you would have got by wrongly leaving ink_dimension at 1
    lf1, _, ge1 = lie_factor(r.value_start, r.value_end, r.ink_start, r.ink_end, 1)
    rows.append({"chart": r.chart_id, "subject": r.subject, "dim": int(r.ink_dimension),
                 "data effect": f"{de:+.1%}", "graphic effect": f"{ge:+.1%}",
                 "Lie Factor": round(lf, 2), "verdict": lie_verdict(lf),
                 "LF if dim left at 1": round(lf1, 2)})

table = pd.DataFrame(rows)
print("Q1 - the audit table\n")
print(table.to_string(index=False))

print("\nQ3 - graphics that need ink_dimension=2:",
      ", ".join(table[table.dim == 2].chart))
for _, c in table[table.dim == 2].iterrows():
    print(f"   {c['chart']}: LF is {c['Lie Factor']} with dim=2 but would read "
          f"{c['LF if dim left at 1']} with dim=1 - the area grew as the square "
          f"of the length")

# ---- Q5: chart F ------------------------------------------------------------
w = pd.read_csv(os.path.join(ROOT, "data", "case07_dual_axis_series.csv"))
w["profit_pkr_m"] = w.revenue_pkr_m - w.cost_pkr_m
print("\nQ5 - chart F, the underlying data (PKR millions, same unit)\n")
print(w.to_string(index=False))
print(f"\nLoss months: {(w.profit_pkr_m < 0).sum()} of {len(w)}. "
      f"Profit grows {w.profit_pkr_m.iloc[0]} -> {w.profit_pkr_m.iloc[-1]} PKR m.")
print(f"Revenue +{w.revenue_pkr_m.iloc[-1]/w.revenue_pkr_m.iloc[0]-1:.0%}, "
      f"cost +{w.cost_pkr_m.iloc[-1]/w.cost_pkr_m.iloc[0]-1:.0%} Jan->Jun.")
print("Lie Factor for F: NOT COMPUTABLE. The formula compares ink to data on ONE "
      "scale. A dual-axis chart has two\nscales, so 'ink' for each line depends on "
      "an arbitrary axis range chosen by the author; the crossing point moves "
      "when either axis moves.")
