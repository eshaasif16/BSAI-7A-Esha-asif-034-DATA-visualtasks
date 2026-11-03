Data Visualization Tasks

This repository contains my assignments, practical work, and experiments for the Data Visualization course as part of my Bachelor of Science in Artificial Intelligence (BSAI) degree. The coursework covers visual perception, chart interpretation, misleading visualizations, statistical plotting, data analysis, and the design of clear and accurate visualizations using Python.

Student Information
Name: Esha Asif
Roll Number: 034
Program: Bachelor of Science in Artificial Intelligence (BSAI)
Section: 7A
University: Superior University — Gold Campus
About This Repository

This repository contains coursework completed across different weeks of the Data Visualization course. Each week's work focuses on understanding, creating, analysing, and evaluating visualizations.

The assignments involve working with datasets, writing Python code, generating charts, interpreting results, identifying misleading representations, and improving visual communication through appropriate design choices.

Coursework
Week 1 — Introduction to Data Visualization

The initial tasks focus on understanding how visualizations communicate information and how visual design affects the way people interpret data.

Topics include:

Understanding fundamental visualization principles.
Exploring how chart design influences interpretation.
Recognizing patterns and relationships in data.
Applying visual perception principles to chart design.
Week 2 — Evaluating and Interpreting Visualizations

The second week's work builds on the basics by focusing on evaluating existing charts and identifying issues that can affect how accurately information is communicated.

Topics include:

Evaluating the effectiveness of different chart types.
Identifying misleading visual representations.
Understanding the effects of axes, scales, and visual encodings.
Applying principles of accurate and clear data presentation.
Week 3 — Matplotlib and Seaborn

Week 3 focuses on creating visualizations in Python using Matplotlib and Seaborn.

The assignments involve generating charts, customizing figures, exploring statistical distributions, and using appropriate visualizations to investigate data.

Topics include:

Creating and customizing charts with Matplotlib.
Using the object-oriented Matplotlib interface.
Exploring statistical relationships with Seaborn.
Comparing distributions and identifying patterns.
Understanding the effects of bin widths and smoothing.
Improving chart readability through appropriate labels, titles, and scales.
Week 4 — Chart Analysis and Visualization Design

Week 4 focuses on evaluating visualization quality, identifying misleading representations, comparing chart formats, cleaning data, and communicating analytical findings.

The coursework is divided into six parts:

Part	Focus
Part A	Diagnosing misleading charts, examining their underlying data, identifying design issues, and producing suitable redesigns.
Part B	Calculating and interpreting Lie Factors to evaluate the relationship between visual distortion and changes in the underlying data.
Part C	Comparing pie charts and bar charts for representing proportions and rankings, recording reading results, and discussing the limitations of the comparison.
Part D	Cleaning and validating time-series data, handling mixed timestamp formats, duplicate records, missing observations, invalid values, and inconsistent categories before creating visualizations.
Part E	Preparing a written justification of visualization design decisions, supported by data analysis and relevant evidence.
Part F	Analysing seasonal patterns in monthly time-series data and comparing additive and multiplicative approaches to seasonal decomposition.

The Week 4 assignments emphasize evidence-based visualization decisions. They consider chart accuracy, appropriate visual encodings, data quality, readability, and the limitations of analytical conclusions.

Week 5 —
<!-- Week 5 section to be added after Week 6 is finished. -->
Week 6 — Integration Checkpoint: Data Processing and Visualization

Week 6 brings the earlier weeks together on a single synthetic dataset from a national electricity operator: a district register, daily returns from six supply zones, monthly generation mix, and district boundaries. The work is marked on two things: how the data is processed before it is trusted, and how the visualization decisions are made and declared.

The board's two questions were where is supply least reliable? and is the shift to renewables real, or is it arithmetic?

The coursework is divided into four parts:

Part	Focus
Part A	Auditing the three CSV files and the GeoJSON in one script, finding the deliberate defects (duplicate keys, text where numbers belong, not-available codes, mixed date formats, calendar gaps, a meter reset, a total row hidden among parts), fixing them with stated rules, and recording each decision in a table with the number of rows affected.
Part B	Three charts answering three different kinds of question: a trend (monthly energy delivered per zone, calculated from meter-reading differences rather than summing a counter), a composition (generation mix, showing solar's share growth against a falling total), and a relationship (rooftop solar against income per person). Every parameter that changes a picture is declared on the figure.
Part C	One figure for one named reader: a normalized choropleth beside a sorted bar chart showing interruptions per 1,000 households, with a written note covering the denominator, class breaks, projection, and the counterfactual of what a raw-count map would have shown and which districts it would have disadvantaged.
Part D (bonus)	An interactive Plotly version of the generation-mix chart, with a short note on what the interaction adds and what it risks.

The Week 6 work emphasizes that processing and design choices are decisions, and that any decision which changes the picture must be written down: dropping a row versus repairing it, treating an operator's not-available code as missing rather than as a number, normalizing a count before mapping it, and naming the denominator in words.

Tools and Technologies

The tools used across the coursework include:

Python — data analysis and visualization.
Pandas — data loading, cleaning, and manipulation.
NumPy — numerical operations.
Matplotlib — chart creation and figure customization.
Seaborn — statistical visualization.
SciPy — statistical measures such as rank correlation.
Plotly — interactive charts.
Jupyter Notebook — interactive coding and analysis, where applicable.
Git and GitHub — version control and assignment management.
General Workflow

The assignments generally follow these steps:

Load and inspect the relevant dataset.
Understand the variables and the question being investigated.
Select an appropriate visualization or analytical method.
Implement the solution in Python.
Generate and inspect the resulting figures.
Interpret the results using evidence from the data.
Document findings, limitations, and design decisions where required.
Repository Structure

The repository is organized by week to make the coursework easier to navigate.

text
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
│   └── Week 5 coursework
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

This is a simplified overview of the repository. Individual folders may contain additional datasets, Python scripts, notebooks, figures, reports, and supporting files.

Learning Objectives

Through these assignments, I have worked on developing my ability to:

Understand and apply fundamental data visualization principles.
Select charts that suit the data and analytical question.
Interpret patterns, distributions, and relationships.
Identify misleading visualizations and potential sources of distortion.
Use Python libraries to create and customize figures.
Clean and validate data before visualization.
Audit raw files and document every cleaning decision with a rule and a row count.
Evaluate visualizations using numerical evidence where appropriate.
Analyse time-series trends and seasonal patterns.
Normalize data before mapping it, and explain what a raw-count version would have misled readers into.
Communicate analytical findings and limitations clearly.
Consider accessibility and readability when designing charts.
Author

Esha Asif
BS Artificial Intelligence — Section 7A
Roll Number: 034
Superior University — Gold Campus

GitHub: eshaasif16

This repository is maintained as part of my Data Visualization coursework.
