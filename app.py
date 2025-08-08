# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- App Config ---
st.set_page_config(page_title="Startup Funding Dashboard", layout="wide")
st.title("🚀 Indian Startup Funding Analysis")

# --- Load Data ---
df = pd.read_csv("startup.csv")  # Ensure this CSV is cleaned

# --- Data Cleaning ---
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Amount in USD", "City Location", "Startup Name", "Investors Name", "Industry Vertical"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# --- Sidebar Filters ---
st.sidebar.header("📊 Filter Options")

# 1. City
selected_city = st.sidebar.multiselect("Select Cities", sorted(df["City Location"].unique()), default=["Bengaluru", "Mumbai", "New Delhi"])

# 2. Year
selected_years = st.sidebar.multiselect("Select Year(s)", sorted(df["Year"].unique(), reverse=True), default=[df["Year"].max()])

# 3. Month
month_map = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
             7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
month_options = [month_map[m] for m in sorted(df["Month"].dropna().unique())]
selected_months = st.sidebar.multiselect("Select Month(s)", month_options, default=month_options)

# 4. Industry
industry_list = ["All"] + sorted(df["Industry Vertical"].dropna().unique())
selected_industry = st.sidebar.selectbox("Select Industry", industry_list)

# 5. Startup
startup_list = sorted(df["Startup Name"].dropna().unique())
selected_startups = st.sidebar.multiselect("Select Startups (Optional)", startup_list)

# 6. Investor
all_investors = sorted(set(i.strip() for inv in df["Investors Name"].dropna() for i in inv.split(",") if i.strip()))
selected_investors = st.sidebar.multiselect("Select Investors (Optional)", all_investors)

# 7. Funding Range
min_amt, max_amt = int(df["Amount in USD"].min()), int(df["Amount in USD"].max())
amount_range = st.sidebar.slider("Select Funding Amount Range (USD)", min_amt, max_amt, (min_amt, max_amt))

# 8. Top N
top_n = st.sidebar.slider("Top N Results for Charts", 3, 20, 10)

# --- Apply Filters ---
filtered_df = df[
    df["City Location"].isin(selected_city) &
    df["Year"].isin(selected_years) &
    df["Amount in USD"].between(amount_range[0], amount_range[1])
]

# Apply month filter
filtered_df = filtered_df[filtered_df["Month"].map(month_map).isin(selected_months)]

# Apply industry filter
if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["Industry Vertical"] == selected_industry]

# Apply startup filter
if selected_startups:
    filtered_df = filtered_df[filtered_df["Startup Name"].isin(selected_startups)]

# Apply investor filter
if selected_investors:
    filtered_df = filtered_df[
        filtered_df["Investors Name"].apply(
            lambda x: any(inv in x for inv in selected_investors) if pd.notna(x) else False
        )
    ]

# --- Main Area ---
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
else:
    # Key Metrics
    total_funding = filtered_df["Amount in USD"].sum()
    total_deals = len(filtered_df)
    avg_ticket = filtered_df["Amount in USD"].mean()

    st.markdown("### 📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Funding", f"${total_funding/1e9:.2f}B")
    col2.metric("Number of Deals", f"{total_deals}")
    col3.metric("Average Deal Size", f"${avg_ticket/1e6:.2f}M")
    st.markdown("---")

    # Filtered Data (Optional)
    with st.expander("🔍 See Filtered Data Table"):
        st.dataframe(filtered_df.reset_index(drop=True))

    st.header("📊 Visual Insights")

    # ROW 1
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        st.subheader("🏆 Top Funded Startups")
        top_startups = (
            filtered_df.groupby("Startup Name")["Amount in USD"]
            .sum().nlargest(top_n).reset_index()
        )
        fig1, ax1 = plt.subplots()
        sns.barplot(data=top_startups, x="Amount in USD", y="Startup Name", palette="Set3", ax=ax1)
        ax1.set_xlabel("Total Funding (USD)")
        ax1.set_ylabel(None)
        st.pyplot(fig1)

    with r1c2:
        st.subheader("🤝 Top Investors")
        investor_df = filtered_df.copy()
        investor_df["Investors Name"] = investor_df["Investors Name"].str.split(", ")
        investor_df = investor_df.explode("Investors Name")
        investor_df = investor_df[~investor_df["Investors Name"].isin(["Undisclosed Investors", ""])]
        top_investors = (
            investor_df.groupby("Investors Name")["Amount in USD"]
            .sum().nlargest(top_n).reset_index()
        )
        fig2, ax2 = plt.subplots()
        sns.barplot(data=top_investors, x="Amount in USD", y="Investors Name", palette="Set2", ax=ax2)
        ax2.set_xlabel("Total Investment (USD)")
        ax2.set_ylabel(None)
        st.pyplot(fig2)

    # ROW 2
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        st.subheader("📈 Monthly Funding Trend")
        monthly_trend = (
            filtered_df.groupby("Month")["Amount in USD"]
            .sum().reset_index()
        )
        fig3, ax3 = plt.subplots()
        sns.lineplot(data=monthly_trend, x="Month", y="Amount in USD", marker="o", color="purple", ax=ax3)
        ax3.set_xticks(range(1, 13))
        ax3.set_xlabel("Month")
        ax3.set_ylabel("Total Funding (USD)")
        st.pyplot(fig3)

    with r2c2:
        st.subheader("🏭 Top Industries")
        top_industries = (
            filtered_df.groupby("Industry Vertical")["Amount in USD"]
            .sum().nlargest(top_n).reset_index()
        )
        fig4, ax4 = plt.subplots()
        sns.barplot(data=top_industries, x="Amount in USD", y="Industry Vertical", palette="coolwarm", ax=ax4)
        ax4.set_xlabel("Total Funding (USD)")
        ax4.set_ylabel(None)
        st.pyplot(fig4)

    # ROW 3
    r3c1, r3c2 = st.columns(2)

    with r3c1:
        st.subheader("🏙️ Top Cities (Filtered Years)")
        top_cities = (
            df[df["Year"].isin(selected_years)]
            .groupby("City Location")["Amount in USD"]
            .sum().nlargest(top_n).reset_index()
        )
        fig5, ax5 = plt.subplots()
        sns.barplot(data=top_cities, x="Amount in USD", y="City Location", palette="crest", ax=ax5)
        ax5.set_xlabel("Total Funding (USD)")
        ax5.set_ylabel(None)
        st.pyplot(fig5)

    with r3c2:
        st.subheader("💰 Funding by Investment Type")
        if "Investment Type" in filtered_df.columns:
            inv_type_counts = filtered_df["Investment Type"].value_counts()
            fig6, ax6 = plt.subplots()
            ax6.pie(inv_type_counts.values, labels=inv_type_counts.index, autopct="%1.1f%%",
                    startangle=90, textprops={'fontsize': 8})
            ax6.axis("equal")
            st.pyplot(fig6)
        else:
            st.info("Investment Type data not available.")
