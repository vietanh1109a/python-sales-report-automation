import pandas as pd

from src.analytics import calculate_kpis, monthly_analytics, product_performance


def make_cleaned_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-10", "2026-01-20", "2026-02-02"]),
            "product": ["Keyboard", "Mouse", "Keyboard"],
            "category": ["Accessories", "Accessories", "Accessories"],
            "quantity": [2, 4, 1],
            "unit_price": [30.0, 20.0, 30.0],
            "customer": ["Ana", "Ben", "Ana"],
            "revenue": [60.0, 80.0, 30.0],
        }
    )


def test_calculate_kpis_returns_expected_values() -> None:
    kpis = calculate_kpis(make_cleaned_data())

    assert kpis["Total Revenue"] == 170.0
    assert kpis["Total Transactions"] == 3
    assert kpis["Total Units Sold"] == 7.0
    assert kpis["Unique Customers"] == 2
    assert round(kpis["Average Transaction Value"], 2) == 56.67
    assert kpis["Best Selling Product"] == "Mouse"
    assert kpis["Highest Revenue Product"] == "Keyboard"


def test_product_performance_aggregates_products() -> None:
    performance = product_performance(make_cleaned_data())

    keyboard = performance.loc[performance["Product"] == "Keyboard"].iloc[0]
    assert keyboard["Units Sold"] == 3
    assert keyboard["Number of Transactions"] == 2
    assert keyboard["Revenue"] == 90.0
    assert keyboard["Average Selling Price"] == 30.0


def test_monthly_analytics_aggregates_each_month() -> None:
    monthly = monthly_analytics(make_cleaned_data())

    january = monthly.loc[monthly["Month"] == "2026-01"].iloc[0]
    assert january["Transactions"] == 2
    assert january["Units Sold"] == 6
    assert january["Revenue"] == 140.0
