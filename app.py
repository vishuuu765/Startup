import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- App Config ---
st.set_page_config(page_title="🚀 Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")

# --- Load Dataset ---
df = pd.read_csv("startup.csv")

# --- Data Cleaning ---
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df.dropna(subset=["Amount in USD", "City Location", "Startup Name", "Investors Name", "Industry Vertical"], inplace=True)
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# --- Sidebar Filters ---
st.sidebar.header("📍 Filter Options")

selected_cities = st.sidebar.multiselect("Select City(s)", options=sorted(df["City Location"].unique()), default=[])
selected_years = st.sidebar.multiselect("Select Year(s)", options=sorted(df["Year"].unique()), default=[])
selected_industries = st.sidebar.multiselect("Select Industry(s)", options=sorted(df["Industry Vertical"].unique()), default=[])

min_amt = int(df["Amount in USD"].min())
max_amt = int(df["Amount in USD"].max())
amount_range = st.sidebar.slider("Funding Amount Range (USD)", min_amt, max_amt, (min_amt, max_amt))

# --- Apply Filters ---
filtered_df = df.copy()
if selected_cities:
    filtered_df = filtered_df[filtered_df["City Location"].isin(selected_cities)]
if selected_years:
    filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
if selected_industries:
    filtered_df = filtered_df[filtered_df["Industry Vertical"].isin(selected_industries)]

filtered_df = filtered_df[filtered_df["Amount in USD"].between(amount_range[0], amount_range[1])]

# --- Data Preview ---
st.subheader("📊 Filtered Data Preview")
st.dataframe(filtered_df.head(50), use_container_width=True)

# --- Layout: 3 Rows, 2 Columns each ---

# Row 1
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏆 Top 10 Funded Startups")
    top_startups = filtered_df.groupby("Startup Name")["Amount in USD"].sum().nlargest(10).reset_index()
    if not top_startups.empty:
        fig, ax = plt.subplots()
        sns.barplot(data=top_startups, x="Amount in USD", y="Startup Name", ax=ax)
        ax.set_title("Top Funded Startups")
        st.pyplot(fig)
    else:
        st.warning("No data available.")

with col2:
    st.subheader("💰 Top 10 Investors")
    top_investors = filtered_df.groupby("Investors Name")["Amount in USD"].sum().nlargest(10).reset_index()
    if not top_investors.empty:
        fig, ax = plt.subplots()
        sns.barplot(data=top_investors, x="Amount in USD", y="Investors Name", ax=ax)
        ax.set_title("Top Investors")
        st.pyplot(fig)
    else:
        st.warning("No data available.")

# Row 2
col3, col4 = st.columns(2)
with col3:
    st.subheader("📈 Monthly Funding Trend")
    if not filtered_df.empty:
        monthly = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Amount in USD"].sum().reset_index()
        monthly["Date"] = monthly["Date"].astype(str)
        fig, ax = plt.subplots()
        sns.lineplot(data=monthly, x="Date", y="Amount in USD", marker="o", ax=ax)
        ax.set_xticklabels(monthly["Date"], rotation=45)
        ax.set_title("Monthly Trend")
        st.pyplot(fig)
    else:
        st.info("No data available.")

with col4:
    st.subheader("🏭 Funding by Industry")
    top_industry = filtered_df.groupby("Industry Vertical")["Amount in USD"].sum().nlargest(10).reset_index()
    if not top_industry.empty:
        fig, ax = plt.subplots()
        sns.barplot(data=top_industry, x="Amount in USD", y="Industry Vertical", ax=ax)
        ax.set_title("Top Industries by Funding")
        st.pyplot(fig)
    else:
        st.info("No data available.")

# Row 3
col5, col6 = st.columns(2)
with col5:
    st.subheader("📊 Funding Count by Industry")
    industry_count = filtered_df["Industry Vertical"].value_counts().head(10).reset_index()
    industry_count.columns = ["Industry Vertical", "Count"]
    if not industry_count.empty:
        fig, ax = plt.subplots()
        sns.barplot(data=industry_count, x="Count", y="Industry Vertical", ax=ax)
        ax.set_title("Funding Count")
        st.pyplot(fig)
    else:
        st.info("No data available.")

with col6:
    st.subheader("🗺️ Funding by City")
    top_cities = filtered_df.groupby("City Location")["Amount in USD"].sum().nlargest(10).reset_index()
    if not top_cities.empty:
        fig, ax = plt.subplots()
        sns.barplot(data=top_cities, x="Amount in USD", y="City Location", ax=ax)
        ax.set_title("Top Funded Cities")
        st.pyplot(fig)
    else:
        st.info("No data available.")
