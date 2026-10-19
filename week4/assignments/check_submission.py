"""Run last: python3 check_submission.py - the marker's complaints from Week 3, checked before the marker does."""
import re
import sys
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
problems, notes = [], []

required = ["README.md", "partA_charts.py", "partA_diagnosis.pdf", "partA_published_all.png", "partA_redesigns_all.png",
            "partA_output.txt", "partB_windows.py", "partB_output.txt", "partC_shares.py", "partC_output.txt",
            "pie_stimulus.png", "bars_stimulus.png", "partD_figure.py", "partD_figure.png", "partD_output.txt",
            "partE_justification.pdf", "vizlib.py", "tslib.py", "w4common.py"]
for f in required:
    if not (ROOT / f).exists():
        problems.append(f"missing {f}")
for f in sorted((ROOT / "data").glob("*")):
    pass
if len(list((ROOT / "data").glob("*"))) < 13:
    problems.append("data/ folder incomplete (need 12 datasets + DATA_DICTIONARY.md)")

# every PNG at exactly 300 dpi
for png in ROOT.rglob("*.png"):
    dpi = Image.open(png).info.get("dpi", (0, 0))[0]
    if round(dpi) != 300:
        problems.append(f"{png.relative_to(ROOT)} is {dpi} dpi, not 300")

# Part E is one page
if len(PdfReader(str(ROOT / "partE_justification.pdf")).pages) != 1:
    problems.append("partE_justification.pdf is not one page")

# no caches, no download suffixes, no duplicate files, no spaces in names
for p in ROOT.rglob("*"):
    rel = p.relative_to(ROOT)
    if "__pycache__" in rel.parts or p.suffix == ".pyc":
        problems.append(f"cache committed: {rel}")
    if re.search(r" \(\d+\)|\s", p.name):
        problems.append(f"download suffix or space in name: {rel}")
names = [p.name for p in ROOT.rglob("*") if p.is_file()]
for n in set(names):
    if names.count(n) > 1:
        problems.append(f"file appears twice: {n}")

# no placeholders and no absolute paths in anything a marker reads
for p in list(ROOT.glob("*.txt")) + list(ROOT.glob("*.md")) + list(ROOT.glob("*.json")):
    if p.name == "check_submission.py":
        continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    if "___" in t or "Your result here" in t:
        problems.append(f"placeholder text in {p.name}")
    if re.search(r"/home/|/Users/|[A-Z]:\\\\", t):
        problems.append(f"absolute path in {p.name}")

# the one thing a script cannot do for you
if not (ROOT / "pie_ranking_results.csv").exists():
    notes.append("pie_ranking_results.csv is missing: run  python3 partC_shares.py --run  with a REAL reader, then "
                 "python3 partC_shares.py  to score it (Part C.2-C.3, 5 marks).")
if not (ROOT / "partF_SOURCE.md").exists():
    notes.append("partF_SOURCE.md missing (Part F bonus).")

print("PROBLEMS:" if problems else "no problems found")
for x in problems:
    print("  -", x)
for x in notes:
    print("TO DO:", x)
sys.exit(1 if problems else 0)
