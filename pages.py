import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from components.charts import (
    ranking_chart,
    connection_chart,
    chennai_comparison_chart,
    coverage_chart,
)


def show_chart(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def download_csv(df, label, filename):
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def overview(bengaluru, chennai, combined):
    st.subheader("Executive Overview")

    st.caption(
        "Explore consumption records, regional patterns "
        "and integrated water data."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Indian Cities", "02")
    c2.metric("Bengaluru Ward Records", len(bengaluru))
    c3.metric("Chennai Zones", len(chennai))
    c4.metric("Integrated Records", len(combined))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("### Bengaluru")

        st.metric(
            "Reported Water Consumption",
            f"{bengaluru['consumption_ml'].sum():,.2f} ML",
        )

        st.caption("Reporting duration not verified.")

        fig = ranking_chart(
            bengaluru,
            "consumption_ml",
            "Highest-Consuming Ward Records",
            min(7, len(bengaluru)),
        )
        show_chart(fig)

    with right:
        st.markdown("### Chennai")

        st.metric(
            "Domestic Water Consumption",
            f"{chennai['daily_consumption_ml'].sum():,.2f} ML/day",
        )

        st.caption(
            "Reported daily consumption as of January 2019."
        )

        fig = ranking_chart(
            chennai,
            "daily_consumption_ml",
            "Highest-Consuming Zones",
            min(7, len(chennai)),
        )
        show_chart(fig)

    st.divider()

    st.markdown("### Data Integration Workflow")

    st.info(
        "Original CSV Datasets → Pandas Preprocessing → "
        "Cleaned CSV Files → Combined Dataset → "
        "Streamlit Dashboard"
    )

    st.caption(
        "Bengaluru and Chennai have different reporting "
        "periods. Their consumption totals must not be "
        "directly compared as equivalent daily rates."
    )


def bengaluru_page(df):
    st.subheader("Bengaluru Water Analytics")

    if df.empty:
        st.warning("No Bengaluru records available.")
        return

    ward_names = sorted(
        df["area_name"].dropna().astype(str).unique().tolist()
    )

    selected_wards = st.multiselect(
        "Select Bengaluru wards",
        options=ward_names,
        default=ward_names,
        key="bengaluru_wards",
    )

    filtered = df[
        df["area_name"].isin(selected_wards)
    ].copy()

    if filtered.empty:
        st.warning("Select at least one ward.")
        return

    a, b, c = st.columns(3)

    a.metric(
        "Reported Consumption",
        f"{filtered['consumption_ml'].sum():,.2f} ML",
    )

    b.metric(
        "Water Connections",
        f"{filtered['connections'].sum():,.0f}",
    )

    c.metric("Selected Ward Records", len(filtered))

    st.divider()

    max_records = min(30, len(filtered))

    top_count = st.slider(
        "Number of records",
        min_value=1,
        max_value=max_records,
        value=min(10, max_records),
        key="bengaluru_top_count",
    )

    metric = st.radio(
        "Choose visualization",
        options=[
            "consumption_ml",
            "connections",
            "litres_per_connection",
        ],
        format_func=lambda x: {
            "consumption_ml": "Reported Consumption (ML)",
            "connections": "Water Connections",
            "litres_per_connection":
                "Litres per Connection",
        }[x],
        horizontal=True,
        key="bengaluru_metric",
    )

    fig = ranking_chart(
        filtered,
        metric,
        "Bengaluru Ward Ranking",
        top_count,
    )
    show_chart(fig)

    st.subheader("Connections vs Consumption")

    fig = connection_chart(filtered)
    show_chart(fig)

    st.subheader("Explore Ward Records")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )

    download_csv(
        filtered,
        "Download Selected Bengaluru Data",
        "selected_bengaluru_data.csv",
    )

    st.caption(
        "Repeated ward numbers are retained because "
        "their records may differ. The reporting "
        "duration has not been verified."
    )


def chennai_page(df):
    st.subheader("Chennai Water Analytics")

    if df.empty:
        st.warning("No Chennai records available.")
        return

    zone_names = sorted(
        df["area_name"].dropna().astype(str).unique().tolist()
    )

    selected_zones = st.multiselect(
        "Select Chennai zones",
        options=zone_names,
        default=zone_names,
        key="chennai_zones",
    )

    filtered = df[
        df["area_name"].isin(selected_zones)
    ].copy()

    if filtered.empty:
        st.warning("Select at least one zone.")
        return

    a, b, c = st.columns(3)

    a.metric("Selected Zones", len(filtered))

    b.metric(
        "Domestic Consumption",
        f"{filtered['daily_consumption_ml'].sum():,.2f} ML/day",
    )

    c.metric(
        "Average Network Coverage",
        f"{filtered['network_coverage_pct'].mean():.1f}%",
    )

    st.divider()

    max_records = min(30, len(filtered))

    top_count = st.slider(
        "Number of records",
        min_value=1,
        max_value=max_records,
        value=min(10, max_records),
        key="chennai_top_count",
    )

    chart_type = st.radio(
        "Choose visualization",
        [
            "Zone Consumption",
            "Capacity Comparison",
            "Network Coverage",
        ],
        horizontal=True,
        key="chennai_chart_type",
    )

    if chart_type == "Zone Consumption":
        fig = ranking_chart(
            filtered,
            "daily_consumption_ml",
            "Chennai Zone Consumption",
            top_count,
        )

    elif chart_type == "Capacity Comparison":
        fig = chennai_comparison_chart(filtered)

    else:
        fig = coverage_chart(filtered)

    show_chart(fig)

    st.subheader("Supply Indicators")

    flagged = filtered[
        filtered["consumption_litres"]
        > filtered["capacity_litres_per_day"]
    ]

    st.metric(
        "Zones Above Stated Supply Capacity",
        len(flagged),
    )

    st.caption(
        "This is a potential data-quality or supply "
        "pressure indicator, not proof of leakage."
    )

    st.subheader("Explore Zone Records")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )

    download_csv(
        filtered,
        "Download Selected Chennai Data",
        "selected_chennai_data.csv",
    )


