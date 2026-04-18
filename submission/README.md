# DAP Submission Pack

This folder organizes the 8 required submission items for the CodeForge DAP project.

## Required Deliverables

1. `01_notebook/CodeForge_DAP_Analysis.ipynb`
2. `02_dataset/` containing the CSV files used for analysis
3. `03_report/CodeForge_Report.docx`
4. `03_report/CodeForge_Report.pdf`
5. `04_presentation/CodeForge_Presentation.pptx`
6. `04_presentation/CodeForge_Presentation.pdf`
7. `01_notebook/CodeForge_DAP_Analysis.pdf`
8. `05_cognitive_report/Cognitive_Report.docx` or `.pdf`

## What Already Exists In This Repo

- Dataset: `data/2026-02-17_exp.csv`, `data/2026-02-24_exp.csv`, `data/2026-03-02_exp.csv`
- Architecture notes: `docs/architecture.md`
- Presentation seed: `docs/presentation_outline.md`
- Notebook-like walkthrough code:
  - `notebooks/01_python_analytics_walkthrough.py`
  - `notebooks/02_cursor_benchmark_walkthrough.py`
- Visualizations in Streamlit pages under `frontend/pages/`
- Dashboard visuals in `dashboard/src/App.jsx`

## Recommended Final Submission Theme

Title:
`CodeForge: AI-Powered Options Market Analytics with Cursor-Optimized Data Processing`

## Minimum 5 Project Objectives

1. To ingest and structure raw options-chain data for analytical use.
2. To compute market intelligence metrics such as PCR, max pain, and open-interest concentration.
3. To detect unusual or anomalous options activity using data-driven methods.
4. To visualize derivatives-market behavior through interactive charts and dashboards.
5. To improve processing efficiency using cursor-based, batch-oriented database access.
6. To compare analytical and database optimization approaches in one integrated system.

## Suggested Key Visualizations

1. Market overview line chart of spot price vs time
2. Open interest by strike bar chart
3. Call vs put OI comparison chart
4. PCR trend chart
5. Volume heatmap across strikes and expiry
6. Volatility smile chart
7. Volatility surface heatmap
8. Anomaly detection scatter/bar chart
9. Database full scan vs cursor batch benchmark chart
10. Top OI strikes summary table

## Formatting Rules To Follow

- IEEE single-column conference style is usually not correct for your requirement here.
- Your requirement says `single page for Springer format double sided for IEEE`; that wording is mixed.
- The safest practical choice is:
  - Use IEEE-style paper sections and citations
  - Keep the document in a clean two-column academic format unless your faculty explicitly says single-column
  - Confirm with faculty whether they want IEEE two-column or Springer LNNS/LNCS style
- Figure captions go below the figure.
- Table titles go above the table.
- All visuals must be numbered and cited inside the text.
- Keep 15 to 20 references only from IEEE / library-approved sources.

## Submission Build Order

1. Finalize the notebook and export PDF.
2. Freeze the dataset files used in the notebook.
3. Write the report in Word using `03_report/report_outline.md`.
4. Export the report to PDF.
5. Convert the report into slides using `04_presentation/ppt_outline.md`.
6. Export the PPT to PDF.
7. Write the cognitive report using `05_cognitive_report/cognitive_report_template.md`.
8. Fill the references tracker using `06_references/reference_tracker.md`.

## Important Academic Note

Do not cite random web pages, blogs, or Google search results. Use IEEE Xplore, Springer, ScienceDirect, Wiley, ACM Digital Library, and your MPSTME library database only.
