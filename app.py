# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# App configuration
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")
st.write("An interactive dashboard to explore funding trends in the Indian startup ecosystem.")


# --- DATA LOADING AND CLEANING ---
@st.cache_data
def load_data():
    # Load dataset
    df = pd.read_csv("Startup.csv")

    # Standardize column names
    df.rename(columns={
        "Date dd/mm/yyyy": "Date",
        "City  Location": "City",
        "Investors Name": "Investors",
        "Startup Name": "Startup",
        "Industry Vertical": "Industry",
        "SubVertical": "SubIndustry",
        "Amount in USD": "AmountUSD",
        "InvestmentnType": "InvestmentType"
    }, inplace=True)

    # Clean 'AmountUSD' column
    df["AmountUSD"] = pd.to_numeric(df["AmountUSD"].str.replace(",", ""), errors='coerce')

    # Clean and format the 'Date' column
    df["Date"] = pd.to_datetime(
        df["Date"].str.replace('.', '-', regex=False).str.replace('/', '-', regex=False),
        errors='coerce'
    )
    
    # Clean up investment type names
    df['InvestmentType'] = df['InvestmentType'].replace({
        'SeedFunding': 'Seed Funding', 'PrivateEquity': 'Private Equity',
        'Seed/ Angel Funding': 'Seed Funding', 'Seed/Angel Funding': 'Seed Funding'
    })

    # Drop rows with missing essential data
    df.dropna(subset=["Date", "Startup", "Industry", "SubIndustry", "City", "AmountUSD", "Investors", "InvestmentType"], inplace=True)

    # Feature Engineering
    df["Year"] = df["Date"].dt.year.astype(int)
    df["Month"] = df["Date"].dt.month
    return df

df = load_data()


# --- SIDEBAR FILTERS ---
st.sidebar.header("📊 Filter Options")
selected_year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True))
industry_list = ["Overall"] + sorted(df["Industry"].unique().tolist())
selected_industry = st.sidebar.selectbox("Select Industry", industry_list)
city_list = sorted(df["City"].unique().tolist())
selected_cities = st.sidebar.multiselect("Select Cities", city_list, default=["Bengaluru", "Mumbai", "New Delhi"])
investment_type_list = sorted(df["InvestmentType"].unique().tolist())
selected_investment_types = st.sidebar.multiselect("Select Investment Types", investment_type_list, default=investment_type_list)
min_amount, max_amount = st.sidebar.slider(
    "Select Funding Amount Range (USD)", 0, int(df["AmountUSD"].max()), (0, int(df["AmountUSD"].max()))
)


# --- FILTERING LOGIC ---
filtered_df = df[
    (df["Year"] == selected_year) &
    (df["City"].isin(selected_cities)) &
    (df["InvestmentType"].isin(selected_investment_types)) &
    (df["AmountUSD"].between(min_amount, max_amount))
]
if selected_industry != "Overall":
    filtered_df = filtered_df[filtered_df["Industry"] == selected_industry]


# --- MAIN PAGE ---
st.header("Analysis Dashboard")

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
else:
    # --- KEY METRICS ---
    total_funding = filtered_df['AmountUSD'].sum()
    num_deals = len(filtered_df)
    avg_ticket_size = filtered_df['AmountUSD'].mean()
    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Funding", f"${total_funding/1e9:.2f}B")
    col2.metric("Number of Deals", f"{num_deals}")
    col3.metric("Average Deal Size", f"${avg_ticket_size/1e6:.2f}M")
    st.markdown("---")

    # --- VISUALIZATION GRIDS ---
    st.header("📊 Top Rankings")
    row1_col1, row1_col2 = st.columns(2)
    
    # CHART 1: Top Startups
    with row1_col1:
        st.subheader("🏆 Top 10 Startups")
        top_startups = filtered_df.groupby("Startup")["AmountUSD"].sum().nlargest(10)
        fig1, ax1 = plt.subplots()
        sns.barplot(y=top_startups.index, x=top_startups.values, palette="viridis", ax=ax1)
        ax1.set_xlabel("Total Funding (USD)")
        ax1.set_ylabel(None)
        st.pyplot(fig1)

    # CHART 2: Top Investors
    with row1_col2:
        st.subheader("🤝 Top 10 Investors")
        investor_df = filtered_df.copy()
        investor_df["Investors"] = investor_df["Investors"].str.split(', ')
        investor_df = investor_df.explode("Investors")
        investor_df = investor_df[~investor_df["Investors"].isin(["Undisclosed Investors", ""])]
        top_investors = investor_df.groupby("Investors")["AmountUSD"].sum().nlargest(10)
        fig2, ax2 = plt.subplots()
        sns.barplot(y=top_investors.index, x=top_investors.values, palette="plasma", ax=ax2)
        ax2.set_xlabel("Total Amount Invested (USD)")
        ax2.set_ylabel(None)
        st.pyplot(fig2)

    st.header("📊 Deeper Insights")
    row2_col1, row2_col2 = st.columns(2)

    # CHART 3: Top Sub-Industries
    with row2_col1:
        st.subheader("🏭 Top 10 Sub-Industries")
        top_sub_industries = filtered_df.groupby("SubIndustry")["AmountUSD"].sum().nlargest(10)
        fig3, ax3 = plt.subplots()
        sns.barplot(y=top_sub_industries.index, x=top_sub_industries.values, palette="coolwarm", ax=ax3)
        ax3.set_xlabel("Total Funding (USD)")
        ax3.set_ylabel(None)
        st.pyplot(fig3)

    # CHART 4: Funding Amount Distribution
    with row2_col2:
        st.subheader("Histogram of Funding Amounts")
        fig4, ax4 = plt.subplots()
        sns.histplot(filtered_df["AmountUSD"], bins=30, kde=True, log_scale=True, ax=ax4, color="green")
        ax4.set_xlabel("Funding Amount (USD) - Log Scale")
        ax4.set_ylabel("Number of Deals")
        st.pyplot(fig4)

    # --- FULL-WIDTH HEATMAP ---
    st.header("📅 Year vs. Month Funding Heatmap")
    st.write("This heatmap shows the total funding amount across all years and is independent of the filters above.")
    
    heatmap_data = df.pivot_table(index="Month", columns="Year", values="AmountUSD", aggfunc='sum')
    fig5, ax5 = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax5, cbar_kws={'label': 'Funding Amount (USD)'})
    ax5.set_title("Total Funding Amount per Month and Year")
    st.pyplot(fig5)
