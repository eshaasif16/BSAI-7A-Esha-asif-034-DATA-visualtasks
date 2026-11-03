# Part C note: where is supply least reliable?

**Message.** Supply is least reliable in Lashkar (D12), Kotla (D11) and Mehrabad (D13): about 50 interruptions per 1,000 households a year, against 43.7 nationally. **Reader:** a National Grid Authority board member splitting the reliability budget across 24 districts, who will give the figure a few seconds.

## Parameters, and why

- **Denominator: billed households, per 1,000.** Interruptions are logged on feeders that serve connections, and people per household swings from 5.70 to 7.36. With population instead, the top three becomes D13, D12, D21 (Kotla drops out), so the choice matters at the edge. D12 and D13 stay on top either way.
- **Class breaks: Jenks, k = 5**, edges printed in the legend (30.4 / 33.5 / 36.2 / 42.7 / 45.8 / 50.9), fit 0.96. Quantile scored 0.90 by cutting through a cluster of near-identical districts at 40 to 43; equal-interval ties Jenks, so it is a safe choice, not a magic one.
- **Colour: one-hue blues.** A rate has no natural midpoint; the national rate is the dashed line on the bars.
- **Projection: equal-area.** Colour fills area, so area must be honest. The 5 most populous districts hold 12.6% of the land and 59.9% of the people, so the map sits beside a sorted bar chart where each district gets one bar.
- **Axis order and window:** sorted by rate, bars from zero, the register's 12 months, no rescaling.

## The counterfactual

A raw-count version points at Qilabad (D17), Mehrabad (D13) and Zhobara (D24), which hold 41.9% of all interruptions. Counts track size (r with households +0.991); rates don't (+0.175). D17 (40.4) and D24 (42.5) are below the national rate, just big. Only D13 is on both lists, and that is the finding: it is large *and* worse than average.

The count map would take money away from **Lashkar** (1st on rate, 8th on count), **Rohtas West** (4th to 13th), **Chakwa** (5th to 17th), **Ushkan** (6th to 14th) and **Nawabsar** (7th to 23rd). As an illustration with my own rule, not the board's: splitting by count gives those five 11.2% of the budget; splitting by interruptions above the national rate gives them 27.5%.

## Limits

Lashkar and Kotla also rank 1st and 2nd on interruption-minutes per household; Mehrabad is 17th of 22 (its interruptions are short, 102 minutes against a median of 184), and Ilyaspur and Tarmak have no usable minutes. **Suppressed or merged: 0 districts.** The smallest count, 3,234, is +/-3.4% at 95%, so nothing is too noisy to publish.
