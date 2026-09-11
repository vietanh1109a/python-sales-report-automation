"""Command-line entry point for Python Sales Report Automation."""

import argparse
from pathlib import Path

import pandas as pd

from src.analytics import calculate_kpis, monthly_analytics, product_performance
from src.data_cleaner import clean_sales_data, get_row_accounting
from src.report_generator import generate_excel_report


def parse_arguments() -> argparse.Namespace:
    """Read optional input and output paths from the command line."""
    parser = argparse.ArgumentParser(description="Create an Excel sales report from a CSV file.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_sales.csv"), help="Path to the input CSV file.")
    parser.add_argument("--output", type=Path, default=Path("output/sales_report.xlsx"), help="Path for the Excel report.")
    return parser.parse_args()


def main() -> int:
    """Load a CSV file, clean it, calculate analytics, and save an Excel report."""
    args = parse_arguments()
    if not args.input.is_file():
        print(f"Error: input file not found: {args.input}")
        return 1

    try:
        raw_data = pd.read_csv(args.input)
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        print(f"Error: could not read CSV file: {error}")
        return 1

    try:
        row_accounting = get_row_accounting(raw_data)
        cleaned_data, rejected_rows = clean_sales_data(raw_data)
    except ValueError as error:
        print(f"Error: {error}")
        return 1
    kpis = calculate_kpis(cleaned_data)
    products = product_performance(cleaned_data)
    monthly = monthly_analytics(cleaned_data)
    generate_excel_report(args.output, cleaned_data, rejected_rows, kpis, products, monthly)

    print("Sales report generated successfully.")
    print(f"Input rows: {len(raw_data)}")
    print(f"Blank rows removed: {row_accounting['Blank rows removed']}")
    print(f"Duplicates removed: {row_accounting['Duplicates removed']}")
    print(f"Rejected rows: {len(rejected_rows)}")
    print(f"Valid rows: {len(cleaned_data)}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
