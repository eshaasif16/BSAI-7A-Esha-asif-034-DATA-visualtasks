"""
Week 6 - Task D1 (bonus): the generation chart from Task B, rebuilt in Plotly.

    python3 partD_interactive.py        # writes partD_interactive.html

Same data as partB_2.png (clean/generation_parts.csv, 144 part-rows, no Total
row). What a reader can do here that they cannot do on the PNG:
  - hover a bar to get the month's solar MWh, total MWh and solar share
  - click "Solar" or "All other sources" in the legend to hide a series
  - drag the range slider (or box-zoom) to look at any run of months
The page is self-contained, so it opens offline.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

HERE = Path(__file__).resolve().parent
src = HERE / "clean" / "generation_parts.csv"
if not src.exists():
    raise SystemExit("run partA_process.py first (clean/generation_parts.csv)")

g = pd.read_csv(src)
mx = g.pivot_table(index="month", columns="subsource", values="mwh", aggfunc="sum")
solar = mx["Solar"]
other = mx.drop(columns="Solar").sum(axis=1)
total = solar + other
share = solar / total * 100

ORANGE, GREY = "#D55E00", "#9AA7B4"       # same two colours as partB_2.png
x = pd.to_datetime(mx.index + "-01")
cd = list(zip(solar, other, total, share))

fig = go.Figure()
fig.add_bar(x=x, y=solar / 1e6, name="Solar", marker_color=ORANGE,
            customdata=cd,
            hovertemplate=("<b>%{x|%b %Y}</b><br>Solar: %{customdata[0]:,.0f} MWh"
                           "<br>Total generation: %{customdata[2]:,.0f} MWh"
                           "<br>Solar share: %{customdata[3]:.1f}%<extra></extra>"))
fig.add_bar(x=x, y=other / 1e6, name="All other sources (7 categories)",
            marker_color=GREY, opacity=0.6, customdata=cd,
            hovertemplate=("<b>%{x|%b %Y}</b><br>Everything else: %{customdata[1]:,.0f} MWh"
                           "<br>Total generation: %{customdata[2]:,.0f} MWh<extra></extra>"))
fig.update_layout(
    barmode="stack",
    title=dict(text="Solar's share rose from 4.1% to 7.9%: hover a month for the "
                    "numbers, drag the slider to change the window", x=0.01),
    yaxis=dict(title="Energy generated, TWh per month", rangemode="tozero"),
    xaxis=dict(rangeslider=dict(visible=True), title=None),
    legend=dict(orientation="h", y=1.08, x=0),
    template="simple_white", height=560,
    annotations=[dict(
        x=0, y=-0.32, xref="paper", yref="paper", showarrow=False, xanchor="left",
        font=dict(size=10, color="#5B6573"),
        text=("Source: generation_mix.csv, cleaned by partA_process.py (Total rows removed, "
              "144 part-rows). Apr 2025 - Sep 2026. Synthetic data, CDB601220 Week 6."))])
fig.write_html(HERE / "partD_interactive.html", include_plotlyjs=True)
print("wrote partD_interactive.html")
