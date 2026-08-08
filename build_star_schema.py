import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR    = Path("c:/Users/d_men/OneDrive/Área de Trabalho/Projeto Walmart")
OUT_DIR    = Path("c:/Users/d_men/OneDrive/Área de Trabalho/tabelas limpas")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load raw files
orders    = pd.read_csv(RAW_DIR / "novas tabelas/5qPZ8EyPSau2UNVvdRak_orders.csv")
drivers   = pd.read_csv(RAW_DIR / "novas tabelas/DASNKm5LTPy2hXX0dM0D_drivers_data.csv")
customers = pd.read_csv(RAW_DIR / "novas tabelas/i7WiftZQm2ToVfzHFBBW_customers_data.csv")
products  = pd.read_csv(RAW_DIR / "novas tabelas/PGqj7HULTByfy23R8vxN_products_data.csv")
missing   = pd.read_csv(RAW_DIR / "LKyEGqe9QsWdRFCujqRc_missing_items_data.csv")

def age_group(age):
    if age <= 29:  return "18-29"
    if age <= 44:  return "30-44"
    if age <= 59:  return "45-59"
    return "60+"

# ── dim_date — full 2023 calendar
dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
dim_date = pd.DataFrame({
    "date_key":    dates.strftime("%Y%m%d").astype(int),
    "date":        dates.strftime("%Y-%m-%d"),
    "year":        dates.year,
    "quarter":     dates.quarter,
    "quarter_label": "Q" + dates.quarter.astype(str) + " " + dates.year.astype(str),
    "month_num":   dates.month,
    "month_name":  dates.strftime("%B"),
    "month_label": dates.strftime("%b %Y"),
    "week_of_year":dates.isocalendar().week.values,
    "day_of_month":dates.day,
    "day_name":    dates.strftime("%A"),
    "is_weekend":  dates.dayofweek.isin([5, 6]).astype(int),
})
dim_date.to_excel(OUT_DIR / "dim_date.xlsx", index=False)
print(f"dim_date.xlsx           {len(dim_date):>6,} rows")

# ── dim_region — 7 zones extracted from orders
regions = (
    orders[["region"]].drop_duplicates()
    .sort_values("region")
    .reset_index(drop=True)
)
regions.insert(0, "region_id", range(1, len(regions) + 1))
regions.columns = ["region_id", "region_name"]
regions.to_excel(OUT_DIR / "dim_region.xlsx", index=False)
print(f"dim_region.xlsx         {len(regions):>6,} rows")

# ── dim_driver — drops Trips, adds age_group
dim_driver = drivers[["driver_id", "driver_name", "age"]].copy()
dim_driver["age_group"] = dim_driver["age"].apply(age_group)
dim_driver.to_excel(OUT_DIR / "dim_driver.xlsx", index=False)
print(f"dim_driver.xlsx         {len(dim_driver):>6,} rows")

# ── dim_customer — adds age_group
dim_customer = customers.rename(columns={"customer_age": "age"}).copy()
dim_customer["age_group"] = dim_customer["age"].apply(age_group)
dim_customer.to_excel(OUT_DIR / "dim_customer.xlsx", index=False)
print(f"dim_customer.xlsx       {len(dim_customer):>6,} rows")

# ── dim_product — fixes typo produc_id → product_id, cleans price
dim_product = products.rename(columns={"produc_id": "product_id"}).copy()
dim_product["unit_price"] = (
    dim_product["price"].str.replace("$", "", regex=False).astype(float)
)
dim_product = dim_product.drop(columns=["price"])
dim_product.to_excel(OUT_DIR / "dim_product.xlsx", index=False)
print(f"dim_product.xlsx        {len(dim_product):>6,} rows")

# ── fact_orders — cleans order_amount, extracts delivery hour, adds keys
orders["date"] = pd.to_datetime(orders["date"])
orders["order_amount"] = (
    orders["order_amount"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)
orders["delivery_hour"] = (
    pd.to_datetime(orders["delivery_hour"], format="%H:%M:%S").dt.hour
)

region_map = regions.set_index("region_name")["region_id"]
orders["region_id"] = orders["region"].map(region_map)
orders["date_key"]   = orders["date"].dt.strftime("%Y%m%d").astype(int)
orders["has_missing"] = (orders["items_missing"] > 0).astype(int)

fact_orders = orders[[
    "order_id", "date_key", "region_id", "driver_id", "customer_id",
    "order_amount", "items_delivered", "items_missing",
    "delivery_hour", "has_missing"
]]
fact_orders.to_excel(OUT_DIR / "fact_orders.xlsx", index=False)
print(f"fact_orders.xlsx        {len(fact_orders):>6,} rows")

# ── fact_missing_items — UNPIVOT: 3 columns → rows
melted = missing.melt(
    id_vars="order_id",
    value_vars=["product_id_1", "product_id_2", "product_id_3"],
    var_name="position_label",
    value_name="product_id",
)
melted = melted.dropna(subset=["product_id"])
melted["position"] = melted["position_label"].str.extract(r"(\d)").astype(int)
fact_missing = melted[["order_id", "product_id", "position"]].sort_values(
    ["order_id", "position"]
).reset_index(drop=True)
fact_missing.to_excel(OUT_DIR / "fact_missing_items.xlsx", index=False)
print(f"fact_missing_items.xlsx {len(fact_missing):>6,} rows")

print(f"\nAll files saved to  {OUT_DIR.resolve()}")
print("\n── Relationships to set in Power BI ──────────────────────────────────")
print("  fact_orders[date_key]       → dim_date[date_key]")
print("  fact_orders[region_id]      → dim_region[region_id]")
print("  fact_orders[driver_id]      → dim_driver[driver_id]")
print("  fact_orders[customer_id]    → dim_customer[customer_id]")
print("  fact_missing_items[order_id]  → fact_orders[order_id]")
print("  fact_missing_items[product_id] → dim_product[product_id]")
