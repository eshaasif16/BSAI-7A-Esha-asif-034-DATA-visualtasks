# Data Visualization Tasks

This repository contains my assignments, practical work, and experiments for the Data Visualization course as part of my Bachelor of Science in Artificial Intelligence (BSAI) degree. The coursework covers visual perception, chart interpretation, misleading visualizations, statistical plotting, data analysis, and the design of clear and accurate visualizations using Python.

## Student Information

- **Name:** Esha Asif
- **Roll Number:** 034
- **Program:** Bachelor of Science in Artificial Intelligence (BSAI)
- **Section:** 7A
- **University:** Superior University — Gold Campus

## About This Repository

This repository contains coursework completed across different weeks of the Data Visualization course. Each week's work focuses on understanding, creating, analysing, and evaluating visualizations.

The assignments involve working with datasets, writing Python code, generating charts, interpreting results, identifying misleading representations, and improving visual communication through appropriate design choices.

## Coursework

### Week 1 — Introduction to Data Visualization

The initial tasks focus on understanding how visualizations communicate information and how visual design affects the way people interpret data.

Topics include:

- Understanding fundamental visualization principles.
- Exploring how chart design influences interpretation.
- Recognizing patterns and relationships in data.
- Applying visual perception principles to chart design.

### Week 2 — Evaluating and Interpreting Visualizations

The second week's work builds on the basics by focusing on evaluating existing charts and identifying issues that can affect how accurately information is communicated.

Topics include:

- Evaluating the effectiveness of different chart types.
- Identifying misleading visual representations.
- Understanding the effects of axes, scales, and visual encodings.
- Applying principles of accurate and clear data presentation.

### Week 3 — Matplotlib and Seaborn

Week 3 focuses on creating visualizations in Python using Matplotlib and Seaborn.

The assignments involve generating charts, customizing figures, exploring statistical distributions, and using appropriate visualizations to investigate data.

Topics include:

- Creating and customizing charts with Matplotlib.
- Using the object-oriented Matplotlib interface.
- Exploring statistical relationships with Seaborn.
- Comparing distributions and identifying patterns.
- Understanding the effects of bin widths and smoothing.
- Improving chart readability through appropriate labels, titles, and scales.

### Week 4 — Chart Analysis and Visualization Design

Week 4 focuses on evaluating visualization quality, identifying misleading representations, comparing chart formats, cleaning data, and communicating analytical findings.

The coursework is divided into six parts:

| Part | Focus |
|---|---|
| Part A | Diagnosing misleading charts, examining their underlying data, identifying design issues, and producing suitable redesigns. |
| Part B | Calculating and interpreting Lie Factors to evaluate the relationship between visual distortion and changes in the underlying data. |
| Part C | Comparing pie charts and bar charts for representing proportions and rankings, recording reading results, and discussing the limitations of the comparison. |
| Part D | Cleaning and validating time-series data, handling mixed timestamp formats, duplicate records, missing observations, invalid values, and inconsistent categories before creating visualizations. |
| Part E | Preparing a written justification of visualization design decisions, supported by data analysis and relevant evidence. |
| Part F | Analysing seasonal patterns in monthly time-series data and comparing additive and multiplicative approaches to seasonal decomposition. |

The Week 4 assignments emphasize evidence-based visualization decisions. They consider chart accuracy, appropriate visual encodings, data quality, readability, and the limitations of analytical conclusions.

### Week 5 — Visual Channels, Scaling, and Spatial Data

Week 5 moves from judging single charts to understanding *why* a chart misleads. The work uses synthetic data only: a table of sixty countries, a fictional federation of 24 districts with GeoJSON boundaries, small-area counts, and a county crime table. Each misleading chart is traced to one specific decision: the size encoding, the scaling method, the axis order, the denominator, the classification scheme, the boundaries, or the order of radar axes.

The coursework is divided into five parts:

