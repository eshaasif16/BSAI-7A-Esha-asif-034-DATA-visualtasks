"""Builds partA_diagnosis.pdf: one page per case, both figures, four marks' worth of text.
Run partA_charts.py (and partD_bubble.py) first. Every number below is printed by
partA_charts.py into partA_numbers.txt - check them there before you submit."""
from pathlib import Path
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage, KeepTogether

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figs"
W = A4[0] - 1.1 * inch

base = ParagraphStyle("b", fontName="Helvetica", fontSize=8.6, leading=10.8, spaceAfter=3.2)
h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=13, leading=15, spaceAfter=2)
claim = ParagraphStyle("c", fontName="Helvetica-Oblique", fontSize=9, leading=11, textColor=colors.HexColor("#5B6573"), spaceAfter=4)
cap = ParagraphStyle("cap", fontName="Helvetica-Bold", fontSize=7.8, leading=9, textColor=colors.HexColor("#16202E"), spaceBefore=2, spaceAfter=1)
big = ParagraphStyle("big", parent=base, fontSize=9.4, leading=12.4, spaceAfter=5)


def fig(path, maxh=2.62 * inch):
    w, h = Image.open(path).size
    scale = min(W / w, maxh / h)
    im = RLImage(str(path), width=w * scale, height=h * scale)
    im.hAlign = "LEFT"
    return im


def P(head, txt):
    return Paragraph(f"<b>{head}</b> {txt}", base)


