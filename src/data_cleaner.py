"""Functions for preparing raw sales data for reporting."""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {"date", "product", "category", "quantity", "unit_price", "customer"}


def _normalise_column_name(name: object) -> str:
    """Return a consistent snake_case column name."""
    return str(name).strip().lower().replace(" ", "_")


def _trim_text_values(data: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace from text cells without changing numeric cells."""
    for column in data.select_dtypes(include="object").columns:
        data[column] = data[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    return data


def get_row_accounting(df: pd.DataFrame) -> dict[str, int]:
    """Count blank and duplicate rows using the same preparation as cleaning."""
    data = df.copy()
    data.columns = [_normalise_column_name(column) for column in data.columns]
    data = _trim_text_values(data)

    blank_rows_removed = int(data.isna().all(axis=1).sum())
    non_blank_data = data.dropna(how="all")
    duplicates_removed = int(non_blank_data.duplicated().sum())
    return {
        "Blank rows removed": blank_rows_removed,
        "Duplicates removed": duplicates_removed,
    }


def clean_sales_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Clean sales rows and return valid rows plus invalid rows with reasons.

    The returned valid data uses the canonical columns ``date``, ``product``,
    ``category``, ``quantity``, ``unit_price``, ``customer``, and ``revenue``.
    Invalid rows are kept in the second DataFrame and include
    ``rejection_reason`` for use in a report.
    """
    data = df.copy()
    data.columns = [_normalise_column_name(column) for column in data.columns]

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        names = ", ".join(sorted(missing_columns))
        raise ValueError(f"Input data is missing required columns: {names}")

    data = _trim_text_values(data)
    data = data.dropna(how="all")
    data = data.drop_duplicates().copy()

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["quantity"] = pd.to_numeric(data["quantity"], errors="coerce")
    data["unit_price"] = pd.to_numeric(data["unit_price"], errors="coerce")

    missing_product = data["product"].isna() | data["product"].eq("")
    invalid_date = data["date"].isna()
    invalid_quantity = data["quantity"].isna() | data["quantity"].le(0)
    invalid_price = data["unit_price"].isna() | data["unit_price"].lt(0)

    reasons = pd.Series("", index=data.index, dtype="object")
    checks = [
        (missing_product, "Missing product"),
        (invalid_date, "Invalid date"),
        (invalid_quantity, "Invalid quantity"),
        (invalid_price, "Invalid unit price"),
    ]
    for failed_rows, reason in checks:
        reasons = reasons.mask(failed_rows & reasons.eq(""), reason)
        reasons = reasons.mask(failed_rows & reasons.ne("") & ~reasons.str.contains(reason), reasons + "; " + reason)

    rejected_rows = data.loc[reasons.ne("")].copy()
    rejected_rows["rejection_reason"] = reasons.loc[rejected_rows.index]

    cleaned_data = data.loc[reasons.eq("")].copy()
    cleaned_data["customer"] = cleaned_data["customer"].fillna("").replace("", "Unknown")
    cleaned_data["revenue"] = cleaned_data["quantity"] * cleaned_data["unit_price"]

    return cleaned_data.reset_index(drop=True), rejected_rows.reset_index(drop=True)