| Part | Focus |
|---|---|
| Part A | Rebuilding nine published, misleading charts from their recipes, diagnosing each one (the conclusion it invites, the decoy objection, the mechanism that actually distorts it), and producing an honest redesign. Cases include a bubble chart sized by population squared, a count choropleth, min–max scaled and badly ordered parallel coordinates, quantile classes on flat rates, a small-area league table, a correlation that changes with the zoning, and a radar chart whose area depends on axis order. |
| Part B | Five decisions answered with numbers rather than opinion: the size range for a bubble chart (area versus radius, Lie Factor, smallest and largest mark), four ways of drawing 9,000 overplotted points, three scalings and PCA on a skewed variable, area computed in degrees versus on the sphere and the Mercator inflation factor, and a funnel plot showing how much of a small-area map is noise. |
| Part C | The two-map activity: the same counties, classes, and colour ramp, mapped once as a raw count and once as a rate per 100,000 residents, with a record of how real readers' answers changed between the two maps and a note on the limitations of such a small test. |
| Part D | Three final figures at 300 dpi: a four-variable bubble chart (position, area, and hue each assigned on purpose), a parallel coordinates plot with its scaling, axis order, and brushed group declared, and a normalized choropleth with named denominator, class breaks, equal-area projection, and join check. |
| Part E | A one-page written justification of the Part D choices: which variable got which visual channel and why, the three parallel-coordinates decisions, the denominator, classification, and projection for the map, and a counterfactual of what the raw-count version would have shown. |

The Week 5 work emphasizes that a chart is a set of encoding decisions, that each decision can be tested and quantified, and that a normalized, declared, equal-area map tells a different story from a raw count of the same data.

<!-- Week 6 below -->

### Week 6 — Integration Checkpoint: Data Processing and Visualization

Week 6 brings the earlier weeks together on a single synthetic dataset from a national electricity operator: a district register, daily returns from six supply zones, monthly generation mix, and district boundaries. The work is marked on two things: how the data is processed before it is trusted, and how the visualization decisions are made and declared.

The board's two questions were where is supply least reliable? and is the shift to renewables real, or is it arithmetic?

The coursework is divided into four parts:

