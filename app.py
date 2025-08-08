import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# App configuration
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Startup Funding Analysis")

# Load dataset
df = pd.read_csv("startup.csv")

# Data Cleaning
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Amount in USD", "City Location", "Startup Name", "Investors Name", "Industry Vertical"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# Sidebar Filters
st.sidebar.header("Filter Options")
city_options = ["All"] + sorted(df["City Location"].dropna().unique())
selected_city = st.sidebar.selectbox("Select City", options=city_options)

year_options = ["All"] + sorted(df["Year"].dropna().unique())
selected_year = st.sidebar.selectbox("Select Year", options=year_options)

industry_options = ["All"] + sorted(df["Industry Vertical"].dropna().unique())
selected_industry = st.sidebar.selectbox("Select Industry", options=industry_options)

amount_range = st.sidebar.slider("Funding Amount Range (USD)",
                                  int(df["Amount in USD"].min()),
                                  int(df["Amount in USD"].max()),
                                  (int(df["Amount in USD"].min()), int(df["Amount in USD"].max())))

# Apply Filters
filtered_df = df.copy()
if selected_city != "All":
    filtered_df = filtered_df[filtered_df["City Location"] == selected_city]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["Year"] == selected_year]
if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry Vertical"] == selected_industry]
filtered_df = filtered_df[filtered_df["Amount in USD"].between(amount_range[0], amount_range[1])]

# Data Preview
st.subheader("📊 Filtered Data Preview")
st.dataframe(filtered_df.head())

# Layout: Display 6 charts in 3 rows, 2 per row
# Row 1
col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 10 Funded Startups")
    top_startups = filtered_df.groupby("Startup Name")["Amount in USD"].sum().sort_values(ascending=False).head(10).reset_index()
    if not top_startups.empty:
        fig1, ax1 = plt.subplots()
        sns.barplot(data=top_startups, x="Amount in USD", y="Startup Name", ax=ax1)
        st.pyplot(fig1)
    else:
        st.info("No data available for selected filters.")

with col2:
    st.subheader("Top 10 Investors")
    top_investors = filtered_df.groupby("Investors Name")["Amount in USD"].sum().sort_values(ascending=False).head(10).reset_index()
    if not top_investors.empty:
        fig2, ax2 = plt.subplots()
        sns.barplot(data=top_investors, x="Amount in USD", y="Investors Name", ax=ax2)
        st.pyplot(fig2)
    else:
        st.info("No data available for selected filters.")

# Row 2
col3, col4 = st.columns(2)
with col3:
    st.subheader("Monthly Funding Trend")
    if not filtered_df.empty:
        monthly_trend = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Amount in USD"].sum().reset_index()
        monthly_trend["Date"] = monthly_trend["Date"].astype(str)
        fig3, ax3 = plt.subplots()
        sns.lineplot(data=monthly_trend, x="Date", y="Amount in USD", marker="o", ax=ax3)
        plt.xticks(rotation=45)
        st.pyplot(fig3)
    else:
        st.info("No data available for selected filters.")

with col4:
    st.subheader("Funding by Industry")
    industry_funding = filtered_df.groupby("Industry Vertical")["Amount in USD"].sum().sort_values(ascending=False).head(10).reset_index()
    if not industry_funding.empty:
        fig4, ax4 = plt.subplots()
        sns.barplot(data=industry_funding, x="Amount in USD", y="Industry Vertical", ax=ax4)
        st.pyplot(fig4)
    else:
        st.info("No data available for selected filters.")

# Row 3
col5, col6 = st.columns(2)
with col5:
    st.subheader("Funding Count by Industry")
    industry_count = filtered_df["Industry Vertical"].value_counts().head(10).reset_index()
    industry_count.columns = ["Industry Vertical", "Count"]
    if not industry_count.empty:
        fig5, ax5 = plt.subplots()
        sns.barplot(data=industry_count, x="Count", y="Industry Vertical", ax=ax5)
        st.pyplot(fig5)
    else:
        st.info("No data available for selected filters.")

with col6:
    st.subheader("Funding by City")
    city_funding = filtered_df.groupby("City Location")["Amount in USD"].sum().sort_values(ascending=False).head(10).reset_index()
    if not city_funding.empty:
        fig6, ax6 = plt.subplots()
        sns.barplot(data=city_funding, x="Amount in USD", y="City Location", ax=ax6)
        st.pyplot(fig6)
    else:
        st.info("No data available for selected filters.")
