# Week 4 - Time series, proportions and hierarchies

**Esha Asif - Roll 034 - BSAI - Section 7A - CDB601220 Data Visualization, Superior University Lahore**

All data in `data/` is synthetic, generated for CDB601220 Week 4. Nothing here is a finding about a real
business. Part F uses one real public dataset, cited in `partF_SOURCE.md`.

## What I attempted

| Part | What I did | Files |
|---|---|---|
| **A** (36) | Rebuilt all nine published charts from their recipes and hit every self-check number; tested a decoy for each; named and proved each mechanism; plotted all nine redesigns. Both sets are drawn, as 3 x 3 sheets and one pair per case. | `partA_charts.py`, `partA_published_all.png`, `partA_redesigns_all.png`, `partA_figures/`, `partA_output.txt`, `partA_diagnosis.pdf` |
| **B** (15) | All five questions answered in prose with the numbers beside them (look for the word `ANSWER`). | `partB_windows.py`, `partB_output.txt`, `partB_windows.png` |
| **C** (9) | C.1 legality tested in code for all three share tables; both stimuli drawn; the experiment runner and scorer are written. C.2-C.3 need a real reader: `python3 partC_shares.py --run` writes `pie_ranking_results.csv`; running the script again scores it. C.4 is answered. | `partC_shares.py`, `partC_output.txt`, `pie_stimulus.png`, `bars_stimulus.png`, `pie_ranking_results.csv` |
| **D** (25) | The 2 x 2 figure. All six faults in `sessions_hourly.csv` found and handled, each with a stated rule; catalogue duplicate and negatives handled; shares within 0.23 points of `shares_eight.csv`. | `partD_figure.py`, `partD_figure.png`, `partD_appendix_28day.png`, `partD_output.txt` |
| **E** (15) | One page, including the window clause and the symmetry test. | `partE_justification.pdf` (built by `build_partE_pdf.py`) |
| **F** (bonus) | Week 1's seasonality question on real BLS unemployment-by-industry data, with the audit, banked panel, cycle plot and both decompositions. | `partF_cycle.py`, `partF_cycle.png`, `partF_output.txt`, `partF_SOURCE.md`, `partF_data/` |

## Where each answer lives

* **A**: every case has Conclusion, Decoy, Mechanism, Redesign in `partA_diagnosis.pdf` (and in `partA_output.txt`).
* **B.1-B.5**: `partB_output.txt`, each answer starts `ANSWER B1` ... `ANSWER B5`. B.5 includes why the Lie Factor cannot be computed for a chosen window.
* **C.1**: `partC_output.txt`, verdicts (a), (b), (c). **C.4**: last line of that file.
* **D**: the audit of the six faults is at the top of `partD_output.txt`.
* **E**: `partE_justification.pdf`.

## Two honest notes

* `seasonal_decompose(period=365)` (B.3) cannot run: statsmodels needs two full cycles (730 days) and the series has 529.
  The script records the error and answers the question in words instead of skipping it.
* Where a function refuses NaN (decompose, `lag_at_turn`, EWMA), the 13 unrecorded days are linearly interpolated *for that call only*
  and the output says so. The Part D figure itself interpolates nothing.

## Running it

On Windows type `python` where this says `python3`.

```bash
pip install -r requirements.txt
python3 partA_charts.py && python3 build_partA_pdf.py
python3 partB_windows.py
python3 partC_shares.py            # add --run to run the experiment on a reader
python3 partD_figure.py && python3 build_partE_pdf.py
python3 partF_cycle.py
python3 check_submission.py        # last: checks files, 300 dpi, no placeholders, no absolute paths
```

Every script finds `data/` from its own location, so it runs from any folder. `vizlib.py` and `tslib.py` are the course
toolkits, unchanged; `w4common.py` holds the shared cleaning so that Parts B, D and E use the same series.
