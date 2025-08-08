# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page Config ---
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")

# --- Load Data ---
df = pd.read_csv("startup.csv")  # Make sure CSV is cleaned and available

# --- Data Cleaning ---
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df.dropna(subset=["Amount in USD", "City Location", "Startup Name", "Industry Vertical"], inplace=True)
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# --- Sidebar Filters ---
st.sidebar.header("📊 Filter Options")

# 1. City
cities = sorted(df["City Location"].dropna().unique())
selected_city = st.sidebar.multiselect("Select Cities", cities, default=["Bengaluru", "Mumbai"])

# 2. Year
years = sorted(df["Year"].dropna().unique(), reverse=True)
selected_year = st.sidebar.multiselect("Select Year(s)", years, default=[df["Year"].max()])

# 3. Industry
industries = sorted(df["Industry Vertical"].dropna().unique())
selected_industry = st.sidebar.selectbox("Select Industry", ["All"] + industries)

# 4. Funding Range
min_amt = int(df["Amount in USD"].min())
max_amt = int(df["Amount in USD"].max())
amount_range = st.sidebar.slider("Funding Range (USD)", min_amt, max_amt, (min_amt, max_amt))

# --- Apply Filters ---
filtered_df = df[
    df["City Location"].isin(selected_city) &
    df["Year"].isin(selected_year) &
    df["Amount in USD"].between(amount_range[0], amount_range[1])
]

if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry Vertical"] == selected_industry]

# --- Handle empty ---
if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# --- Metrics ---
total_funding = filtered_df["Amount in USD"].sum()
num_deals = len(filtered_df)
avg_deal = filtered_df["Amount in USD"].mean()

st.markdown("### 💡 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Funding", f"${total_funding/1e9:.2f} B")
col2.metric("Deals", f"{num_deals}")
col3.metric("Avg Deal Size", f"${avg_deal/1e6:.2f} M")
st.markdown("---")

# --- Charts Layout ---

## ROW 1
r1c1, r1c2 = st.columns(2)

with r1c1:
    st.subheader("🏆 Top Funded Startups")
    top_startups = filtered_df.groupby("Startup Name")["Amount in USD"].sum().nlargest(10).reset_index()
    fig1, ax1 = plt.subplots()
    sns.barplot(data=top_startups, y="Startup Name", x="Amount in USD", ax=ax1)
    ax1.set_xlabel("Total Funding (USD)")
    ax1.set_ylabel("")
    st.pyplot(fig1)

with r1c2:
    st.subheader("🏭 Top Industries by Funding")
    top_industries = filtered_df.groupby("Industry Vertical")["Amount in USD"].sum().nlargest(10).reset_index()
    fig2, ax2 = plt.subplots()
    sns.barplot(data=top_industries, y="Industry Vertical", x="Amount in USD", ax=ax2, palette="coolwarm")
    ax2.set_xlabel("Total Funding (USD)")
    ax2.set_ylabel("")
    st.pyplot(fig2)

## ROW 2
r2c1, r2c2 = st.columns(2)

with r2c1:
    st.subheader("📈 Funding by Month")
    monthly = filtered_df.groupby("Month")["Amount in USD"].sum().reset_index()
    fig3, ax3 = plt.subplots()
    sns.lineplot(data=monthly, x="Month", y="Amount in USD", marker='o', ax=ax3)
    ax3.set_xticks(range(1, 13))
    ax3.set_xlabel("Month")
    ax3.set_ylabel("Total Funding")
    st.pyplot(fig3)

with r2c2:
    st.subheader("🏙️ Top Cities by Funding")
    top_cities = filtered_df.groupby("City Location")["Amount in USD"].sum().nlargest(10).reset_index()
    fig4, ax4 = plt.subplots()
    sns.barplot(data=top_cities, y="City Location", x="Amount in USD", ax=ax4, palette="crest")
    ax4.set_xlabel("Total Funding (USD)")
    ax4.set_ylabel("")
    st.pyplot(fig4)

## ROW 3
r3c1, r3c2 = st.columns(2)

with r3c1:
    st.subheader("🔝 Top Investors")
    if "Investors Name" in filtered_df.columns:
        investor_df = filtered_df.copy()
        investor_df["Investors Name"] = investor_df["Investors Name"].str.split(", ")
        investor_df = investor_df.explode("Investors Name")
        investor_df = investor_df[~investor_df["Investors Name"].isin(["Undisclosed Investors", ""])]
        top_investors = investor_df.groupby("Investors Name")["Amount in USD"].sum().nlargest(10).reset_index()
        fig5, ax5 = plt.subplots()
        sns.barplot(data=top_investors, y="Investors Name", x="Amount in USD", ax=ax5, palette="Set2")
        ax5.set_xlabel("Total Investment (USD)")
        ax5.set_ylabel("")
        st.pyplot(fig5)
    else:
        st.info("Investor data not available.")

with r3c2:
    st.subheader("💸 Investment Type Breakdown")
    if "Investment Type" in filtered_df.columns:
        type_count = filtered_df["Investment Type"].value_counts()
        fig6, ax6 = plt.subplots()
        ax6.pie(type_count.values, labels=type_count.index, autopct='%1.1f%%', startangle=90)
        ax6.axis("equal")
        st.pyplot(fig6)
    else:
        st.info("Investment Type column not found.")
