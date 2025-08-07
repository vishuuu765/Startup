# app.py


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# App configuration
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")

# Load dataset
df = pd.read_csv("your_dataset.csv")  # Replace with your CSV file name

# Data Cleaning
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Amount in USD", "City Location", "Startup Name"])

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_city = st.sidebar.selectbox("Select City", options=df["City Location"].dropna().unique())
selected_year = st.sidebar.selectbox("Select Year", options=df["Date"].dt.year.dropna().unique())

# Filter data
filtered_df = df[
    (df["City Location"] == selected_city) &
    (df["Date"].dt.year == selected_year)
]

# Show Raw Data
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)

# Section: Top 10 Funded Startups
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

# Section: Total Funding by Investor
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

# Section: Funding Trend Over Time
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

