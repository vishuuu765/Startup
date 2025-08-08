# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# App configuration
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")

# Load dataset
df = pd.read_csv("startup_cleaned.csv")  # Your cleaned CSV

# Data Cleaning
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Amount in USD", "City Location", "Startup Name"])

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_city = st.sidebar.selectbox("Select City", options=df["City Location"].dropna().unique())
selected_year = st.sidebar.selectbox("Select Year", options=sorted(df["Date"].dt.year.dropna().unique()))
industry_list = ["All"] + sorted(df["Industry Vertical"].dropna().unique())
selected_industry = st.sidebar.selectbox("Select Industry", options=industry_list)
amount_range = st.sidebar.slider("Select Funding Amount Range (USD)", 
                                  int(df["Amount in USD"].min()), 
                                  int(df["Amount in USD"].max()), 
                                  (int(df["Amount in USD"].min()), int(df["Amount in USD"].max())))

# Filter data
filtered_df = df[
    (df["City Location"] == selected_city) &
    (df["Date"].dt.year == selected_year) &
    (df["Amount in USD"].between(amount_range[0], amount_range[1]))
]

if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry Vertical"] == selected_industry]

# Filtered Data Preview
st.subheader("📊 Filtered Data Preview")
st.write(filtered_df.head())

# Show Raw Data (Full Filtered Data)
if st.checkbox("Show Full Filtered Data"):
    st.dataframe(filtered_df)

# Layout: 2x2 grid
col1, col2 = st.columns(2)

# 1️⃣ Top 10 Funded Startups
with col1:
    st.subheader(f"Top 10 Funded Startups in {selected_city} ({selected_year})")
    top_startups = (
        filtered_df.groupby("Startup Name")["Amount in USD"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig1, ax1 = plt.subplots()
    sns.barplot(data=top_startups, x="Amount in USD", y="Startup Name", palette="Set3", ax=ax1)
    st.pyplot(fig1)

# 2️⃣ Top 10 Investors
with col2:
    st.subheader(f"Top 10 Investors in {selected_city} ({selected_year})")
    top_investors = (
        filtered_df.groupby("Investors Name")["Amount in USD"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig2, ax2 = plt.subplots()
    sns.barplot(data=top_investors, x="Amount in USD", y="Investors Name", palette="Set2", ax=ax2)
    st.pyplot(fig2)

# 3️⃣ Monthly Funding Trend
with col1:
    st.subheader(f"Monthly Funding Trend in {selected_city} ({selected_year})")
    monthly_trend = (
        filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Amount in USD"]
        .sum()
        .reset_index()
    )
    monthly_trend["Date"] = monthly_trend["Date"].astype(str)
    fig3, ax3 = plt.subplots()
    sns.lineplot(data=monthly_trend, x="Date", y="Amount in USD", marker="o", ax=ax3)
    plt.xticks(rotation=45)
    st.pyplot(fig3)

# 4️⃣ Funding by Industry
with col2:
    st.subheader(f"Funding Distribution by Industry in {selected_city} ({selected_year})")
    industry_funding = (
        filtered_df.groupby("Industry Vertical")["Amount in USD"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig4, ax4 = plt.subplots()
    sns.barplot(data=industry_funding, x="Amount in USD", y="Industry Vertical", palette="coolwarm", ax=ax4)
    st.pyplot(fig4)
