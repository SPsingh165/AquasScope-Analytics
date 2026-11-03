import matplotlib.pyplot as plt
import numpy as np

BACKGROUND = "#102338"
TEXT = "#e8f5fc"
CYAN = "#31cbbb"
BLUE = "#4d9ce5"


def style_chart(ax, title, ylabel=""):
    fig = ax.figure

    fig.patch.set_facecolor(BACKGROUND)
    ax.set_facecolor(BACKGROUND)

    ax.set_title(
        title,
        color=TEXT,
        fontsize=15,
        fontweight="bold",
        pad=16
    )

    ax.set_ylabel(ylabel, color=TEXT)
    ax.tick_params(colors=TEXT)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(
        axis="y",
        color="#345066",
        alpha=0.35
    )

    ax.set_axisbelow(True)

    return fig


def ranking_chart(df, column, title, count=10):
    top = (
        df.dropna(subset=[column])
        .nlargest(count, column)
        .sort_values(column)
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.barh(
        top["area_name"],
        top[column],
        color=CYAN,
        height=0.65
    )

    style_chart(ax, title)
    ax.set_xlabel(column.replace("_", " ").title(), color=TEXT)

    fig.tight_layout()
    return fig


def connection_chart(df):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.scatter(
        df["connections"],
        df["consumption_ml"],
        color=CYAN,
        alpha=0.8,
        s=55
    )

    style_chart(
        ax,
        "Water Connections vs Consumption",
        "Reported Consumption (ML)"
    )

    ax.set_xlabel("Connections", color=TEXT)

    fig.tight_layout()
    return fig


def chennai_comparison_chart(df):
    fig, ax = plt.subplots(figsize=(11, 5))

    x = np.arange(len(df))
    width = 0.38

    ax.bar(
        x - width / 2,
        df["capacity_litres_per_day"] / 1e6,
        width,
        color=BLUE,
        label="Supply capacity"
    )

    ax.bar(
        x + width / 2,
        df["daily_consumption_ml"],
        width,
        color=CYAN,
        label="Domestic consumption"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        df["area_name"],
        rotation=45,
        ha="right"
    )

    style_chart(
        ax,
        "Supply Capacity vs Domestic Consumption",
        "Million Litres per Day"
    )

    ax.legend(
        facecolor=BACKGROUND,
        labelcolor=TEXT,
        edgecolor="#345066"
    )

    fig.tight_layout()
    return fig


def coverage_chart(df):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(
        df["area_name"],
        df["network_coverage_pct"],
        color=BLUE
    )

    style_chart(
        ax,
        "Water Supply Network Coverage",
        "Coverage (%)"
    )

    ax.set_ylim(0, 105)
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    return fig
