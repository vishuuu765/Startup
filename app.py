# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# App configuration
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")

# --- DATA LOADING AND CLEANING ---

# Load dataset from the correct file
df = pd.read_csv("Startup.csv")

# Standardize column names
df.rename(columns={
    "Date dd/mm/yyyy": "Date",
    "City  Location": "City Location",
    "Investors Name": "Investors Name",
    "Startup Name": "Startup Name",
    "Amount in USD": "Amount in USD"
}, inplace=True)

# Clean 'Amount in USD' column by removing commas and converting to numeric
# Coerce errors will turn problematic values into 'NaN' (Not a Number)
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"].str.replace(",", ""), errors='coerce')

# Clean and format the 'Date' column
# Replace incorrect separators and convert to datetime objects
df["Date"] = pd.to_datetime(df["Date"].str.replace('.', '-', regex=False).str.replace('/', '-', regex=False), errors='coerce')

# Drop rows with missing essential data for the dashboard to function
df.dropna(subset=["Date", "City Location", "Startup Name", "Amount in USD", "Investors Name"], inplace=True)

# Convert year to integer
df["Year"] = df["Date"].dt.year.astype(int)

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Options")
selected_year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique()))
selected_city = st.sidebar.selectbox("Select City", sorted(df["City Location"].unique()))

# --- FILTERED DATAFRAME ---
filtered_df = df[(df["Year"] == selected_year) & (df["City Location"] == selected_city)]

if filtered_df.empty:
    st.warning(f"No data available for {selected_city} in {selected_year}. Please select different filters.")
else:
    # --- MAIN PAGE DISPLAY ---

    st.header(f"Dashboard for {selected_city} in {selected_year}")

    # Show Raw Data
    if st.checkbox("Show Raw Data"):
        st.dataframe(filtered_df)

    # --- ANALYSIS & VISUALIZATION ---

    # Section: Top 10 Funded Startups
    st.subheader("Top 10 Funded Startups")
    top_startups = (
        filtered_df.groupby("Startup Name")["Amount in USD"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_startups.values, y=top_startups.index, palette="viridis", ax=ax1)
    ax1.set_xlabel("Total Funding (USD)")
    ax1.set_ylabel("Startup Name")
    st.pyplot(fig1)

    # Process investor names: split and explode for accurate analysis
    investor_df = filtered_df.copy()
    investor_df["Investors Name"] = investor_df["Investors Name"].str.split(', ')
    investor_df = investor_df.explode("Investors Name")
    
    # Exclude undisclosed investors for a cleaner chart
    investor_df = investor_df[investor_df["Investors Name"] != "Undisclosed Investors"]


    # Section: Top 10 Investors
    st.subheader("Top 10 Investors")
    top_investors = (
        investor_df.groupby("Investors Name")["Amount in USD"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_investors.values, y=top_investors.index, palette="plasma", ax=ax2)
    ax2.set_xlabel("Total Amount Invested (USD)")
    ax2.set_ylabel("Investor Name")
    st.pyplot(fig2)
