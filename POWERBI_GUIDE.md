# Power BI Dashboard — Reference Guide

The dashboard file is at `dashboard/walmart-delivery-analytics.pbix`. Open it directly in Power BI Desktop — all data connections point to the CSVs in `data/powerbi/`, which are included in the repository.

If you move the project folder, use **Transform Data → Data Source Settings** to update the file paths.

---

## Files in `data/powerbi/`

| File | Type | Role |
|---|---|---|
| `fct_orders.csv` | Fact | Central table — connects to all dimensions |
| `dim_date.csv` | Dimension | Time axis and period filters |
| `dim_drivers.csv` | Dimension | Segment, tier, intervention quadrant |
| `dim_customers.csv` | Dimension | Segment, churn flag, lifetime value |
| `dim_regions.csv` | Dimension | Regional KPIs |
| `dim_products.csv` | Dimension | Product ranking |
| `agg_monthly_kpis.csv` | Aggregate | Monthly trend chart |
| `agg_hour_day_heatmap.csv` | Aggregate | Hour × day failure heatmap |
| `agg_region_day.csv` | Aggregate | Failure by region × day |
| `agg_driver_monthly.csv` | Aggregate | Driver monthly consistency index |
| `agg_financial_impact.csv` | Aggregate | Cost by driver quadrant |
| `agg_top_products.csv` | Aggregate | Product ranking |
| `agg_retention_summary.csv` | Aggregate | Retention metrics |

---

## Data Model (Star Schema)

```
fct_orders[date_key]    → dim_date[date_key]         (Many:1)
fct_orders[driver_id]   → dim_drivers[driver_id]     (Many:1)
fct_orders[customer_id] → dim_customers[customer_id] (Many:1)
fct_orders[region]      → dim_regions[region]        (Many:1)
```

The `agg_*` tables are used directly in specific visuals without relationships to `fct_orders` — they already contain pre-aggregated data.

---

## DAX Measures

```dax
Total Orders = COUNTROWS(fct_orders)

Total Revenue = SUM(fct_orders[order_amount])

Avg Ticket = AVERAGE(fct_orders[order_amount])

Failure Rate =
DIVIDE(
    COUNTROWS(FILTER(fct_orders, fct_orders[has_missing] = TRUE())),
    COUNTROWS(fct_orders),
    0
)

Total Failure Cost = SUM(fct_orders[failure_cost])

Failure Rate vs Global =
VAR CurrentRate = [Failure Rate]
VAR GlobalRate  = 0.15
RETURN CurrentRate - GlobalRate

High Risk Drivers =
CALCULATE(
    DISTINCTCOUNT(dim_drivers[driver_id]),
    dim_drivers[intervention_quadrant] = "Chronic — Disciplinary Action"
)

Coaching Needed =
CALCULATE(
    DISTINCTCOUNT(dim_drivers[driver_id]),
    dim_drivers[intervention_quadrant] = "Unstable — Coaching"
)

Customers with Failure =
CALCULATE(
    COUNTROWS(dim_customers),
    dim_customers[had_failure] = TRUE()
)

Churned Customers =
CALCULATE(
    COUNTROWS(dim_customers),
    dim_customers[churned] = TRUE()
)

Revenue at Risk =
CALCULATE(
    SUM(dim_customers[total_revenue]),
    dim_customers[churned] = TRUE()
)

Projected Savings 30pct = [Total Failure Cost] * 0.30
```

---

## Dashboard Pages

### Page 1 — Executive Overview
Global KPIs (orders, revenue, ticket, failure rate, cost, churn), monthly trend with dual axis (orders + revenue), and revenue by region.

Filters: Month / Semester / Day of Week

### Page 2 — Delivery Quality
Failure rate by region (vs. global average), hour × day heatmap, failure by day of week, and breakdown by time period (overnight / morning / afternoon / evening).

Filters: Region / Month / Semester

### Page 3 — Driver Performance
Driver quadrant distribution (chronic / unstable / improving / stable), top 15 critical drivers table, failure rate distribution histogram, and H1 vs H2 scatter plot.

Filters: Experience Tier / Quadrant / Region

### Page 4 — Customer Impact
Customer failure profile (donut), churn rate by number of failures, purchase frequency comparison (with vs. without failure), and churned customer detail table.

Filters: Value Segment / Failure Group / Age

### Page 5 — Action Plan
Current total cost, projected savings from the 30% reduction target, priority action table, and cost-by-quadrant bar chart.

---

## Regenerating the CSVs

If you rerun the Python analysis and want to refresh the Power BI data:

```bash
python export_powerbi.py
```

Then in Power BI Desktop: **Home → Refresh**.