CASES = [
    dict(n=1, title="Size by pop_m squared: the biggest countries hide the rest",
         claim='"Population and healthcare access are unrelated: the large countries are spread right across the range."',
         conc="The chart invites you to say that how big a country is tells you nothing about its healthcare access. My first objection was that the claim might just be wrong and I was dressing up an ugly chart. "
              "I checked: Spearman between population and access is 0.22 (p = 0.09), and the six most populous countries run from 32.8 to 79.3 on access. So a weak-to-no relationship is roughly what the data says. "
              "The conclusion survives. What does not survive is the idea that this chart shows it.",
         mech="The size channel. s = pop_m**2 puts population squared into the marker area, so the diameter ends up proportional to population itself. Wessant (353 M) is drawn 353 pt, "
              "about 4.9 inches, across. The biggest mark has 346,921 times the area of the smallest (589 times the diameter, which is the '589x' in the brief). The three biggest countries own 87% of all the ink; "
              "9 countries are under 2 pt across and 3 are under 1 pt. A reader who sees a handful of enormous circles scattered across the range has seen six countries, not sixty.",
         fix="Same data, but area proportional to population (12 pt<super>2</super> per million, so the diameter ratio is a sensible 24x), hue for region, a size legend in real millions, and four countries labelled by name. "
             "The same picture shows what the published one buried: access is tied to GDP per capita (Spearman 0.89), and population hardly matters."),
    dict(n=2, title="Colouring a count: the map of where people live",
         claim='"The outbreak is concentrated in the three districts around the capital."',
         conc="The map invites you to read D17, D13 and D09 as a hot cluster. My first objection was that they might really be a cluster, and really be hot. Neither holds. They are 435 to 578 km apart (D17-D13 578, D17-D09 437, D13-D09 435), "
              "so there is no cluster to speak of, and the file has no capital to be around. On rate, D17 (51.0) and D09 (49.9) are both below the national 52.8, ranked 13th and 14th of 24. Only D13 (64.0, 5th) is genuinely high.",
         mech="The denominator. cases is a count, population ranges 23-fold, and r(cases, population) = 0.986. A choropleth of that count is a map of where people live. Divide by population and the top three become D19 (76.5 per 100,000), "
              "D20 (74.2) and D21 (68.8), all in the north-west. The overlap with the count top three is zero.",
         fix="Left: cases against population with a line at the national rate. The three count leaders sit on or near the line, which means average, while D19 to D21 sit well above it. "
             "Right: the same districts coloured by cases per 100,000 residents, five natural breaks, equal-area projection."),
    dict(n=3, title="Min-max scaling: one rich country flattens the whole axis",
         claim='"GDP per capita barely varies across the sample."',
         conc="The flat orange-and-grey band along the bottom says every country has about the same GDP per capita. The obvious objection is that maybe it really is flat. It is not: GDP per capita runs from $283 to $120,219, a 425-fold range. "
              "I also asked whether it is all Aldonia. Without Aldonia the other 59 countries still span 46x (interquartile range $1,514 to $4,770). The spread is real.",
         mech="The scaling method. Min-max sets 0 and 1 from the two extreme values, and the top one, Aldonia ($120,219), is 9.2x the second richest (Brightmoor, $13,009). "
              "After scaling, 58 of 60 countries sit below 0.10 and the median is 0.017. The axis is flat because one country stretched the scale, not because the countries are alike.",
         fix="The same parallel coordinates plot with the same axis order, and only the scaling changed to percentile rank. The median becomes 0.51 and the axis fills out. "
             "This is a decision fix, not a chart-type fix. The price: rank throws away the size of the gaps (Aldonia is just 'rank 60'), so I print the real min and max on every axis. Log10 then min-max would be the alternative."),
    dict(n=4, title="File order: the strongest pair is three axes apart",
         claim='"Healthcare access and case rate are unrelated: there is no crossing pattern between them."',
         conc="The plot invites you to conclude there is nothing between access and case rate. The objection is that maybe there really is nothing. There is the opposite: r = -0.799 (Spearman -0.810), the strongest correlation among the five columns.",
         mech="The axis order. In file order the axes are gdp_pc, healthcare_access, urban_pct, median_age, cases_per_100k, so access is axis 2 and cases is axis 5, three apart. "
              "A parallel coordinates plot only shows a relationship between neighbouring axes, and the lines get scrambled passing through urban_pct and median_age. The pairs the reader can actually see are gdp/access (r 0.37), access/urban (0.75), urban/age (0.64) and age/cases (-0.59).",
         fix="Same scaling, same highlighted countries, only the order changed to the greedy |r| chain, computed in code before looking: healthcare_access, cases_per_100k, urban_pct, median_age, gdp_pc. "
             "The access/cases pair is now adjacent and the X-shaped crossing appears. Like case 3, this stays a parallel coordinates plot, so the fix is a decision, not a new chart type."),
    dict(n=5, title="Quantile classes: a five-level gradient built out of nothing",
         claim='"There is a clear five-level gradient in incidence across the federation."',
         conc="Five distinct blues invite you to read five levels of risk. My first objection was that the districts might differ a little and the map is just showing it. "
              "The rates run 31.07 to 33.40 per 100,000, a spread of 7.2% of the mean. At these case counts, pure chance would give a coefficient of variation near 7.1%; the observed one is 2.2%, so the districts vary less than chance alone predicts. "
              "On a funnel plot 0 of 24 fall outside the limits (largest |z| 0.58). There is nothing to grade.",
         mech="The classification scheme. Quantile breaks force four or five districts into every class, whatever the spread. The edges are 31.07, 31.49, 32.07, 32.51, 32.94, 33.40, so the narrowest class is 0.41 per 100,000 wide, 1.3% of the rate. "
              "A full light-to-dark ramp is spent on differences smaller than a rounding error. The join (24 of 24) and the arithmetic are fine; the lie is in the breaks.",
         fix="Left: the same map using the class edges of the other outbreak (case 2), so the two are on one scale. All 24 districts fall in the lightest class, which is the honest picture of a flat outbreak. "
             "Right: a funnel plot with its axis from zero, nothing outside the limits. A mostly one-colour map is the finding, not a failure of the map."),
    dict(n=6, title="Ranking small-area rates: sorting by noise",
         claim='"Unit U32 is a hotspot, running at nearly five times the national rate."',
         conc="The ranked bars invite you to send resources to U32 (40.9 per 100,000 against a pooled 8.72, which is 4.7x). My first objection was the opposite of the usual one: maybe U32 really is a hotspot and I am being too sceptical. "
              "The funnel does put it outside the 95% limits, the only one of 40, and the exact Poisson chance of 9 or more cases when 1.92 are expected is 0.00018 (about 0.007 allowing for 40 units). "
              "In real data I would flag it for follow-up. Here the data dictionary says every unit shares one true rate, so it is a rare tail draw.",
         mech="Small denominators. U32 is 9 cases in 22,000 people. Its exact 95% interval is 18.7 to 77.7 per 100,000, and one case more or less moves the rate by 4.5. Units under 30,000 people range from 0.0 to 40.9, "
              "while the 10 units over 100,000 sit between 5.5 and 12.0. Ranking rates puts the noisiest units at both ends: 8 of the 10 units furthest from the national rate have under 50,000 people.",
         fix="A funnel plot: rate against population with 95% Poisson limits that widen as population falls. The wild values live where the funnel is wide, the large units hug the pooled rate, and U32 is shown with its interval, not as a bare 40.9. "
             "If this were a map I would also need a suppression or merge rule for units this small."),
    dict(n=7, title="Correlation across 24 districts: the answer depends on the zoning",
         claim='"District income and case rate are only weakly related: r is about -0.31."',
         conc="The scatter invites the conclusion that income barely matters for case rate. The objections I tried first were a single outlier district and urban density as a confounder. "
              "Leaving out each district in turn gives r between -0.39 and -0.19, so no one district drives it. Density is related to neither income (r = -0.08) nor rate (r = 0.001). Neither decoy explains the weak r.",
         mech="The boundaries (the modifiable areal unit problem). Pool the same people and cases into the six coarse zones, income as the population-weighted mean, and r becomes -0.75. "
              "Nothing in the data changed, only the unit. (Using a plain mean of district incomes makes it -0.89, another modelling choice.) Re-cutting into the 24 alternative units gives -0.29, so here scale matters far more than zoning, though that alternative uses areal interpolation, which assumes cases and income are spread evenly inside a district. "
              "Weighting the 24 districts by population gives -0.37. Whichever, none of these numbers is about individuals.",
         fix="Three panels with the same axes: the published 24 districts (r -0.31), the 24 alternative units (-0.29) and the 6 zones (-0.75). The honest statement is that the strength of the relationship depends on the unit, "
             "so r should never be quoted without saying which units it was computed on."),
    dict(n=8, title="Rural outbreak: colour measures land, not people",
         claim='"This is a rural outbreak: look how much of the map is dark."',
         conc="The map invites you to read a lot of dark, sparsely populated land as a rural outbreak. My first objection was that the dark districts might in fact be the sparse ones. Only barely: the nine districts in the top two classes average 48 people per km<super>2</super> against 60 for the rest, "
              "rate against density has r = 0.001 (Spearman 0.13), D13 is dark at 204 per km<super>2</super>, and D04, the sparsest district (5.8 per km<super>2</super>), is in the lightest class. There is no urban-rural gradient to find.",
         mech="Area is the encoding channel for a quantity that belongs to people. The five most populous districts are 12.6% of the land and 59.9% of the population. Class 3 holds 25.3% of the land but 49.5% of the people. "
              "The top two classes cover 31.2% of the map and 26.5% of residents. That gap is modest, which is the honest bit; the real trouble is that 'rural' is a reading the map cannot support, and the dark area reads as people when it is mostly land.",
         fix="The map beside a sorted bar chart of the rate (bars from zero, one bar per district) and a pair of bars per class showing share of land against share of people. The bars give every district the same weight, and the class chart shows where the map's ink and the people disagree."),
    dict(n=9, title="Radar chart: the enclosed area depends on the order of the axes",
         claim='"Region A is the stronger of the two: its profile encloses visibly more area."',
         conc="The overlaid polygons invite you to say A beats B. The objection is that maybe A really is better overall. The means are 62.3 and 62.0, a difference of 0.33 on a 0-100 scale; the sums are 374 and 372; "
              "and indicator by indicator it is 3 each. A wins funding (+35.5), equipment (+15.3) and access (+3.4); B wins coverage (-42.7), training (-8.9) and staffing (-0.6).",
         mech="Angle and area, and the axis order. A radar polygon's area is half of sin(60 degrees) times the sum of products of neighbouring values, so it depends on which indicators sit next to each other. In file order A encloses 9,933 and B 9,433. "
              "Over all 60 distinct orders of the six axes A wins 39 and B wins 21, and the difference runs from -1,131 to +1,659. A quantity that changes sign when you reorder the labels is not measuring strength.",
         fix="Left, a dumbbell chart: all six indicators on one 0-100 axis, sorted by difference, so the trade-off (A strong on funding, B on coverage) is visible and nothing hides in an area. "
             "Right, the histogram of area(A) minus area(B) across the 60 orders, with the file-order value marked."),
]

