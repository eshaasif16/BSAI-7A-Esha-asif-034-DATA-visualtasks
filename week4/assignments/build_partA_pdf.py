"""Builds partA_diagnosis.pdf from partA_diagnosis.json (written by partA_charts.py)
and the 18 single-case figures. Run partA_charts.py first."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

HERE = Path(__file__).resolve().parent


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
H1 = ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=INK, spaceAfter=4)
H2 = ParagraphStyle("h2", fontName="DV-B", fontSize=9, leading=12, textColor=BLUE, spaceBefore=6, spaceAfter=1)
BODY = ParagraphStyle("b", fontName="DV", fontSize=8.6, leading=12.2, textColor=INK)
SMALL = ParagraphStyle("s", fontName="DV", fontSize=7.4, leading=10, textColor=SOFT)
CAP = ParagraphStyle("c", fontName="DV-B", fontSize=7.8, leading=10, textColor=SOFT, alignment=1)

T = json.loads((HERE / "partA_diagnosis.json").read_text())
FIG = HERE / "partA_figures"


def P(text, style=BODY):
    return Paragraph(escape(text), style)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7)
    canvas.setFillColor(SOFT)
    canvas.drawString(1.8 * cm, 1.0 * cm, "Esha Asif - Roll 034 - BSAI 7A - Week 4 Part A. "
                      "All data is synthetic, generated for CDB601220.")
    canvas.drawRightString(A4[0] - 1.8 * cm, 1.0 * cm, f"page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(str(HERE / "partA_diagnosis.pdf"), pagesize=A4, leftMargin=1.8 * cm,
                        rightMargin=1.8 * cm, topMargin=1.5 * cm, bottomMargin=1.7 * cm,
                        title="Week 4 Part A - nine diagnoses", author="Esha Asif (034)")
story = [P("Part A - nine charts, taken apart", H1),
         P("Esha Asif - Roll 034 - BSAI - Section 7A - CDB601220 Data Visualization, Week 4", SMALL),
         Spacer(1, 6),
         P("Every one of these charts is arithmetically correct. What is wrong with each is upstream of the "
           "drawing - a parse, a resample, a window, a denominator - so for each case I rebuilt the chart from its "
           "recipe, checked the brief's self-check number, tried the first objection I could think of and ruled it out "
           "with a number, named the mechanism with the number that proves it, and then drew the honest version. "
           "Both figures are on every page. All numbers come from partA_charts.py (printed in partA_output.txt).")]
rows = [[P("#", CAP), P("Published claim", CAP), P("What was actually going on", CAP)]]
short = {
    "1": "A date column sorted as text: December landed in front of February.",
    "2": "Plotting by row number deleted a 21-day closure; flat, then a step.",
    "3": "A level (concurrent users) summed over days with different numbers of logged hours.",
    "4": "A trailing mean reports a turn half a window (15 days) late.",
    "5": "The window starts at the seasonal peak and ends at the trough.",
    "6": "October has 11 of 31 days; the sum compares a partial month with full ones.",
    "7": "B's volatility passes upward through the stack to D's edge.",
    "8": "Channel flags overlap, so the shares add to 131% and the pie is invalid.",
    "9": "A share rises because the whole fell 40% while premium fell 5%.",
}
for k in sorted(T, key=int):
    rows.append([P(k, BODY), P(T[k]["title"], BODY), P(short[k], BODY)])
tbl = Table(rows, colWidths=[0.8 * cm, 6.6 * cm, 9.6 * cm])
tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#DFE6EE")),
                         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F5F9"))]))
story += [Spacer(1, 10), tbl, Spacer(1, 8),
          P("Three of the nine - the ones where the obvious fix would have repeated the analyst's error - are worth "
            "naming. Case 3 is not fixed by 'use a bigger window', it needs mean() instead of sum(); case 4 is not "
            "fixed by 'smooth less', it needs a centred window; case 9 needs no different chart type, only the "
            "absolute numbers beside the share.", BODY),
          PageBreak()]

for k in sorted(T, key=int):
    t = T[k]
    imgw = 8.5 * cm
    imgh = imgw * 3.9 / 5.6
    pair = Table([[Image(str(FIG / f"case{int(k):02d}_published.png"), imgw, imgh),
                   Image(str(FIG / f"case{int(k):02d}_redesign.png"), imgw, imgh)],
                  [P("As published (rebuilt from the recipe)", CAP), P("Redesign", CAP)]],
                 colWidths=[8.8 * cm, 8.8 * cm])
    pair.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 1),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 1)]))
    story += [P(f"Case {k} - \u201c{t['title']}\u201d", H1),
              P(f"Data: {t['file']}.  Self-check: {t['selfcheck']}", SMALL),
              pair,
              P("The conclusion the chart invites", H2), P(t["conclusion"]),
              P("The first objection, and why it does not hold here", H2), P(t["decoy"]),
              P("The mechanism", H2), P(t["mechanism"]),
              P("The redesign", H2), P(t["redesign"])]
    if k != "9":
        story.append(PageBreak())
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote partA_diagnosis.pdf")
