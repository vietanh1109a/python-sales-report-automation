"""Create a clear, client-ready Excel workbook from sales data."""

from pathlib import Path
from typing import Any

import pandas as pd


def generate_excel_report(
    output_path: Path,
    cleaned_data: pd.DataFrame,
    rejected_rows: pd.DataFrame,
    kpis: dict[str, Any],
    products: pd.DataFrame,
    monthly: pd.DataFrame,
) -> None:
    """Write the sales report and its charts to an Excel workbook."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
        workbook = writer.book
        title_format = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#FFFFFF", "bg_color": "#1F4E78"})
        section_format = workbook.add_format({"bold": True, "font_size": 12, "font_color": "#1F1F1F", "bg_color": "#D9EAF7"})
        label_format = workbook.add_format({"bold": True, "bg_color": "#EAF2F8", "border": 1})
        value_format = workbook.add_format({"border": 1, "font_size": 11})
        currency_format = workbook.add_format({"num_format": "$#,##0.00", "border": 1, "font_size": 11})
        integer_format = workbook.add_format({"num_format": "#,##0", "border": 1, "font_size": 11})
        header_format = workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#1F4E78", "border": 1})

        summary = workbook.add_worksheet("Summary")
        writer.sheets["Summary"] = summary
        summary.set_column("A:A", 28)
        summary.set_column("B:B", 20)
        summary.set_column("D:K", 14)
        summary.merge_range("A1:H1", "Python Sales Report Automation", title_format)
        summary.write("A3", "Key Performance Indicators", section_format)

        kpi_rows = [
            ("Total Revenue", kpis["Total Revenue"], currency_format),
            ("Total Transactions", kpis["Total Transactions"], integer_format),
            ("Units Sold", kpis["Total Units Sold"], integer_format),
            ("Unique Customers", kpis["Unique Customers"], integer_format),
            ("Average Order Value", kpis["Average Order Value"], currency_format),
            ("Best Selling Product", kpis["Best Selling Product"], value_format),
            ("Highest Revenue Product", kpis["Highest Revenue Product"], value_format),
        ]
        for row_index, (label, value, cell_format) in enumerate(kpi_rows, start=3):
            summary.write(row_index, 0, label, label_format)
            summary.write(row_index, 1, value, cell_format)

        cleaned_data.to_excel(writer, sheet_name="Cleaned Data", index=False)
        products.to_excel(writer, sheet_name="Product Performance", index=False)
        monthly.to_excel(writer, sheet_name="Monthly Report", index=False)
        rejected_rows.to_excel(writer, sheet_name="Rejected Rows", index=False)

        _format_data_sheet(writer, "Cleaned Data", cleaned_data, header_format)
        _format_data_sheet(writer, "Product Performance", products, header_format)
        _format_data_sheet(writer, "Monthly Report", monthly, header_format)
        _format_data_sheet(writer, "Rejected Rows", rejected_rows, header_format)

        if not products.empty:
            chart = workbook.add_chart({"type": "column"})
            chart.add_series({
                "name": "Revenue by Product",
                "categories": ["Product Performance", 1, 0, len(products), 0],
                "values": ["Product Performance", 1, 4, len(products), 4],
                "fill": {"color": "#5B9BD5"},
            })
            chart.set_title({"name": "Revenue by Product"})
            chart.set_y_axis({"name": "Revenue", "num_format": "$#,##0"})
            chart.set_legend({"none": True})
            summary.insert_chart("D3", chart, {"x_scale": 1.25, "y_scale": 1.15})

        if not monthly.empty:
            chart = workbook.add_chart({"type": "line"})
            chart.add_series({
                "name": "Monthly Revenue",
                "categories": ["Monthly Report", 1, 0, len(monthly), 0],
                "values": ["Monthly Report", 1, 3, len(monthly), 3],
                "line": {"color": "#ED7D31", "width": 2.25},
            })
            chart.set_title({"name": "Monthly Revenue Trend"})
            chart.set_y_axis({"name": "Revenue", "num_format": "$#,##0", "min": 0})
            chart.set_legend({"none": True})
            summary.insert_chart("D20", chart, {"x_scale": 1.25, "y_scale": 1.15})


def _format_data_sheet(
    writer: pd.ExcelWriter, sheet_name: str, data: pd.DataFrame, header_format: Any
) -> None:
    """Apply basic widths, headers, and number formats to a data worksheet."""
    sheet = writer.sheets[sheet_name]
    for column_index, column_name in enumerate(data.columns):
        width = max(len(str(column_name)) + 2, min(24, data[column_name].astype(str).str.len().max() + 2 if not data.empty else 12))
        sheet.set_column(column_index, column_index, width)
        sheet.write(0, column_index, column_name, header_format)
        if column_name in {"Revenue", "Unit Price", "Average Selling Price", "revenue", "unit_price"}:
            sheet.set_column(column_index, column_index, width, writer.book.add_format({"num_format": "$#,##0.00"}))
    sheet.freeze_panes(1, 0)
    if not data.empty:
        sheet.autofilter(0, 0, len(data), len(data.columns) - 1)