front = [
    Paragraph("Part A - nine diagnoses", h1),
    Paragraph("CDB601220 Week 5. All data is synthetic, generated for this course. For each case: the rebuilt chart, the redesign, then the conclusion and the decoy, the mechanism, and the fix. "
              "Every figure is produced by partA_charts.py and every number quoted is printed in partA_numbers.txt.", big),
    Paragraph("<b>Where my numbers differ from the brief</b>", base),
    Paragraph("<b>Case 1.</b> The brief says the largest mark is drawn 589x the area of the smallest. With s = pop_m**2 I get 346,921x in area; 589x is the ratio of the diameters. "
              "For the 9 countries under 2.0 M, I find s under 4 pt<super>2</super>, which is a dot under 2 pt across (3 of them are under 1 pt across), so I read 'smaller than a single point' loosely.", base),
    Paragraph("<b>Part C.</b> The brief says Elmsworth and Hollowfield go from the bottom of the count map to the top of the rate map. I get count ranks 13th and 16th of 20 (classes 2 and 1 of 5) and rate ranks 3rd and 1st, which matches in spirit but not literally 'bottom'.", base),
    Paragraph("<b>Toolkit.</b> geolib.corr_chain() crashes on pandas 3.0 (it writes into a read-only array); I use a copy-based version of the same rule in w5common.py and get the chain the brief expects. "
              "geolib's docstring also says Mercator inflates area by sec(latitude); measured directly it is sec<super>2</super>, and Part B reports the measured number.", base),
    Spacer(1, 4),
    Paragraph("<b>Which two are not fixed by changing the chart type</b>", base),
    Paragraph("Cases 3 and 4. Both stay parallel coordinates plots; the redesign is the same chart with a different decision inside it (the scaling in case 3, the axis order in case 4). "
              "Case 5 is a near third: it stays a choropleth, but the fix is to stop classifying noise and use a shared scale.", base),
]

story = list(front)
for c in CASES:
    story.append(PageBreak())
    story.append(Paragraph(f"Case {c['n']}  |  {c['title']}", h1))
    story.append(Paragraph(c["claim"], claim))
    story.append(Paragraph("1. Rebuilt from the recipe (reproduces the published claim)", cap))
    story.append(fig(FIGS / f"case{c['n']}_published.png"))
    story.append(Paragraph("2. The redesign", cap))
    story.append(fig(FIGS / f"case{c['n']}_redesign.png"))
    story.append(Spacer(1, 3))
    story.append(P("The conclusion and the decoy.", c["conc"]))
    story.append(P("The mechanism.", c["mech"]))
    story.append(P("The redesign.", c["fix"]))

doc = SimpleDocTemplate(str(HERE / "partA_diagnosis.pdf"), pagesize=A4, leftMargin=0.55 * inch, rightMargin=0.55 * inch,
                        topMargin=0.5 * inch, bottomMargin=0.45 * inch, title="Week 5 Part A diagnosis")
doc.build(story)
print("wrote partA_diagnosis.pdf")
