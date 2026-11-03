# Part C - how to run the two-map test (needs REAL people)

You need **at least five readers**. They must be real. Do not invent or "simulate" readers: the
brief marks this, and a made-up result is academic misconduct. Friends, flatmates and family are fine.
They do not need to know any statistics. Do not tell them what the test is about until the end.

## What to prepare
- `partC_mapA.png` (crimes reported, the COUNT) and `partC_mapB.png` (crimes per 100,000, the RATE).
- Show **Map A alone first**. Do not show `partC_maps_side_by_side.png` to anyone until the end.
- Use an anonymous reader id (R1, R2, ...). Do not record names.

## What to say, word for word, for each reader
1. Show Map A. Say: *"This map shows crimes reported in each county. Name the three counties you
   would be most worried about."* Write down the three names, in the order they say them.
2. Take Map A away. Show Map B. Say: *"This map shows crimes per 100,000 residents in each
   county. Name the three counties you would be most worried about."* Write down the three names.
3. Only after both: ask *"Did your answers change? Why?"* and jot their reason in `notes`.

Keep the order the same for every reader (A then B). Say that this order effect is a limitation in
your write-up (readers may have learned something from Map A).

## Where to record the results
Open `partC_reader_results.csv` and add one row per reader:

    reader_id,a1,a2,a3,b1,b2,b3,overlap_count,notes
    R1,Dunmere,Pellbrook,Grimsby,Hollowfield,Netherby,Elmsworth,0,"said 'oh, it is the small ones'"

County names must match `county_crime.csv` exactly (Alder, Birchwood, Calder, Dunmere, Elmsworth,
Foxhall, Grimsby, Hollowfield, ...). `overlap_count` is how many of the three names appear in BOTH
lists (the script recomputes it and warns if you got it wrong).

## Then
    python3 partC_maps.py      # scores your readers
    python3 build_partE.py     # puts your real numbers into the Part E counterfactual paragraph

## For the write-up (a few honest sentences)
- n readers, mean overlap out of 3.
- It is a tiny convenience sample, not a study. Say so.
- Reference points from the data: the top three counties by count are Dunmere, Pellbrook, Grimsby; by
  rate they are Hollowfield, Netherby, Elmsworth. Overlap between those two top-threes is 0.
