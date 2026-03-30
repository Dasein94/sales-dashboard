"""
analyze.py — reads sales.csv and writes summary JSON files to output/

Run with:
    python analyze.py
"""

import json
import pathlib

import pandas as pd


# ── File paths ────────────────────────────────────────────────────────────────
DATA_FILE  = pathlib.Path("data/sales.csv")
OUTPUT_DIR = pathlib.Path("output")


def load_data() -> pd.DataFrame:
    """Read the CSV file and return it as a DataFrame.

    parse_dates=["date"] tells pandas to convert the date column from a
    plain string into a proper datetime object, which unlocks .dt operations
    later (e.g. extracting the month).
    """
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    print(f"Loaded {len(df)} rows from {DATA_FILE}")
    return df


def compute_summary(df: pd.DataFrame) -> dict:
    """Compute overall totals and identify the top product and region.

    Key operations:
    - .sum()    — adds up all values in a column
    - .groupby() — splits the data into groups (one per product or region)
    - .idxmax() — returns the *label* (name) of the group with the highest value
    """
    total_revenue = round(df["revenue"].sum(), 2)
    total_units   = int(df["units_sold"].sum())

    # Group all rows by product, sum their revenue, then find the top name
    top_product = df.groupby("product")["revenue"].sum().idxmax()

    # Same pattern for region
    top_region  = df.groupby("region")["revenue"].sum().idxmax()

    return {
        "total_revenue": total_revenue,
        "total_units":   total_units,
        "top_product":   top_product,
        "top_region":    top_region,
    }


def compute_monthly_revenue(df: pd.DataFrame) -> list[dict]:
    """Return total revenue per calendar month, sorted oldest to newest.

    Key operations:
    - .dt.to_period("M") — converts a full date like 2024-03-15 to just "2024-03"
    - .astype(str)       — converts the Period object to a plain string for JSON
    - .reset_index()     — after groupby, the group labels become an index column;
                           reset_index() turns them back into a regular column
    - to_dict("records") — converts the DataFrame to a list of dicts:
                           [{"month": "2024-01", "revenue": 1234.56}, ...]
                           This format is exactly what Chart.js expects.
    """
    df = df.copy()  # avoid modifying the original DataFrame
    df["month"] = df["date"].dt.to_period("M").astype(str)

    monthly = (
        df.groupby("month")["revenue"]
        .sum()
        .round(2)
        .reset_index()
        .sort_values("month")  # sort chronologically (strings sort correctly here)
    )

    return monthly.to_dict(orient="records")


def compute_revenue_by_product(df: pd.DataFrame) -> list[dict]:
    """Return total revenue per product, sorted highest to lowest."""
    by_product = (
        df.groupby("product")["revenue"]
        .sum()
        .round(2)
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    return by_product.to_dict(orient="records")


def compute_revenue_by_region(df: pd.DataFrame) -> list[dict]:
    """Return total revenue per region, sorted highest to lowest."""
    by_region = (
        df.groupby("region")["revenue"]
        .sum()
        .round(2)
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    return by_region.to_dict(orient="records")


def write_json(data: dict | list, filename: str) -> None:
    """Write a Python object to output/<filename> as formatted JSON.

    indent=2 makes the file human-readable (pretty-printed).
    """
    path = OUTPUT_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {path}")


def main():
    # Create the output directory if it doesn't exist yet
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = load_data()

    write_json(compute_summary(df),             "summary.json")
    write_json(compute_monthly_revenue(df),     "monthly_revenue.json")
    write_json(compute_revenue_by_product(df),  "revenue_by_product.json")
    write_json(compute_revenue_by_region(df),   "revenue_by_region.json")

    print("\nDone. Check the output/ folder.")


if __name__ == "__main__":
    main()
