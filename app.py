import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- App Config ---
st.set_page_config(page_title="🚀 Startup Funding Dashboard", layout="wide")
st.title("🚀 Startup Funding Analysis")

# --- Load Dataset ---
df = pd.read_csv("Startup.csv")

# --- Clean & Enrich ---
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df.dropna(subset=["Amount in USD", "City Location", "Startup Name", "Investors Name", "Industry Vertical", "Date"], inplace=True)
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# --- Sidebar Filters ---
st.sidebar.header("📍 Filter Options")

city_list = sorted(df["City Location"].dropna().unique())
industry_list = sorted(df["Industry Vertical"].dropna().unique())
year_list = sorted(df["Year"].dropna().unique())

selected_cities = st.sidebar.multiselect("Select City(s)", city_list, default=city_list[:3])
selected_industries = st.sidebar.multiselect("Select Industry(s)", industry_list, default=industry_list[:3])
selected_years = st.sidebar.slider("Select Year Range", min_value=int(min(year_list)), max_value=int(max(year_list)), value=(int(min(year_list)), int(max(year_list))))

amount_min = int(df["Amount in USD"].min())
amount_max = int(df["Amount in USD"].max())
amount_range = st.sidebar.slider("Funding Amount Range (USD)", min_value=amount_min, max_value=amount_max, value=(amount_min, amount_max))

show_top_10 = st.sidebar.checkbox("Show only Top 10 in charts", value=True)

# --- Apply Filters ---
filtered_df = df.copy()
filtered_df = filtered_df[
    (filtered_df["City Location"].isin(selected_cities)) &
    (filtered_df["Industry Vertical"].isin(selected_industries)) &
    (filtered_df["Year"].between(selected_years[0], selected_years[1])) &
    (filtered_df["Amount in USD"].between(amount_range[0], amount_range[1]))
]

# --- Chart Function ---
def render_bar_chart(data, x, y, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(data=data, x=x, y=y, ax=ax)
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

def render_line_chart(data, x, y, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.lineplot(data=data, x=x, y=y, marker="o", ax=ax)
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

# --- Data Preview ---
st.subheader("📊 Filtered Dataset Preview")
st.dataframe(filtered_df.head(50), use_container_width=True)

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters.")
else:
    # --- Row 1 ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Top Funded Startups")
        top_startups = filtered_df.groupby("Startup Name")["Amount in USD"].sum().sort_values(ascending=False)
        if show_top_10:
            top_startups = top_startups.head(10)
        render_bar_chart(top_startups.reset_index(), "Amount in USD", "Startup Name", "Top Funded Startups")

    with col2:
        st.subheader("💰 Top Investors")
        top_investors = filtered_df.groupby("Investors Name")["Amount in USD"].sum().sort_values(ascending=False)
        if show_top_10:
            top_investors = top_investors.head(10)
        render_bar_chart(top_investors.reset_index(), "Amount in USD", "Investors Name", "Top Investors")

    # --- Row 2 ---
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📈 Monthly Funding Trend")
        monthly = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Amount in USD"].sum().reset_index()
        monthly["Date"] = monthly["Date"].astype(str)
        render_line_chart(monthly, "Date", "Amount in USD", "Monthly Funding Trend")

    with col4:
        st.subheader("🏭 Industry Funding")
        top_industry = filtered_df.groupby("Industry Vertical")["Amount in USD"].sum().sort_values(ascending=False)
        if show_top_10:
            top_industry = top_industry.head(10)
        render_bar_chart(top_industry.reset_index(), "Amount in USD", "Industry Vertical", "Funding by Industry")

    # --- Row 3 ---
    col5, col6 = st.columns(2)
    with col5:
        st.subheader("🔢 Funding Count by Industry")
        industry_count = filtered_df["Industry Vertical"].value_counts()
        if show_top_10:
            industry_count = industry_count.head(10)
        render_bar_chart(industry_count.reset_index(), "count", "Industry Vertical", "Industry Count")
        
    with col6:
        st.subheader("🌆 Funding by City")
        city_funding = filtered_df.groupby("City Location")["Amount in USD"].sum().sort_values(ascending=False)
        if show_top_10:
            city_funding = city_funding.head(10)
        render_bar_chart(city_funding.reset_index(), "Amount in USD", "City Location", "City-wise Funding")

    # --- Row 4 (Extra Insightful Chart) ---
    col7, col8 = st.columns(2)
    with col7:
        st.subheader("📅 Yearly Trend by Sector")
        yearly_sector = filtered_df.groupby(["Year", "Industry Vertical"])["Amount in USD"].sum().reset_index()
        pivot = yearly_sector.pivot(index="Year", columns="Industry Vertical", values="Amount in USD").fillna(0)
        fig, ax = plt.subplots(figsize=(6, 4))
        pivot.plot(ax=ax)
        ax.set_title("Yearly Trend by Sector")
        st.pyplot(fig)

    with col8:
        st.subheader("🌍 Startup Count per City")
        city_count = filtered_df["City Location"].value_counts()
        if show_top_10:
            city_count = city_count.head(10)
        render_bar_chart(city_count.reset_index(), "count", "City Location", "Startups per City")

