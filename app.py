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
    df = pd.read_csv("Startup.csv")

    # Standardize column names
    df.rename(columns={
        "Date dd/mm/yyyy": "Date", "City  Location": "City", "Investors Name": "Investors",
        "Startup Name": "Startup", "Industry Vertical": "Industry", "SubVertical": "SubIndustry",
        "Amount in USD": "AmountUSD", "InvestmentnType": "InvestmentType"
    }, inplace=True)

    # Clean 'AmountUSD'
    df["AmountUSD"] = pd.to_numeric(df["AmountUSD"].str.replace(",", ""), errors='coerce')

    # Format 'Date'
    df["Date"] = pd.to_datetime(
        df["Date"].str.replace('.', '-', regex=False).str.replace('/', '-', regex=False),
        errors='coerce'
    )

    # Clean investment type
    df["InvestmentType"] = df["InvestmentType"].replace({
        "SeedFunding": "Seed Funding", "PrivateEquity": "Private Equity",
        "Seed/ Angel Funding": "Seed Funding", "Seed/Angel Funding": "Seed Funding"
    })

    # Drop missing values
    df.dropna(subset=["Date", "Startup", "Industry", "SubIndustry", "City", "AmountUSD", "Investors", "InvestmentType"], inplace=True)

    # Feature engineering
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
    total_funding = filtered_df["AmountUSD"].sum()
    num_deals = len(filtered_df)
    avg_ticket_size = filtered_df["AmountUSD"].mean()

    st.markdown("### Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Funding", f"${total_funding/1e9:.2f}B")
    col2.metric("Number of Deals", f"{num_deals}")
    col3.metric("Average Deal Size", f"${avg_ticket_size/1e6:.2f}M")
    st.markdown("---")

    # --- VISUAL INSIGHTS 2x3 MATRIX ---
    st.header("📊 Visual Insights")

    # ROW 1
    row1 = st.columns(3)

    with row1[0]:
        st.subheader("🏆 Top Startups")
        top_startups = filtered_df.groupby("Startup")["AmountUSD"].sum().nlargest(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(y=top_startups.index, x=top_startups.values, palette="viridis", ax=ax)
        ax.set_xlabel("Total Funding (USD)")
        ax.set_ylabel(None)
        st.pyplot(fig)

    with row1[1]:
        st.subheader("🤝 Top Investors")
        investor_df = filtered_df.copy()
        investor_df["Investors"] = investor_df["Investors"].str.split(', ')
        investor_df = investor_df.explode("Investors")
        investor_df = investor_df[~investor_df["Investors"].isin(["Undisclosed Investors", ""])]
        top_investors = investor_df.groupby("Investors")["AmountUSD"].sum().nlargest(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(y=top_investors.index, x=top_investors.values, palette="plasma", ax=ax)
        ax.set_xlabel("Total Investment (USD)")
        ax.set_ylabel(None)
        st.pyplot(fig)

    with row1[2]:
        st.subheader("🏙️ Top Cities by Funding")
        top_cities = filtered_df.groupby("City")["AmountUSD"].sum().nlargest(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(y=top_cities.index, x=top_cities.values, palette="coolwarm", ax=ax)
        ax.set_xlabel("Total Funding (USD)")
        ax.set_ylabel(None)
        st.pyplot(fig)

    # ROW 2
    row2 = st.columns(3)

    with row2[0]:
        st.subheader("📈 Monthly Funding Trend")
        monthly_funding = filtered_df.groupby("Month")["AmountUSD"].sum()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.lineplot(x=monthly_funding.index, y=monthly_funding.values, marker='o', color='purple', ax=ax)
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Funding (USD)")
        ax.set_xticks(range(1, 13))
        st.pyplot(fig)

    with row2[1]:
        st.subheader("💰 Funding by Investment Type")
        investment_dist = filtered_df["InvestmentType"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(investment_dist.values, labels=investment_dist.index, autopct='%1.1f%%',
               startangle=90, colors=sns.color_palette("Set2"), textprops={'fontsize': 8})
        ax.axis('equal')
        st.pyplot(fig)

    with row2[2]:
        st.subheader("🏭 Top Sub-Industries")
        top_sub_industries = filtered_df.groupby("SubIndustry")["AmountUSD"].sum().nlargest(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(y=top_sub_industries.index, x=top_sub_industries.values, palette="rocket", ax=ax)
        ax.set_xlabel("Total Funding (USD)")
        ax.set_ylabel(None)
        st.pyplot(fig)
