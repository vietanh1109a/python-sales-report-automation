import pandas as pd
import pytest

from src.data_cleaner import clean_sales_data, get_row_accounting


def make_sales_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": ["2026-01-10", "2026-01-10", "2026-01-11", "bad-date", "2026-01-12", "2026-01-13"],
            "Product": [" Keyboard ", " Keyboard ", "Mouse", "Webcam", "Headset", "USB Hub"],
            "Category": ["Accessories"] * 6,
            "Quantity": [2, 2, 1, 1, 0, 3],
            "Unit Price": [30, 30, 20, 45, 50, -5],
            "Customer": [" Ana ", " Ana ", None, "Ben", "Cara", "Dan"],
        }
    )


def test_clean_sales_data_removes_duplicates_and_trims_text() -> None:
    cleaned, rejected = clean_sales_data(make_sales_data())

    assert len(cleaned) == 2
    assert cleaned.loc[0, "product"] == "Keyboard"
    assert rejected.shape[0] == 3


def test_get_row_accounting_counts_blank_and_duplicate_rows() -> None:
    data = make_sales_data()
    data.loc[len(data)] = [None, None, None, None, None, None]

    assert get_row_accounting(data) == {
        "Blank rows removed": 1,
        "Duplicates removed": 1,
    }


def test_clean_sales_data_replaces_missing_customer() -> None:
    cleaned, _ = clean_sales_data(make_sales_data())

    assert cleaned.loc[cleaned["product"] == "Mouse", "customer"].item() == "Unknown"


@pytest.mark.parametrize(
    ("product", "expected_reason"),
    [("Headset", "Invalid quantity"), ("USB Hub", "Invalid unit price")],
)
def test_clean_sales_data_rejects_invalid_numeric_values(product: str, expected_reason: str) -> None:
    _, rejected = clean_sales_data(make_sales_data())

    reason = rejected.loc[rejected["product"] == product, "rejection_reason"].item()
    assert expected_reason in reason


def test_clean_sales_data_calculates_revenue() -> None:
    cleaned, _ = clean_sales_data(make_sales_data())

    keyboard_revenue = cleaned.loc[cleaned["product"] == "Keyboard", "revenue"].item()
    assert keyboard_revenue == 60


def test_clean_sales_data_requires_all_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        clean_sales_data(pd.DataFrame({"Date": ["2026-01-10"]}))
