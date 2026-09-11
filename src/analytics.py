"""Simple business analytics calculated from cleaned sales data."""

from __future__ import annotations

import pandas as pd


def calculate_kpis(cleaned_df: pd.DataFrame) -> dict[str, object]:
    """Calculate dashboard KPIs from cleaned sales rows."""
    total_transactions = len(cleaned_df)
    total_revenue = float(cleaned_df["revenue"].sum())
    total_units_sold = float(cleaned_df["quantity"].sum())
    average_order_value = total_revenue / total_transactions if total_transactions else 0.0

    products = product_performance(cleaned_df)
    best_selling_product = None
    highest_revenue_product = None
    if not products.empty:
        best_selling_product = products.loc[products["Units Sold"].idxmax(), "Product"]
        highest_revenue_product = products.loc[products["Revenue"].idxmax(), "Product"]

    return {
        "Total Revenue": total_revenue,
        "Total Transactions": total_transactions,
        "Total Units Sold": total_units_sold,
        "Unique Customers": int(cleaned_df["customer"].nunique()),
        "Average Order Value": average_order_value,
        "Best Selling Product": best_selling_product,
        "Highest Revenue Product": highest_revenue_product,
    }


def product_performance(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Return product-level sales metrics sorted by revenue."""
    columns = [
        "Product", "Category", "Units Sold", "Number of Transactions", "Revenue", "Average Selling Price"
    ]
    if cleaned_df.empty:
        return pd.DataFrame(columns=columns)

    performance = (
        cleaned_df.groupby(["product", "category"], dropna=False)
        .agg(
            **{
                "Units Sold": ("quantity", "sum"),
                "Number of Transactions": ("product", "size"),
                "Revenue": ("revenue", "sum"),
                "Average Selling Price": ("unit_price", "mean"),
            }
        )
        .reset_index()
        .rename(columns={"product": "Product", "category": "Category"})
        .sort_values("Revenue", ascending=False, kind="stable")
        .reset_index(drop=True)
    )
    return performance[columns]


def monthly_analytics(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Return monthly orders, units, and revenue sorted by month."""
    columns = ["Month", "Transactions", "Units Sold", "Revenue"]
    if cleaned_df.empty:
        return pd.DataFrame(columns=columns)

    monthly_data = cleaned_df.copy()
    monthly_data["month"] = pd.to_datetime(monthly_data["date"]).dt.to_period("M")
    monthly = (
        monthly_data.groupby("month")
        .agg(
            Transactions=("product", "size"),
            **{"Units Sold": ("quantity", "sum"), "Revenue": ("revenue", "sum")},
        )
        .reset_index()
        .rename(columns={"month": "Month"})
    )
    monthly["Month"] = monthly["Month"].astype(str)
    return monthly[columns]
