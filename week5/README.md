# CDB601220 Week 5 - submission folder

Run `./run_all.sh` (or each script in the order below). Python 3.10+, `pip install -r requirements.txt`.
No geopandas, no shapely: boundaries are read with `geolib.read_geojson()`.

| Part | Files |
|---|---|
| A | `partA_charts.py` (18 figures in `figs/`, numbers in `partA_numbers.txt`), `build_partA_diagnosis.py` -> `partA_diagnosis.pdf` |
| B | `partB_decisions.py` -> `partB_output.txt`, `partB_overplot.png`, `partB_funnel.png` |
| C | `partC_maps.py` -> `partC_mapA.png`, `partC_mapB.png`, `partC_maps_side_by_side.png`; `partC_reader_protocol.md`; `partC_reader_results.csv` (**you fill this**) |
| D | `partD_bubble.py/.png`, `partD_pcp.py/.png`, `partD_choropleth.py/.png` (all 300 dpi) |
| E | `build_partE.py` -> `partE_justification.pdf` (one page) |
| shared | `w5common.py` (helpers), `geolib.py` and `vizlib.py` (course toolkit, unmodified), `data/` |

## Things I found in the toolkit and brief (also noted in the PDFs)
- `geolib.corr_chain()` crashes on pandas 3.x (read-only array). `w5common.safe_corr_chain()` is the same rule with a `.copy()`.
- Case 1: the brief's "589x" is the DIAMETER ratio; the AREA ratio with `s = pop_m**2` is 346,921x.
- `geolib`'s docstring says Mercator inflates area by sec(lat); measured, it is sec^2(lat). Part B reports the measured number.

## STILL TO DO BY A HUMAN (what I could not do for you)
1. **Part C readers.** Run at least five real readers using `partC_reader_protocol.md`, fill `partC_reader_results.csv`,
   then re-run `partC_maps.py` and `build_partE.py`. Until then, Part E has a yellow highlighted gap.
2. **Make the words yours.** Read `partA_diagnosis.pdf`, `partE_justification.pdf` and `partB_output.txt` and
   re-phrase in your own voice. You will be asked about them. If any number does not reproduce on your
   machine, say so and give yours: the brief treats that as a finding.
3. **Part F (bonus, if the brief offers it)**: needs your own real-world dataset and boundaries; I did not attempt it.
4. **Check the submission rules in TASKS.md** (file names, naming convention, whether PDFs or a zip are wanted, your name/ID).
5. **Run it once on your own machine** from a clean folder to confirm it reproduces.
