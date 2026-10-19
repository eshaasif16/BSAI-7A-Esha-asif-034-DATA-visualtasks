"""Builds partE_justification.pdf (ONE page) from partD_numbers.json. Run partD_figure.py first."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import w4common as w

HERE = Path(__file__).resolve().parent
N = json.loads((HERE / "partD_numbers.json").read_text())
L, C = N["sessions_log"], N["catalogue_log"]


def _find_dejavu():
    """Locate DejaVu Sans (regular, bold, oblique) on Windows, macOS or Linux.

    matplotlib - already required by this project - ships these exact fonts inside its own package, so that
    is tried first and works the same everywhere. System folders are only a fallback."""
    import os
    import matplotlib
    names = ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf")
    folders = [os.path.join(matplotlib.get_data_path(), "fonts", "ttf"),
               "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu",
               "/Library/Fonts", os.path.expanduser("~/Library/Fonts"),
               os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")]
    for folder in folders:
        paths = [os.path.join(folder, n) for n in names]
        if all(os.path.isfile(p) for p in paths):
            return paths
    # last resort on a Windows machine without DejaVu: Arial has the same three styles
    win = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    arial = [os.path.join(win, n) for n in ("arial.ttf", "arialbd.ttf", "ariali.ttf")]
    if all(os.path.isfile(p) for p in arial):
        return arial
    raise FileNotFoundError("No usable TrueType font found. Run: pip install matplotlib")


_REG, _BOLD, _ITAL = _find_dejavu()
pdfmetrics.registerFont(TTFont("DV", _REG))
pdfmetrics.registerFont(TTFont("DV-B", _BOLD))
pdfmetrics.registerFont(TTFont("DV-I", _ITAL))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")
INK, SOFT, BLUE = colors.HexColor("#16202E"), colors.HexColor("#5B6573"), colors.HexColor("#0072B2")

# what the Wearables share would have been if the duplicate SKU had been left in
raw = pd.read_csv(w.DATA / "revenue_catalogue.csv")
rp = raw[raw.net_revenue_pkr_m > 0].groupby("subcategory").net_revenue_pkr_m.sum()
share_with_dup = rp["Wearables"] / rp.sum() * 100
cl = w.clean_catalogue()["pos"].groupby("subcategory").net_revenue_pkr_m.sum()
share_clean = cl["Wearables"] / cl.sum() * 100


def build(fs):
    body = ParagraphStyle("b", fontName="DV", fontSize=fs, leading=fs * 1.32, textColor=INK)
    h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=12.5, leading=15, textColor=INK, spaceAfter=1)
    h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=fs + 0.8, leading=fs * 1.4, textColor=BLUE, spaceBefore=3.5, spaceAfter=0.5)
    small = ParagraphStyle("s", fontName="DV", fontSize=fs - 0.8, leading=(fs - 0.8) * 1.3, textColor=SOFT)
    cell = ParagraphStyle("c", fontName="DV", fontSize=fs - 0.6, leading=(fs - 0.6) * 1.28, textColor=INK)
    cellb = ParagraphStyle("cb", parent=cell, fontName="DV-B")
    P = lambda t, s=body: Paragraph(t, s)
    E = escape

    story = [P("Part E - written justification", h1),
             P("Esha Asif - Roll 034 - BSAI 7A - CDB601220 Week 4. Synthetic course data throughout; nothing here is a finding about a real business.", small)]

    story.append(P("1. The four panels: the question, the chart, the channel rule", h2))
    story.append(P(
        "<b>Panel 1 (daily sessions, line):</b> where is traffic heading once the weekend rhythm is out? A line puts value on "
        "<i>position along a common scale</i>, the top of the Week 2 channel ranking (position &gt; length &gt; angle &gt; area); the raw "
        "series sits in grey as context and the 7-day mean is the single pop-out. "
        "<b>Panel 2 (day x hour heatmap):</b> when in the week do people visit? Colour lightness (one hue, sequential, no midpoint) is a weaker "
        "channel, so it is used for a pattern to be seen as a region, with the colour bar carrying the scale. "
        "<b>Panel 3 (treemap):</b> where is the mass of revenue? Area is the fourth-best channel (about +/-20%), so every block that fits carries its value, "
        "and hue marks the parent. <b>Panel 4 (sorted bars):</b> by how much? Length on a shared baseline is read far more accurately than area; "
        "values are printed. Panels 3 and 4 are the same eight numbers: the treemap shows where the mass is, the bars show by how much."))

    story.append(P("2. Every time decision, named and defended", h2))
    story.append(P(
        f"<b>Parse.</b> The file mixes two formats: {L['n_iso']:,} ISO rows and {L['n_slash']:,} dd/mm/yyyy rows. The slash rows are day-first, "
        f"and I proved it rather than assumed it: {L['slash_first_gt12']:,} of them have a first field above 12 and {L['slash_second_gt12']} have a second field above 12. "
        f"Each format is parsed with its own explicit format string. <i>format='mixed'</i> would also parse every row without an error, but it moves "
        f"{L['n_rows_moved_by_mixed']:,} rows to the wrong day and stretches the series to {L['mixed_min']} - {L['mixed_max']} instead of the true "
        f"{L['right_min']} - {L['right_max']}. "
        f"<b>Aggregation.</b> Sessions are a flow, so the hourly rows are summed to days (sum, never last). The 13 unrecorded days are counted on the "
        f"<i>hourly</i> index before resampling ({L['n_hours_missing']} hours, all 24 of each day), left as NaN and the line breaks there; nothing is interpolated in the figure. "
        f"<b>Window.</b> 7 days, centred: the cycle being cancelled is weekly, and a window one cycle long holds every weekday once (Part B.1: it removes 31.8% of the raw "
        f"variation, a 91-day window only 39.1%). Centred, because this is a retrospective Monday review; the first and last 3 days have no smoothed value, "
        f"and a live version would need the trailing mean and its 3-day lag. <b>Partial month.</b> {L['tail_month']} holds {L['tail_days']} of {L['tail_month_days']} days; it is kept "
        f"and marked on panel 1. The year-on-year figure in the title compares Apr-Aug only, the months complete in both years."))
    story.append(P(
        "<b>The window clause.</b> The window was fixed at 7 days before plotting, because the cycle being removed is weekly (Part B.1). "
        "The series is shown from its first recorded day, 1 April 2024; no start date was selected. "
        f"A 28-day version is in the appendix (partD_appendix_28day.png) and does not change the direction: the fitted slope is {N['slope7']:+.1f} sessions/day per day at 7 days and "
        f"{N['slope28']:+.1f} at 28, and the Apr-Aug year-on-year change on matched dates is {N['yoy_7_paired']:+.1%} against {N['yoy_28']:+.1%} "
        f"(the 28-day line has far fewer paired days, because gaps break a wide window). Part B.5 shows how much the choice could matter: of 60 start-and-window combinations, "
        f"32 rise and 28 fall. <b>Symmetry test:</b> would I have made the same choices if they had weakened my conclusion? Yes - the window comes from the weekly cycle, the start is "
        f"the first row of the file, and the appendix is there because the 28-day line could have disagreed."))

    story.append(P("3. Every row removed: rule, count, and what the number moved from and to", h2))
    rows = [[P("Fault", cellb), P("Rule", cellb), P("Count", cellb), P("Moved from -> to", cellb)],
            [P("Duplicate hours", cell), P("keep first (all identical)", cell), P(f"{L['n_duplicates']} rows", cell),
             P(f"rows {L['n_raw']:,} -> {L['n_raw'] - L['n_duplicates']:,}", cell)],
            [P("Sentinel -1 sessions", cell), P("set to NaN, not 0", cell),
             P(f"{L['n_sentinel_raw_rows']} raw / {L['n_sentinel']} after de-dup, on {L['n_sentinel_days']} days", cell),
             P(f"mean sessions/hour {L['mean_hourly_with_sentinel']:.2f} -> {L['mean_hourly_without']:.2f}", cell)],
            [P("Device spellings", cell), P("strip + lower-case", cell), P("6 spellings -> 3", cell), P("rows unchanged", cell)],
            [P("Unrecorded days", cell), P("not filled; line breaks", cell), P(f"{L['n_missing_days']} days = {L['n_hours_missing']} hours", cell),
             P(f"days with data {L['n_days_expected']} -> {L['n_days_recorded']}", cell)],
            [P("Duplicate SKU-0127", cell), P("keep Audio copy (name AUDI-04)", cell), P("1 row", cell),
             P(f"Wearables share {share_with_dup:.2f}% -> {share_clean:.2f}%; largest gap to shares_eight.csv {N['max_share_gap']:.2f} pts (was ~0.9)", cell)],
            [P("Negative net SKUs", cell), P("not drawn; footnoted on the figure", cell),
             P(f"{C['n_negative']} SKUs, PKR {C['negative_total']:.2f}m", cell),
             P(f"net total PKR {C['total_net_before']:,.2f}m -> {C['total_net_after']:,.2f}m (+1 SKU with net exactly 0)", cell)]]
    t = Table(rows, colWidths=[2.9 * cm, 3.6 * cm, 3.9 * cm, 6.9 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#DFE6EE")),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F5F9")),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.3), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.3),
                           ("LEFTPADDING", (0, 0), (-1, -1), 2.5), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5)]))
    story.append(t)
    story.append(P(f"Black Friday (113,710 sessions) is a real event, not a fault: it stays in. Days with one to three dropped hours "
                   f"({L['n_days_with_dropped_hour']}) read slightly low because the day is summed from the hours that were recorded; they are flagged, not filled.", small))

    story.append(P("4. Every level rolled up", h2))
    story.append(P(
        f"The catalogue has {C['n_after']} drawable SKUs. They are rolled up to <b>8 sub-categories under 4 categories</b>, and I cut the depth there because 336 SKU blocks are "
        f"unreadable and the chosen level answers the question. There is <b>no 'Other' bucket</b>: all 8 sub-categories are drawn, the smallest ({N['bottom_sub']}, "
        f"{N['bottom_sub_share']:.1f}%) carries a short label in the treemap and its exact value on panel 4. The fourth hue (pink) always carries a printed label, as vizlib requires. "
        f"The sub-category shares match shares_eight.csv to within {N['max_share_gap']:.2f} percentage points, so the pie of Part C and this treemap are one whole at two grains."))
    return story


for fs in (8.6, 8.4, 8.2, 8.0, 7.8, 7.6, 7.3, 7.0):
    out = HERE / "partE_justification.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                            topMargin=1.2 * cm, bottomMargin=1.1 * cm, title="Week 4 Part E", author="Esha Asif (034)")
    doc.build(build(fs))
    from pypdf import PdfReader
    n = len(PdfReader(str(out)).pages)
    print(f"font {fs}: {n} page(s)")
    if n == 1:
        break
assert n == 1, "Part E must be ONE page"
