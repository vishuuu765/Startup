import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Startup Funding Analysis", layout="wide")
st.title("🚀 Indian Startup Funding Dashboard")

# Load data
df = pd.read_csv("startup.csv")

# Preprocess
df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df.dropna(subset=["Amount in USD", "City Location", "Startup Name", "Date"], inplace=True)
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month_name()

# Sidebar filters
st.sidebar.header("🔍 Filter Options")

city_filter = st.sidebar.multiselect("Select City", sorted(df["City Location"].unique()), default=["Bengaluru", "Mumbai"])
year_filter = st.sidebar.multiselect("Select Year", sorted(df["Year"].dropna().unique(), reverse=True), default=[df["Year"].max()])
industry_list = ["All"] + sorted(df["Industry Vertical"].dropna().unique())
industry_filter = st.sidebar.selectbox("Select Industry", industry_list)
amount_min, amount_max = int(df["Amount in USD"].min()), int(df["Amount in USD"].max())
amount_filter = st.sidebar.slider("Funding Amount Range (USD)", amount_min, amount_max, (amount_min, amount_max))

# Filter data
filtered_df = df[
    (df["City Location"].isin(city_filter)) &
    (df["Year"].isin(year_filter)) &
    (df["Amount in USD"].between(amount_filter[0], amount_filter[1]))
]
if industry_filter != "All":
    filtered_df = filtered_df[filtered_df["Industry Vertical"] == industry_filter]

# Layout setup: 3 rows, 2 charts per row
def draw_chart(title, data_func):
    st.subheader(title)
    fig, ax = plt.subplots()
    data_func(ax)
    st.pyplot(fig)

# Row 1
col1, col2 = st.columns(2)

with col1:
    draw_chart("1️⃣ Top 10 Funded Startups", lambda ax: sns.barplot(
        data=filtered_df.groupby("Startup Name")["Amount in USD"].sum().nlargest(10).reset_index(),
        x="Amount in USD", y="Startup Name", palette="Set2", ax=ax))

with col2:
    draw_chart("2️⃣ Top 10 Investors", lambda ax: sns.barplot(
        data=filtered_df.groupby("Investors Name")["Amount in USD"].sum().nlargest(10).reset_index(),
        x="Amount in USD", y="Investors Name", palette="Set3", ax=ax))

# Row 2
col3, col4 = st.columns(2)

with col3:
    draw_chart("3️⃣ Monthly Funding Trend", lambda ax: sns.lineplot(
        data=filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Amount in USD"]
        .sum().reset_index().rename(columns={"Date": "Month"}), x="Month", y="Amount in USD", marker="o", ax=ax))

with col4:
    draw_chart("4️⃣ Funding by Industry", lambda ax: sns.barplot(
        data=filtered_df.groupby("Industry Vertical")["Amount in USD"].sum().nlargest(10).reset_index(),
        x="Amount in USD", y="Industry Vertical", palette="coolwarm", ax=ax))

# Row 3
col5, col6 = st.columns(2)

with col5:
    draw_chart("5️⃣ City-wise Funding Distribution", lambda ax: sns.barplot(
        data=filtered_df.groupby("City Location")["Amount in USD"].sum().nlargest(10).reset_index(),
        x="Amount in USD", y="City Location", palette="Blues", ax=ax))

with col6:
    draw_chart("6️⃣ Year-wise Funding Trend", lambda ax: sns.lineplot(
        data=filtered_df.groupby("Year")["Amount in USD"].sum().reset_index(),
        x="Year", y="Amount in USD", marker="o", ax=ax))

# Optional: Show raw data
with st.expander("📂 Show Raw Filtered Data"):
    st.dataframe(filtered_df)
