# Week 6 - CDB601220 - integration checkpoint

Drop this folder into `week6/assignments/` (next to `data/`, `geolib.py`, `tslib.py`, `vizlib.py`). Nothing here uses an absolute path, and `data/` is read, never written.

1. `pip install -r requirements.txt`
2. `python3 partA_process.py` - audits the raw files, prints the audit, writes `clean/`, `partA_audit.txt`, `partA_decisions.md`. **Run this first**, the rest read `clean/`.
3. `python3 partB_charts.py` - writes `partB_1.png` (trend: monthly energy by zone), `partB_2.png` (composition: generation mix), `partB_3.png` (relationship: solar vs income).
4. `python3 partC_figure.py` - writes `partC_figure.png` (map + sorted bars) and prints every number quoted in `partC_note.md`.
5. `python3 partD_interactive.py` (bonus, D1) - writes `partD_interactive.html`; the two required sentences are in `partD_note.md`.

Cleaned data is produced only by `partA_process.py`; no CSV was edited by hand. Figures export at 300 dpi with a source note. The decisions table is `partA_decisions.md`; the half-page for the board figure is `partC_note.md`.
