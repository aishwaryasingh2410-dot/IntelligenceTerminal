# Team Rocket Report Outline

## Title
Team Rocket: AI-Powered Options Market Analytics with Cursor-Optimized Database Processing

## Abstract

Write a 150 to 250 word abstract covering:
- the problem of large-scale options-chain analysis
- the need for both analytics and efficient data retrieval
- the use of Python, MongoDB, Streamlit/React
- key outputs such as PCR, max pain, anomaly detection, and visual analytics
- a brief conclusion on performance and usability

## Keywords

Options chain, market analytics, open interest, put-call ratio, anomaly detection, MongoDB, cursor optimization, visualization

## 1. Introduction

Cover:
- background of options-market analytics
- difficulty of handling multi-dimensional options data
- need for decision-support dashboards
- motivation for combining analytics and DBMS optimization

## 2. Problem Statement

State that the project addresses:
- large and complex options-chain data
- slow or inefficient querying under full scans
- limited interpretability of raw market data
- need for anomaly detection and visual decision support

## 3. Objectives

Use at least these five:
1. To organize raw options-chain records into a structured analytics pipeline.
2. To compute important market indicators such as PCR and max pain.
3. To identify concentration of open interest across strikes and expiries.
4. To detect unusual open-interest behavior through analytical methods.
5. To improve database retrieval using cursor-based batch processing.
6. To present insights through interactive and well-labeled visualizations.

## 4. Dataset Description

Describe the files in `data/`:
- `2026-02-17_exp.csv`
- `2026-02-24_exp.csv`
- `2026-03-02_exp.csv`

Mention typical fields:
- `datetime`
- `expiry`
- `strike`
- `spot_close`
- `oi_CE`, `oi_PE`
- `volume_CE`, `volume_PE`
- `ATM`

Add:
- number of files
- total rows
- preprocessing steps
- missing-value handling
- column normalization

Table title example:
`Table 1. Dataset attributes and descriptions`

## 5. Methodology

### 5.1 System Architecture

Use [architecture.md](c:/Users/91810/OneDrive/Desktop/hackathon/Team Rocket/docs/architecture.md) and explain:
- ingestion layer
- database layer
- analytics layer
- visualization layer

### 5.2 Analytical Methods

Explain each briefly:
- Put-Call Ratio
- Max Pain
- Top Open Interest Strikes
- OI Change by Strike
- Unusual OI detection

Reference the implementation basis:
- [pcr.py](c:/Users/91810/OneDrive/Desktop/hackathon/Team Rocket/backend/analysis/pcr.py)
- [max_pain.py](c:/Users/91810/OneDrive/Desktop/hackathon/Team Rocket/backend/analysis/max_pain.py)
- [anomaly.py](c:/Users/91810/OneDrive/Desktop/hackathon/Team Rocket/backend/analysis/anomaly.py)

### 5.3 Database Optimization

Discuss:
- batch processing
- cursor-based reads
- checkpoint-based resume
- indexed filtering using `expiry`, `strike`, `datetime`

## 6. Implementation

Describe the technology stack:
- Python
- Pandas
- Plotly
- Scikit-learn
- MongoDB
- Node.js/Express
- React
- Streamlit

## 7. Results and Discussion

This section should contain most of the figures.

### Recommended figure sequence

Figure 1. Overall system architecture
Figure 2. Spot price trend over time
Figure 3. Open interest by strike
Figure 4. Call vs put OI comparison
Figure 5. PCR trend and sentiment interpretation
Figure 6. Volume heatmap across strikes and expiries
Figure 7. Volatility smile
Figure 8. Volatility surface
Figure 9. Unusual OI detection output
Figure 10. Full scan vs cursor batch benchmark

For each figure:
- keep caption below the figure
- mention the business insight in 2 to 4 lines
- cite the figure in the paragraph before or after it

### Recommended tables

Table 1. Dataset attributes and descriptions
Table 2. Summary statistics of the options dataset
Table 3. Top 5 high OI strikes
Table 4. Database performance comparison

For each table:
- title above table
- table cited in text

## 8. Conclusion

Mention:
- the project successfully combines analytics and DBMS concepts
- PCR, max pain, OI concentration, and anomaly detection improve interpretability
- cursor-based retrieval improves scalability compared with full scans
- dashboards make the outputs easier for analysts and students to interpret

## 9. Future Scope

Possible points:
- live market streaming
- predictive modeling
- Greeks-based analytics
- alert engine
- deployment on cloud infrastructure

## 10. References

Use 15 to 20 references only.
Source priority:
- IEEE Xplore
- Springer
- Elsevier/ScienceDirect
- ACM DL
- MPSTME library sources

Avoid:
- blogs
- random websites
- Google search result pages
- Wikipedia

## Appendix

You can include:
- screenshots of dashboard pages
- notebook snippets
- schema/index summary
