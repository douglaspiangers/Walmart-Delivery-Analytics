# Walmart Delivery Analytics

Analysis of delivery failures in a grocery operation covering 7 cities in the Orlando, FL area. The goal was to figure out what's driving missing items in deliveries — and whether the problem sits with the drivers or the customers.

---

## The Problem

10,000 orders processed in 2023. $2.83M in revenue. And 15% of deliveries arrived with at least one missing item — generating customer complaints, redelivery costs, and churn.

The central question: is this an operational problem or a customer behavior problem?

---

## Key Findings

| Metric | Value |
|---|---|
| Orders analyzed | 10,000 (Jan–Dec 2023) |
| Total revenue | $2,833,022 |
| Overall failure rate | 15.0% — 1 in 7 deliveries |
| Driver SHAP contribution | 66.8% of predictive power |
| Customer SHAP contribution | 3.4% |
| Driver vs. customer explanatory ratio | 19× |
| Highest-risk region | Altamonte Springs (16.2%) |
| Best-performing region | Sanford (13.9%) |
| Peak failure day | Monday (16.1%) |
| Customers with at least one failure | 71% of the base (881 of 1,239) |
| Post-failure churn rate | 7.8% (26 customers) |
| Revenue at risk from churn | $47,371 |
| Model AUC (Random Forest) | 0.80 |

The driver explains 19× more than the customer. The problem is operational.

---

## Recommendations

**1. Driver retraining program**
Mandatory retraining for drivers with a failure rate above 20% over at least 20 deliveries. Expected impact: roughly $32k/year in recovered costs.

**2. Monday reinforcement**
Monday consistently shows the highest failure rate (16.1%). Additional QA checks and a mandatory double-check protocol for Monday dispatches.

**3. Regional audit — Altamonte Springs**
16.2% failure rate, the highest in the network. On-site process audit comparing operations with Sanford (13.9%, the best-performing region).

**4. Checklist for large orders**
Digital checklist required for orders above $400 or with more than 12 items.

---

## Project Structure

```
walmart-delivery-analytics/
├── data/
│   ├── raw/                    # Original CSV files (5 tables)
│   ├── processed/              # Cleaned Parquet files + shap_results.json
│   └── powerbi/                # Star-schema CSVs for Power BI (13 files)
├── notebooks/
│   ├── 01_data_profiling.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_analysis.ipynb
│   ├── 04_business_insights.ipynb
│   ├── 05_delivery_quality_analysis.ipynb
│   ├── 07_causal_analysis.ipynb
│   ├── 08_segmentation.ipynb
│   ├── 09_driver_cohort_analysis.ipynb
│   ├── 10_customer_retention_analysis.ipynb
│   └── 11_executive_conclusion.ipynb
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   └── visualization.py
├── dashboard/
│   ├── dashboard.py                         # Plotly Dash app (4 tabs)
│   └── walmart-delivery-analytics.pbix      # Power BI report (5 pages)
├── reports/figures/                         # Exported PNG charts
├── sql/                                     # SQL scripts
├── run_analysis.py                          # Full pipeline script
├── run_shap_export.py                       # SHAP export without Jupyter
├── export_powerbi.py                        # Generates star-schema CSVs
├── POWERBI_GUIDE.md                         # Data model and DAX reference
└── requirements.txt
```

---

## Datasets

| File | Rows | Description |
|---|---|---|
| `orders.csv` | 10,000 | Core transaction table — date, amount, region, delivery hour, driver and customer IDs |
| `customers.csv` | 1,239 | Customer registry — name, age |
| `drivers.csv` | 1,247 | Driver registry — name, age, total trip count |
| `order_items.csv` | 1,662 | Maps orders to individual products |
| `products.csv` | 314 | Product catalog — name, category, unit price |

---

## Notebooks

| # | Notebook | What it covers |
|---|---|---|
| 01 | Data Profiling | Schema, nulls, duplicates, issues table |
| 02 | Data Cleaning | Type fixes, normalization, master join → Parquet export |
| 03 | Exploratory Analysis | Monthly trends, regional revenue, delivery heatmap, age distribution |
| 04 | Business Insights | Executive KPIs, region performance table, top products |
| 05 | Delivery Quality | Failure rates by region, day, driver ranking, hour×day heatmap |
| 07 | Causal Analysis | Logistic regression, Random Forest, SHAP values — what drives failures |
| 08 | Segmentation | K-Means clustering for drivers (3 groups) and customers (4 groups) |
| 09 | Driver Cohort | H1 vs H2 performance, whether experience reduces failures |
| 10 | Customer Retention | Churn analysis, post-failure return rate, revenue at risk |
| 11 | Executive Conclusion | Final answer: drivers vs. customers — SHAP + statistical tests |

---

## Power BI Dashboard

The file `dashboard/walmart-delivery-analytics.pbix` has the full interactive report — 5 pages covering executive overview, delivery quality, driver performance, customer impact, and the action plan with projected savings.

**To open:** Power BI Desktop → File → Open → select the `.pbix` file.

The CSVs in `data/powerbi/` are the pre-built star schema used by the report. The `POWERBI_GUIDE.md` file documents the data model relationships and all DAX measures used.

---

## Plotly Dash Dashboard

A 4-tab web app for operational visibility.

| Tab | Content |
|---|---|
| Executive Overview | Global KPIs, monthly trend, regional revenue |
| Delivery Quality | Failure rate by region, day, and hour |
| Driver Performance | Worst/best driver ranking, H1 vs H2 scatter |
| Customer Impact | Churn by failure count, at-risk revenue |

```bash
python dashboard/dashboard.py
# Open http://localhost:8050
```

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Option A — Full pipeline (generates all charts and processed data)
python -X utf8 run_analysis.py

# Option B — Notebooks in order
jupyter notebook notebooks/

# Option C — Plotly Dash app
python dashboard/dashboard.py
```

> Run `run_analysis.py` (or notebooks 01–02) before launching the Dash app — it requires the processed Parquet files.

---

## Stack

Python 3.14 · Pandas 3.0 · Scikit-Learn · SHAP · SciPy · Plotly Dash · Matplotlib · Seaborn · Power BI

---

**Douglas Piangers** · Data Scientist  
[GitHub](https://github.com/douglaspiangers) · [LinkedIn](https://linkedin.com/in/douglaspiangers)
