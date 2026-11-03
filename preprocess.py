from pathlib import Path
import pandas as pd

# Project folders
BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)

BENGALURU_FILE = RAW / "Water_Consumption_Data_Mar_26_0.csv"
CHENNAI_FILE = RAW / "WaterConsumptionChennaiason31Jan2019.csv"


def clean_bengaluru():
    print("Cleaning Bengaluru dataset...")

    df = pd.read_csv(BENGALURU_FILE)

    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Ward number": "ward_number",
        "Ward Name": "area_name",
        "Number of Connections": "connections",
        "Consumption in ML": "consumption_ml"
    })

    df["area_name"] = df["area_name"].astype("string").str.strip()

    for col in ["ward_number", "connections", "consumption_ml"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove only exact duplicate rows.
    df = df.drop_duplicates()

    # Remove rows without essential measurements.
    df = df.dropna(subset=[
        "area_name", "ward_number",
        "connections", "consumption_ml"
    ])

    df = df[
        (df["connections"] >= 0) &
        (df["consumption_ml"] >= 0)
    ].copy()

    df["ward_number"] = df["ward_number"].astype(int)
    df["connections"] = df["connections"].astype(int)

    df["city"] = "Bengaluru"
    df["state"] = "Karnataka"
    df["area_type"] = "Ward"
    df["reporting_period"] = "Mar 2026 (filename)"
    df["period_basis"] = "Not verified"

    # ML means million litres.
    df["consumption_litres"] = df["consumption_ml"] * 1000000

    # Cannot calculate litres/day without a verified period.
    df["daily_consumption_ml"] = float("nan")

    df["capacity_litres_per_day"] = float("nan")
    df["network_coverage_pct"] = float("nan")

    df["litres_per_connection"] = df["consumption_litres"] / (
        df["connections"].replace(0, float("nan"))
    )

    df.to_csv(
        PROCESSED / "bengaluru_cleaned.csv",
        index=False
    )

    return df


def clean_chennai():
    print("Cleaning Chennai dataset...")

    df = pd.read_csv(CHENNAI_FILE)
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "City Name": "city",
        "Zone Name": "area_name",
        "Ward No.": "ward_range",
        "Water supply capacity (litres/day)":
            "capacity_litres_per_day",
        "Water usage or Domestic Water Consumption (litres/day)":
            "consumption_litres",
        "%age of Area with water supply network":
            "network_coverage_pct"
    })

    # The original Ward name column is entirely empty.
    # Chennai records represent zones, not individual wards.
    df = df.drop(columns=["Ward name"], errors="ignore")

    df["area_name"] = df["area_name"].astype("string").str.strip()
    df["ward_range"] = (
        df["ward_range"].astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    numeric_cols = [
        "capacity_litres_per_day",
        "consumption_litres",
        "network_coverage_pct"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates()

    df = df.dropna(subset=[
        "area_name", "consumption_litres"
    ])

    df = df[
        (df["consumption_litres"] >= 0) &
        (df["network_coverage_pct"].between(0, 100))
    ].copy()

    df["city"] = "Chennai"
    df["state"] = "Tamil Nadu"
    df["area_type"] = "Zone"
    df["reporting_period"] = "As on 31 Jan 2019"
    df["period_basis"] = "Litres per day"

    df["daily_consumption_ml"] = (
        df["consumption_litres"] / 1000000
    )

    # Same numeric conversion, but explicitly a daily rate.
    df["consumption_ml"] = df["daily_consumption_ml"]

    df["connections"] = float("nan")
    df["ward_number"] = float("nan")
    df["litres_per_connection"] = float("nan")

    df.to_csv(
        PROCESSED / "chennai_cleaned.csv",
        index=False
    )

    return df


def combine_datasets(bengaluru, chennai):
    print("Combining both datasets...")

    # Both datasets use the same column names.
    # Measurement periods remain separate.
    columns = [
        "city",
        "state",
        "area_type",
        "area_name",
        "ward_number",
        "reporting_period",
        "period_basis",
        "consumption_ml",
        "daily_consumption_ml",
        "connections",
        "litres_per_connection",
        "capacity_litres_per_day",
        "network_coverage_pct"
    ]

    combined = pd.concat(
        [bengaluru[columns], chennai[columns]],
        ignore_index=True
    )

    combined.to_csv(
        PROCESSED / "combined_water_data.csv",
        index=False
    )

    print("Bengaluru rows:", len(bengaluru))
    print("Chennai rows:", len(chennai))
    print("Combined rows:", len(combined))

    return combined


def main():
    bengaluru = clean_bengaluru()
    chennai = clean_chennai()
    combine_datasets(bengaluru, chennai)

    print("\nPreprocessing completed successfully!")
    print("Check the data/processed folder.")


if __name__ == "__main__":
    main()
