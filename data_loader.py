from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"


@st.cache_data(show_spinner=False)
def load_csv_data():

    files = {
        "Bengaluru": "bengaluru_cleaned.csv",
        "Chennai": "chennai_cleaned.csv",
        "Combined": "combined_water_data.csv",
    }

    loaded_data = {}

    for name, filename in files.items():

        file_path = PROCESSED_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing processed file: {file_path}"
            )

        df = pd.read_csv(file_path)

        loaded_data[name] = df

    bengaluru = loaded_data["Bengaluru"]
    chennai = loaded_data["Chennai"]
    combined = loaded_data["Combined"]

    return bengaluru, chennai, combined