| Part | Focus |
|---|---|
| Part A | Auditing the three CSV files and the GeoJSON in one script, finding the deliberate defects (duplicate keys, text where numbers belong, not-available codes, mixed date formats, calendar gaps, a meter reset, a total row hidden among parts), fixing them with stated rules, and recording each decision in a table with the number of rows affected. |
| Part B | Three charts answering three different kinds of question: a trend (monthly energy delivered per zone, calculated from meter-reading differences rather than summing a counter), a composition (generation mix, showing solar's share growth against a falling total), and a relationship (rooftop solar against income per person). Every parameter that changes a picture is declared on the figure. |
| Part C | One figure for one named reader: a normalized choropleth beside a sorted bar chart showing interruptions per 1,000 households, with a written note covering the denominator, class breaks, projection, and the counterfactual of what a raw-count map would have shown and which districts it would have disadvantaged. |
| Part D (bonus) | An interactive Plotly version of the generation-mix chart, with a short note on what the interaction adds and what it risks. |

The Week 6 work emphasizes that processing and design choices are decisions, and that any decision which changes the picture must be written down: dropping a row versus repairing it, treating an operator's not-available code as missing rather than as a number, normalizing a count before mapping it, and naming the denominator in words.

## Tools and Technologies

The tools used across the coursework include:

- **Python** — data analysis and visualization.
- **Pandas** — data loading, cleaning, and manipulation.
- **NumPy** — numerical operations.
- **Matplotlib** — chart creation and figure customization.
- **Seaborn** — statistical visualization.
- **SciPy** — statistical measures such as rank correlation and Poisson intervals.
- **scikit-learn** — standardization and PCA.
- **ReportLab** — generating the written PDF reports.
- **Plotly** — interactive charts.
- **Jupyter Notebook** — interactive coding and analysis, where applicable.
- **Git and GitHub** — version control and assignment management.

## General Workflow

The assignments generally follow these steps:

1. Load and inspect the relevant dataset.
2. Understand the variables and the question being investigated.
3. Select an appropriate visualization or analytical method.
4. Implement the solution in Python.
5. Generate and inspect the resulting figures.
6. Interpret the results using evidence from the data.
7. Document findings, limitations, and design decisions where required.

## Repository Structure

The repository is organized by week to make the coursework easier to navigate.

```text
BSAI-7A-Esha-asif-034-DATA-visualtasks/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── week1/
│   ├── Assignment notebooks
│   └── Supporting datasets
│
├── week2/
│   └── Week 2 coursework
│
├── week3/
│   ├── assignments/
│   └── Week 3 coursework and supporting files
│
├── week4/
│   ├── README.md
│   └── assignments/
│       ├── Part A files
│       ├── Part B files
│       ├── Part C files
│       ├── Part D files
│       ├── Part E files
│       ├── Part F files
│       ├── data/
│       ├── figures and generated outputs
│       └── supporting scripts and reports
│
├── week5/
│   ├── README.md
│   └── assignments/
│       ├── partA_charts.py, build_partA_diagnosis.py, partA_diagnosis.pdf, partA_numbers.txt
│       ├── figs/  (nine published rebuilds and nine redesigns)
│       ├── partB_decisions.py, partB_output.txt, partB_overplot.png, partB_funnel.png
│       ├── partC_maps.py, partC_mapA.png, partC_mapB.png, partC_reader_protocol.md, partC_reader_results.csv
│       ├── partD_bubble.py/.png, partD_pcp.py/.png, partD_choropleth.py/.png
│       ├── build_partE.py, partE_justification.pdf
│       ├── w5common.py, run_all.sh, requirements.txt
│       ├── data/  (provided files, unchanged)
│       └── geolib.py, vizlib.py  (provided toolkits, unchanged)
│
└── week6/
    └── assignments/
        ├── README.md
        ├── requirements.txt
        ├── partA_process.py, partA_audit.txt, partA_decisions.md
        ├── clean/  (cleaned data written by partA_process.py)
        ├── partB_charts.py, partB_1.png, partB_2.png, partB_3.png
        ├── partC_figure.py, partC_figure.png, partC_note.md
        ├── partD_interactive.py, partD_interactive.html, partD_note.md
        ├── data/  (provided files, unchanged)
        └── geolib.py, tslib.py, vizlib.py  (provided toolkits, unchanged)
```

This is a simplified overview of the repository. Individual folders may contain additional datasets, Python scripts, notebooks, figures, reports, and supporting files.

## Learning Objectives

Through these assignments, I have worked on developing my ability to:

- Understand and apply fundamental data visualization principles.
- Select charts that suit the data and analytical question.
- Interpret patterns, distributions, and relationships.
- Identify misleading visualizations and potential sources of distortion.
- Use Python libraries to create and customize figures.
- Clean and validate data before visualization.
- Audit raw files and document every cleaning decision with a rule and a row count.
- Evaluate visualizations using numerical evidence where appropriate.
- Analyse time-series trends and seasonal patterns.
- Assign visual channels (position, area, hue) to variables according to how precisely each must be read.
- Choose scalings, axis orders, and size ranges for multivariate charts and declare them on the figure.
- Normalize data before mapping it, and explain what a raw-count version would have misled readers into.
- Recognize when small-area rates, boundaries, or projections change a map's message.
- Communicate analytical findings and limitations clearly.
- Consider accessibility and readability when designing charts.

## Author

**Esha Asif**
BS Artificial Intelligence — Section 7A
Roll Number: 034
Superior University — Gold Campus

GitHub: [eshaasif16](https://github.com/eshaasif16)

This repository is maintained as part of my Data Visualization coursework.
