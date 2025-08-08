# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# App configuration
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")

# Load dataset
df = pd.read_csv("startup.csv")  # Ensure this CSV is cleaned correctly

# Data Cleaning
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Amount in USD", "City Location", "Startup Name", "Investors Name", "Industry Vertical"])

# Feature Engineering
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# Sidebar Filters
st.sidebar.header("📊 Filter Options")
selected_city = st.sidebar.selectbox("Select City", sorted(df["City Location"].dropna().unique()))
selected_year = st.sidebar.selectbox("Select Year", sorted(df["Year"].dropna().unique(), reverse=True))
industry_list = ["All"] + sorted(df["Industry Vertical"].dropna().unique())
selected_industry = st.sidebar.selectbox("Select Industry", industry_list)
min_amt, max_amt = int(df["Amount in USD"].min()), int(df["Amount in USD"].max())
amount_range = st.sidebar.slider("Select Funding Amount Range (USD)", min_amt, max_amt, (min_amt, max_amt))

# Filter data
filtered_df = df[
    (df["City Location"] == selected_city) &
    (df["Year"] == selected_year) &
    (df["Amount in USD"].between(amount_range[0], amount_range[1]))
]

if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry Vertical"] == selected_industry]

# --- MAIN PAGE ---
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
else:
    # Key Metrics
    total_funding = filtered_df["Amount in USD"].sum()
    total_deals = filtered_df.shape[0]
    avg_deal = filtered_df["Amount in USD"].mean()

    st.markdown("### Key Metrics")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Funding", f"${total_funding/1e9:.2f}B")
    kpi2.metric("Number of Deals", f"{total_deals}")
    kpi3.metric("Average Deal Size", f"${avg_deal/1e6:.2f}M")
    st.markdown("---")

    # Filtered Data Preview (Expandable)
    with st.expander("🔍 See Filtered Data Table"):
        st.dataframe(filtered_df.reset_index(drop=True))

    # --- VISUAL INSIGHTS ---
    st.header("📊 Visual Insights")

    # ROW 1
    row1 = st.columns(2)

    with row1[0]:
        st.subheader("🏆 Top 10 Funded Startups")
        top_startups = (
            filtered_df.groupby("Startup Name")["Amount in USD"]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        fig1, ax1 = plt.subplots()
        sns.barplot(data=top_startups, x="Amount in USD", y="Startup Name", palette="Set3", ax=ax1)
        ax1.set_xlabel("Total Funding (USD)")
        ax1.set_ylabel(None)
        st.pyplot(fig1)

    with row1[1]:
        st.subheader("🤝 Top 10 Investors")
        investor_df = filtered_df.copy()
        investor_df["Investors Name"] = investor_df["Investors Name"].str.split(', ')
        investor_df = investor_df.explode("Investors Name")
        investor_df = investor_df[~investor_df["Investors Name"].isin(["Undisclosed Investors", ""])]
        top_investors = (
            investor_df.groupby("Investors Name")["Amount in USD"]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        fig2, ax2 = plt.subplots()
        sns.barplot(data=top_investors, x="Amount in USD", y="Investors Name", palette="Set2", ax=ax2)
        ax2.set_xlabel("Total Investment (USD)")
        ax2.set_ylabel(None)
        st.pyplot(fig2)

    # ROW 2
    row2 = st.columns(2)

    with row2[0]:
        st.subheader("📈 Monthly Funding Trend")
        monthly_trend = (
            filtered_df.groupby("Month")["Amount in USD"]
            .sum()
            .reset_index()
        )
        fig3, ax3 = plt.subplots()
        sns.lineplot(data=monthly_trend, x="Month", y="Amount in USD", marker="o", color="purple", ax=ax3)
        ax3.set_xticks(range(1, 13))
        ax3.set_xlabel("Month")
        ax3.set_ylabel("Total Funding (USD)")
        st.pyplot(fig3)

    with row2[1]:
        st.subheader("🏭 Funding Distribution by Industry")
        top_industries = (
            filtered_df.groupby("Industry Vertical")["Amount in USD"]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        fig4, ax4 = plt.subplots()
        sns.barplot(data=top_industries, x="Amount in USD", y="Industry Vertical", palette="coolwarm", ax=ax4)
        ax4.set_xlabel("Total Funding (USD)")
        ax4.set_ylabel(None)
        st.pyplot(fig4)

    # ROW 3
    row3 = st.columns(2)

    with row3[0]:
        st.subheader("🏙️ City-wise Funding Comparison (Filtered Year)")
        city_funding = (
            df[df["Year"] == selected_year]
            .groupby("City Location")["Amount in USD"]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        fig5, ax5 = plt.subplots()
        sns.barplot(data=city_funding, x="Amount in USD", y="City Location", palette="crest", ax=ax5)
        ax5.set_xlabel("Total Funding (USD)")
        ax5.set_ylabel(None)
        st.pyplot(fig5)

    with row3[1]:
        st.subheader("💰 Funding by Investment Type (Pie Chart)")
        if "Investment Type" in filtered_df.columns:
            inv_dist = filtered_df["Investment Type"].value_counts()
            fig6, ax6 = plt.subplots()
            ax6.pie(inv_dist.values, labels=inv_dist.index, autopct="%1.1f%%", startangle=90, textprops={'fontsize': 8})
            ax6.axis("equal")
            st.pyplot(fig6)
        else:
            st.info("Investment Type data not available in this dataset.")
