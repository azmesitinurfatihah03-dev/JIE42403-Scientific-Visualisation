
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Scientific Visualisation",
    page_icon="📊",
    layout="wide"
)

sns.set_theme(style="whitegrid")

@st.cache_data
def load_data():
    maternal = pd.read_csv("death_maternal_state.csv")
    life = pd.read_csv("life_expectancy_state_ethnic.csv")
    income = pd.read_csv("hies_state_percentile.csv")

    maternal["date"] = pd.to_datetime(maternal["date"], errors="coerce")
    maternal["rate"] = pd.to_numeric(maternal["rate"], errors="coerce")
    maternal = maternal.dropna(subset=["state", "date", "rate"])
    maternal["year"] = maternal["date"].dt.year

    life["date"] = pd.to_datetime(life["date"], errors="coerce")
    life["life_expectancy"] = pd.to_numeric(life["life_expectancy"], errors="coerce")
    life = life.dropna(subset=["state", "date", "sex", "ethnicity", "life_expectancy"])

    income["date"] = pd.to_datetime(income["date"], errors="coerce")
    income["income"] = pd.to_numeric(income["income"], errors="coerce")
    income["percentile"] = pd.to_numeric(income["percentile"], errors="coerce")
    income = income.dropna(subset=["date", "state", "percentile", "variable", "income"])

    return maternal, life, income


maternal, life, income = load_data()

st.title("Scientific Visualisation Dashboard")
st.subheader("Maternal Death, Life Expectancy and Household Income in Malaysia")

st.write(
    "This dashboard presents three research objectives "
    "using Malaysian health and socioeconomic datasets."
)

st.sidebar.title("Dashboard Navigation")

page = st.sidebar.radio(
    "Select Objective",
    [
        "Overview",
        "Objective 1: Maternal Death",
        "Objective 2: Life Expectancy",
        "Objective 3: Household Income"
    ]
)

if page == "Overview":

    st.header("Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Datasets", "3")
    col2.metric("Research Objectives", "3")
    col3.metric("Visualisations", "3")

    st.subheader("Research Objectives")

    st.markdown("""
    **Objective 1: Maternal Death**

    To examine the distribution and changes in maternal death
    rates across different states in Malaysia from 2000 to 2025.

    **Objective 2: Life Expectancy**

    To compare the average life expectancy among different
    ethnic groups across Malaysian states in 2026.

    **Objective 3: Household Income**

    To analyse the distribution of average household income
    across different income percentiles in Malaysia in 2024.
    """)


elif page == "Objective 1: Maternal Death":

    st.header("Objective 1: Maternal Death")

    years = st.slider(
        "Select Year Range",
        int(maternal["year"].min()),
        int(maternal["year"].max()),
        (int(maternal["year"].min()), int(maternal["year"].max()))
    )

    data = maternal[maternal["year"].between(years[0], years[1])]

    avg = data["rate"].mean()
    highest = data.loc[data["rate"].idxmax()]
    lowest = data.loc[data["rate"].idxmin()]

    c1, c2, c3 = st.columns(3)

    c1.metric("Average Rate", f"{avg:.2f}")
    c2.metric("Highest Rate", f"{highest['rate']:.2f}")
    c3.metric("Lowest Rate", f"{lowest['rate']:.2f}")

    pivot = data.pivot_table(
        index="state",
        columns="year",
        values="rate",
        aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=(15, 8))

    sns.heatmap(
        pivot,
        cmap="YlOrRd",
        linewidths=0.3,
        ax=ax,
        cbar_kws={"label": "Maternal Death Rate"}
    )

    ax.set_title("Maternal Death Rate Across Malaysian States")
    ax.set_xlabel("Year")
    ax.set_ylabel("State")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Interpretation and Discussion")

    st.write(
        f"The average maternal death rate was {avg:.2f} "
        f"for the selected period."
    )

    st.write(
        f"The highest recorded rate was {highest['rate']:.2f} "
        f"in {highest['state']} in {int(highest['year'])}."
    )

    st.write(
        f"The lowest recorded rate was {lowest['rate']:.2f} "
        f"in {lowest['state']} in {int(lowest['year'])}."
    )

    st.write(
        "The heatmap illustrates variations in maternal death "
        "rates across states and years."
    )


