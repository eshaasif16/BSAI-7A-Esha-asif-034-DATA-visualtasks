"""Builds partE_justification.pdf (one page). Re-run AFTER filling partC_reader_results.csv:
the counterfactual paragraph then quotes your real readers instead of the highlighted gap."""
import csv
from pathlib import Path
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

HERE = Path(__file__).resolve().parent
base = ParagraphStyle("b", fontName="Helvetica", fontSize=8.7, leading=11.0, spaceAfter=4.5)
h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=13, leading=15, spaceAfter=3)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=9.6, leading=11.5, spaceBefore=3, spaceAfter=2)
small = ParagraphStyle("s", parent=base, fontSize=7.6, leading=9.2, textColor=colors.HexColor("#5B6573"))

# --- readers: use the real file if it is filled in, otherwise leave a visible gap
rows = []
p = HERE / "partC_reader_results.csv"
if p.exists():
    rows = [r for r in csv.DictReader(open(p)) if r.get("reader_id", "").strip()]
if len(rows) >= 5:
    ov = [len({r["a1"].strip(), r["a2"].strip(), r["a3"].strip()} & {r["b1"].strip(), r["b2"].strip(), r["b3"].strip()}) for r in rows]
    reader = (f"In my Part C test, {len(rows)} readers each named the three worst counties on Map A (the count) and then on Map B (the rate); "
              f"on average {np.mean(ov):.1f} of their three picks stayed the same (overlap per reader: {', '.join(map(str, ov))}). "
              "The two maps share boundaries, classes and ramp, so the only thing that changed their answer was the denominator.")
else:
    reader = ('<font backColor="#FFF200">[FILL IN AFTER PART C: how many real readers you tested, how many of their three picks stayed the same between '
              'Map A and Map B on average, and the overlap per reader. Re-run build_partE.py once partC_reader_results.csv has at least five rows.]</font>')

S = []
S.append(Paragraph("Part E - Justification of the Part D figures", h1))
S.append(Paragraph("CDB601220 Week 5. Data: synthetic, generated for the course. Boundaries: districts.geojson (24 districts). Extracted 2 Nov 2026.", small))

S.append(Paragraph("1. The bubble chart: which channel carries which variable", h2))
S.append(Paragraph(
    "I ranked the variables by how precisely a reader has to compare them, and gave the most precise channel to the most precise job. The question the chart exists to answer is how healthcare access relates to wealth, "
    "so GDP per capita and access took the two position channels, the most accurate ones we have. GDP is on a log axis because it spans $283 to $120,219 and Aldonia is 9.2x the next country; "
    "I kept Aldonia and labelled it, because the log axis absorbs it and dropping it would delete the one rich micro-state. "
    "Population only needs a coarse reading (a giant, a mid-sized country, a speck), so it took area, with area exactly proportional to population (12 pt<super>2</super> per million). That is a diameter range of 24x, not the 589x that "
    "radius-by-population would give. The smallest dot is 0.95 mm and the largest 0.90 in, and the size legend is in real millions. Region is a category with no order, so it took hue, "
    "using six Okabe-Ito colours; under deuteranopia the worst pair (green and pink) has a delta E of 7.5, which needs a second channel, so Dravira carries a dark outline. "
    "I used circles only, because matplotlib gives different visible areas to different marker shapes and that would have broken the area encoding.", base))

S.append(Paragraph("2. The parallel coordinates plot: three decisions, declared", h2))
S.append(Paragraph(
    "<b>Scaling: percentile rank.</b> Min-max puts 58 of 60 countries below 0.10 on GDP; z-score pushes Aldonia to +7.5 sd and still leaves it in charge. Rank cannot be dominated by an outlier. "
    "The cost is that gap sizes disappear, so the real minimum and maximum are printed at each axis. "
    "<b>Axis order:</b> computed, not chosen by eye, with the greedy |r| chain: healthcare_access, cases_per_100k, urban_pct, median_age, gdp_pc. (On ranks the same rule gives a different chain, starting from gdp_pc; I report that rather than hide it.) "
    "<b>Brush:</b> Borealis, fixed in code as the region with the highest mean case rate (115.1 per 100,000). "
    "What it shows that a scatterplot matrix does not: the pairwise panels show access against cases (r = -0.80), cases against urban share (-0.62) and urban share against age (+0.64) separately, "
    "but only the lines show that one group is sitting low on access (mean percentile 0.41), high on cases (0.66) and low on urban share (0.31) all at once.", base))

S.append(Paragraph("3. The choropleth: denominator, classes, projection", h2))
S.append(Paragraph(
    "<b>Denominator:</b> cases per 100,000 residents, because cases is a count and r(cases, population) = 0.986 across districts whose populations differ 23-fold; a count map is a map of where people live. "
    "<b>Classes:</b> five Jenks natural breaks (30.4, 33.8, 47.5, 54.4, 64.8, 76.5). Goodness of variance fit is 0.969 for natural breaks, tied with equal interval at 0.969 and well above quantile at 0.908. "
    "I chose natural breaks because they put the class edges in the gaps in this data, and I printed the edges in the legend. "
    "<b>Projection:</b> Lambert cylindrical equal-area with its standard parallel at the mean latitude, because a choropleth encodes the value in the area it fills. "
    "Mercator would draw every district 1.24 to 1.49 times too large and the north about 21% larger than the south. "
    "<b>Suppression:</b> none needed; the smallest district has 186 cases, and no unit was merged or hidden. The join matched 24 of 24 polygons.", base))

S.append(Paragraph("4. The counterfactual: what a different choice would have said", h2))
S.append(Paragraph(
    "With the other defensible choice, a choropleth of the raw count, the darkest districts would have been D17 Qilabad, D13 Mehrabad and D09 Ilyaspur, and the story would have been 'the outbreak is in the big districts'. "
    "D17 and D09 are actually below the national rate of 52.8 per 100,000. The three districts that really lead, D19, D20 and D21 in the north-west, run at 76.5, 74.2 and 68.8, which is 45%, 40% and 30% above the national rate, "
    "and they hold about 4.2 million people who would have been shown as a quiet corner of the map. That is the cost of the wrong choice: attention and resources sent to where the people are, away from where the risk is. "
    + reader, base))
S.append(Spacer(1, 2))
S.append(Paragraph("Scripts: partD_bubble.py, partD_pcp.py, partD_choropleth.py (all 300 dpi, source line stamped with save_fig). Every figure number above is printed by partB_decisions.py or partA_charts.py.", small))

SimpleDocTemplate(str(HERE / "partE_justification.pdf"), pagesize=A4, leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                  topMargin=0.55 * inch, bottomMargin=0.5 * inch, title="Week 5 Part E").build(S)
print("wrote partE_justification.pdf", "(readers:", len(rows), ")")
