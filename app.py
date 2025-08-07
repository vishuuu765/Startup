# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# App configuration
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")
st.write("An interactive dashboard to explore funding trends in the Indian startup ecosystem.")


# --- DATA LOADING AND CLEANING ---

# Function to load and cache the data for performance
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

    # Drop rows with missing essential data
    df.dropna(subset=["Date", "Startup", "Industry", "City", "AmountUSD", "Investors"], inplace=True)

    # Feature Engineering
    df["Year"] = df["Date"].dt.year.astype(int)
    df["Month"] = df["Date"].dt.month
    return df

df = load_data()


# --- SIDEBAR FILTERS ---
st.sidebar.header("📊 Filter Options")

# Year Filter
selected_year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True))

# Industry Filter (with an 'Overall' option)
industry_list = ["Overall"] + sorted(df["Industry"].unique().tolist())
selected_industry = st.sidebar.selectbox("Select Industry", industry_list)


# --- FILTERED DATAFRAME ---
filtered_df = df[df["Year"] == selected_year]
if selected_industry != "Overall":
    filtered_df = filtered_df[filtered_df["Industry"] == selected_industry]


# --- MAIN PAGE DISPLAY ---
st.header(f"Dashboard for {selected_industry} in {selected_year}")

# --- KEY METRICS ---
total_funding = filtered_df['AmountUSD'].sum()
num_deals = len(filtered_df)
avg_ticket_size = filtered_df['AmountUSD'].mean()
num_investors = filtered_df['Investors'].str.split(',').explode().nunique()


# Display metrics in columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Funding", f"${total_funding/1e9:.2f}B")
col2.metric("Number of Deals", f"{num_deals}")
col3.metric("Average Deal Size", f"${avg_ticket_size/1e6:.2f}M")
col4.metric("Unique Investors", f"{num_investors}")

st.markdown("---")


# --- VISUALIZATION MATRIX ---

st.header("📊 Visual Insights Matrix")

# Create a 2x2 grid for charts
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)


# CHART 1: Top 10 Funded Startups
with row1_col1:
    st.subheader("🏆 Top 10 Funded Startups")
    top_startups = (
        filtered_df.groupby("Startup")["AmountUSD"]
        .sum()
        .nlargest(10)
    )
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_startups.values, y=top_startups.index, palette="viridis", ax=ax1)
    ax1.set_xlabel("Total Funding (USD)")
    ax1.set_ylabel("Startup")
    ax1.tick_params(axis='y', labelsize=8)
    st.pyplot(fig1)


# CHART 2: Monthly Funding Trend
with row1_col2:
    st.subheader("📈 Monthly Funding Trend")
    monthly_funding = filtered_df.groupby("Month")["AmountUSD"].sum()
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.lineplot(x=monthly_funding.index, y=monthly_funding.values, marker='o', ax=ax2)
    ax2.set_xlabel("Month of the Year")
    ax2.set_ylabel("Total Funding (USD)")
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    st.pyplot(fig2)


# CHART 3: Top 10 Cities by Funding
with row2_col1:
    st.subheader("🏙️ Top 10 Cities by Funding")
    top_cities = filtered_df.groupby("City")["AmountUSD"].sum().nlargest(10)
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_cities.values, y=top_cities.index, palette="plasma", ax=ax3)
    ax3.set_xlabel("Total Funding (USD)")
    ax3.set_ylabel("City")
    ax3.tick_params(axis='y', labelsize=8)
    st.pyplot(fig3)


# CHART 4: Investment Type Distribution
with row2_col2:
    st.subheader("💰 Funding by Investment Type")
    # Clean up investment type names
    filtered_df['InvestmentType'] = filtered_df['InvestmentType'].replace({
        'SeedFunding': 'Seed Funding',
        'PrivateEquity': 'Private Equity'
    })
    investment_dist = filtered_df["InvestmentType"].value_counts()
    
    # Exclude small categories for a cleaner pie chart
    if len(investment_dist) > 6:
        others = investment_dist[6:].sum()
        investment_dist = investment_dist[:6]
        investment_dist['Others'] = others

    fig4, ax4 = plt.subplots(figsize=(10, 6))
    ax4.pie(investment_dist.values, labels=investment_dist.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set2"))
    ax4.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig4)