elif page == "Objective 2: Life Expectancy":

    st.header("Objective 2: Life Expectancy")

    available_years = sorted(life["date"].dt.year.unique())

    selected_year = st.selectbox(
        "Select Year",
        available_years,
        index=available_years.index(2026) if 2026 in available_years else len(available_years)-1
    )

    ethnic_labels = {
        "bumi_malay": "Bumiputera Malay",
        "bumi_other": "Bumiputera Other",
        "chinese": "Chinese",
        "indian": "Indian"
    }

    data = life[
        (life["date"].dt.year == selected_year) &
        (life["sex"] == "both") &
        (life["ethnicity"].isin(ethnic_labels.keys()))
    ]

    if data.empty:
        st.warning("No data available for the selected year.")
    else:

        average = data.groupby("ethnicity")["life_expectancy"].mean()
        average = average.reindex(ethnic_labels.keys()).dropna()
        average.index = average.index.map(ethnic_labels)

        c1, c2, c3 = st.columns(3)

        c1.metric("Overall Average", f"{average.mean():.2f} years")
        c2.metric("Highest Group", average.idxmax())
        c3.metric("Lowest Group", average.idxmin())

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(
            average.index,
            average.values,
            edgecolor="black"
        )

        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.15,
                f"{bar.get_height():.2f}",
                ha="center"
            )

        ax.set_title("Average Life Expectancy by Ethnic Group")
        ax.set_xlabel("Ethnic Group")
        ax.set_ylabel("Life Expectancy (Years)")
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.xticks(rotation=15)
        plt.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

        st.subheader("Interpretation and Discussion")

        st.write(
            f"{average.idxmax()} recorded the highest average "
            f"life expectancy at {average.max():.2f} years."
        )

        st.write(
            f"{average.idxmin()} recorded the lowest average "
            f"life expectancy at {average.min():.2f} years."
        )

        st.write(
            f"The difference between the groups was "
            f"{average.max()-average.min():.2f} years."
        )


elif page == "Objective 3: Household Income":

    st.header("Objective 3: Household Income")

    available_years = sorted(income["date"].dt.year.unique())

    selected_year = st.selectbox(
        "Select Year",
        available_years,
        index=available_years.index(2024) if 2024 in available_years else len(available_years)-1
    )

    data = income[
        (income["date"].dt.year == selected_year) &
        (income["variable"] == "mean")
    ]

    if data.empty:
        st.warning("No data available for the selected year.")
    else:

        percentile_avg = data.groupby(
            "percentile"
        )["income"].mean().sort_index()

        c1, c2, c3 = st.columns(3)

        c1.metric("Average Income", f"RM {percentile_avg.mean():,.2f}")
        c2.metric("Highest Income", f"RM {percentile_avg.max():,.2f}")
        c3.metric("Lowest Income", f"RM {percentile_avg.min():,.2f}")

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            percentile_avg.index,
            percentile_avg.values,
            marker="o",
            linewidth=2,
            markersize=3
        )

        ax.set_title("Average Household Income by Percentile")
        ax.set_xlabel("Income Percentile")
        ax.set_ylabel("Average Household Income (RM)")
        ax.grid(True, linestyle="--", alpha=0.4)

        plt.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

        st.subheader("Interpretation and Discussion")

        st.write(
            f"Percentile {percentile_avg.idxmax()} recorded "
            f"the highest average income of "
            f"RM {percentile_avg.max():,.2f}."
        )

        st.write(
            f"Percentile {percentile_avg.idxmin()} recorded "
            f"the lowest average income of "
            f"RM {percentile_avg.min():,.2f}."
        )

        st.write(
            "The line graph illustrates changes in average "
            "household income across different percentiles."
        )

st.divider()

st.caption("JIE42403 – Scientific Visualisation")