def integration_page(combined):
    st.subheader("Data Integration Lab")

    st.write(
        "Explore the standardized dataset created "
        "from Bengaluru and Chennai."
    )

    city = st.radio(
        "Filter by city",
        ["All", "Bengaluru", "Chennai"],
        horizontal=True,
        key="integration_city",
    )

    if city == "All":
        filtered = combined.copy()
    else:
        filtered = combined[
            combined["city"] == city
        ].copy()

    st.metric("Filtered Records", len(filtered))

    columns = st.multiselect(
        "Choose columns to display",
        options=combined.columns.tolist(),
        default=combined.columns.tolist(),
        key="integration_columns",
    )

    if not columns:
        st.warning("Select at least one column.")
        return

    st.dataframe(
        filtered[columns],
        use_container_width=True,
        hide_index=True,
    )

    download_csv(
        filtered,
        "Download Filtered Dataset",
        "filtered_water_data.csv",
    )

    st.info(
        "Both datasets have been combined using "
        "a standardized schema. Missing fields "
        "are preserved instead of inventing values."
    )


def quality_page(bengaluru, chennai):
    st.subheader("Data Quality Center")

    city = st.radio(
        "Choose dataset",
        ["Bengaluru", "Chennai"],
        horizontal=True,
        key="quality_city",
    )

    df = (
        bengaluru
        if city == "Bengaluru"
        else chennai
    )

    a, b, c = st.columns(3)

    a.metric("Records", len(df))

    b.metric(
        "Missing Cells",
        int(df.isna().sum().sum()),
    )

    c.metric(
        "Exact Duplicate Rows",
        int(df.duplicated().sum()),
    )

    st.divider()

    st.subheader("Missing Values by Column")

    missing = df.isna().sum().reset_index()
    missing.columns = ["Column", "Missing Values"]

    st.dataframe(
        missing,
        use_container_width=True,
        hide_index=True,
    )

    if city == "Bengaluru":
        st.subheader("Repeated Ward Numbers")

        repeated = df[
            df.duplicated(
                "ward_number",
                keep=False,
            )
        ]

        st.dataframe(
            repeated,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader("Methodology")

    st.write(
        "The project reads original CSV files, "
        "cleans values using Pandas, standardizes "
        "the columns, and combines the records. "
        "The cleaned and combined datasets are "
        "saved as CSV files and displayed through "
        "the Streamlit dashboard."
    )

    st.warning(
        "These datasets do not provide a complete "
        "daily or weekly time series. Actual water "
        "wastage cannot be confirmed from them."
    )