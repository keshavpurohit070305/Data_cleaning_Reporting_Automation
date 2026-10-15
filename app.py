"""
app.py
------
Interactive dashboard for the Data Cleaning & Reporting Automation project,
styled after Power BI: a dark canvas, a slicer panel that cross-filters
every visual, KPI cards, and drill-down tabs.

Run with:  streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.cleaning import run_cleaning_pipeline
from src.quality_metrics import quality_comparison

st.set_page_config(
    page_title="Data Cleaning & Reporting Automation",
    page_icon="🧹",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Power BI-style theme
# ---------------------------------------------------------------------------
PBI_BG = "#141B2D"
PBI_PANEL = "#1F2A44"
PBI_ACCENT = "#F2C811"   # Power BI's signature yellow
PBI_BLUE = "#2C6BED"
PBI_TEXT = "#E5E7EB"
PBI_MUTED = "#9CA3AF"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {PBI_BG}; }}
    section[data-testid="stSidebar"] {{ background-color: {PBI_PANEL}; }}
    .block-container {{ padding-top: 1.6rem; }}
    h1, h2, h3, h4, p, span, label {{ color: {PBI_TEXT} !important; }}
    div[data-testid="stMetric"] {{
        background-color: {PBI_PANEL};
        border-left: 4px solid {PBI_ACCENT};
        border-radius: 6px;
        padding: 14px 16px;
    }}
    div[data-testid="stMetricLabel"] {{ color: {PBI_MUTED} !important; }}
    .pbi-tag {{
        display: inline-block;
        background: {PBI_ACCENT};
        color: #141B2D;
        padding: 3px 12px;
        border-radius: 3px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    .pbi-panel {{
        background-color: {PBI_PANEL};
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }}
    div[data-baseweb="tab-list"] {{ gap: 4px; }}
    button[data-baseweb="tab"] {{
        background-color: {PBI_PANEL};
        border-radius: 4px 4px 0 0;
        color: {PBI_TEXT} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_LAYOUT = dict(
    plot_bgcolor=PBI_PANEL, paper_bgcolor=PBI_PANEL,
    font_color=PBI_TEXT, margin=dict(l=10, r=10, t=40, b=10),
)

st.markdown('<span class="pbi-tag">THIRANEX INTERNSHIP · TASK 4</span>', unsafe_allow_html=True)
st.title("🧹 Data Cleaning & Reporting Automation")
st.caption("Power BI-style interactive report — automated cleaning, data quality scoring, and visual summaries.")


# ---------------------------------------------------------------------------
# Pipeline (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def load_pipeline():
    raw_df, cleaned_df, log_df = run_cleaning_pipeline("data/raw_customer_orders.csv")
    quality_df = quality_comparison(raw_df, cleaned_df)
    return raw_df, cleaned_df, log_df, quality_df


with st.spinner("Running automated cleaning pipeline..."):
    raw_df, cleaned_df, log_df, quality_df = load_pipeline()

# ---------------------------------------------------------------------------
# Sidebar — slicers (cross-filter every visual, Power BI style)
# ---------------------------------------------------------------------------
st.sidebar.markdown("### 🔎 Slicers")
category_filter = st.sidebar.multiselect(
    "Product Category", sorted(cleaned_df["product_category"].unique()),
)
state_filter = st.sidebar.multiselect(
    "State", sorted(cleaned_df["state"].unique()),
)
status_filter = st.sidebar.multiselect(
    "Order Status", sorted(cleaned_df["order_status"].unique()),
)
date_min = pd.to_datetime(cleaned_df["order_date"]).min()
date_max = pd.to_datetime(cleaned_df["order_date"]).max()
date_range = st.sidebar.date_input("Order Date Range", value=(date_min, date_max),
                                    min_value=date_min, max_value=date_max)

filtered_df = cleaned_df.copy()
filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"])
if category_filter:
    filtered_df = filtered_df[filtered_df["product_category"].isin(category_filter)]
if state_filter:
    filtered_df = filtered_df[filtered_df["state"].isin(state_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df["order_status"].isin(status_filter)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df["order_date"] >= start) & (filtered_df["order_date"] <= end)]

st.sidebar.divider()
st.sidebar.markdown("### 📥 Downloads")
st.sidebar.download_button("Cleaned Data (CSV)", cleaned_df.to_csv(index=False).encode("utf-8"),
                            "cleaned_customer_orders.csv", "text/csv")
st.sidebar.download_button("Cleaning Log (CSV)", log_df.to_csv(index=False).encode("utf-8"),
                            "cleaning_log.csv", "text/csv")
report_path = Path("outputs/Data_Quality_Report.xlsx")
if report_path.exists():
    st.sidebar.download_button("Full Excel Report (.xlsx)", report_path.read_bytes(),
                                "Data_Quality_Report.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
overall_before = quality_df.loc[3, "before_cleaning"]
overall_after = quality_df.loc[3, "after_cleaning"]
duplicates_removed = len(raw_df) - len(cleaned_df)
values_fixed = int(log_df["rows_affected"].sum())

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Raw Records", f"{len(raw_df):,}")
k2.metric("Cleaned Records", f"{len(cleaned_df):,}")
k3.metric("Duplicates Removed", f"{duplicates_removed}")
k4.metric("Values Fixed / Imputed", f"{values_fixed:,}")
k5.metric("Quality Score", f"{overall_after}%", delta=f"+{round(overall_after - overall_before, 2)} pts")

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "✅ Data Quality", "🧾 Cleaning Log", "🔍 Data Explorer", "📄 About"]
)

with tab1:
    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown("**Revenue by Product Category**")
        cat_rev = filtered_df.groupby("product_category")["total_amount"].sum().reset_index()
        fig = px.bar(cat_rev, x="product_category", y="total_amount", color="product_category",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=340)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**Orders by Status**")
        status_counts = filtered_df["order_status"].value_counts().reset_index()
        status_counts.columns = ["order_status", "count"]
        fig2 = px.pie(status_counts, names="order_status", values="count", hole=0.5,
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(**PLOTLY_LAYOUT, height=340)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Monthly Order Volume & Revenue**")
    monthly = filtered_df.groupby("order_month").agg(
        orders=("order_id", "count"), revenue=("total_amount", "sum")
    ).reset_index().sort_values("order_month")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=monthly["order_month"], y=monthly["revenue"], name="Revenue",
                           marker_color=PBI_BLUE, yaxis="y1"))
    fig3.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["orders"], name="Orders",
                               line=dict(color=PBI_ACCENT, width=2), yaxis="y2"))
    fig3.update_layout(
        **PLOTLY_LAYOUT, height=360,
        yaxis=dict(title="Revenue (₹)"),
        yaxis2=dict(title="Orders", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig3, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Orders by State**")
        state_counts = filtered_df["state"].value_counts().reset_index()
        state_counts.columns = ["state", "count"]
        fig4 = px.bar(state_counts, x="count", y="state", orientation="h",
                      color="count", color_continuous_scale="Blues")
        fig4.update_layout(**PLOTLY_LAYOUT, height=320, coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)
    with c4:
        st.markdown("**Payment Method Split**")
        pay_counts = filtered_df["payment_method"].value_counts().reset_index()
        pay_counts.columns = ["payment_method", "count"]
        fig5 = px.bar(pay_counts, x="payment_method", y="count", color="payment_method",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig5.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

with tab2:
    st.markdown("**Data Quality Score — Before vs. After Cleaning**")
    q1, q2 = st.columns([1, 1.2])
    with q1:
        st.dataframe(quality_df.set_index("metric"), use_container_width=True)
    with q2:
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(x=quality_df["metric"], y=quality_df["before_cleaning"],
                               name="Before", marker_color="#EF4444"))
        fig6.add_trace(go.Bar(x=quality_df["metric"], y=quality_df["after_cleaning"],
                               name="After", marker_color="#22C55E"))
        fig6.update_layout(**PLOTLY_LAYOUT, barmode="group", height=340,
                            yaxis=dict(title="Score (%)", range=[0, 105]))
        st.plotly_chart(fig6, use_container_width=True)

    st.markdown("**Missing Values by Column — Raw Data**")
    missing = raw_df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=True).reset_index()
    missing.columns = ["column", "missing_count"]
    fig7 = px.bar(missing, x="missing_count", y="column", orientation="h",
                 color="missing_count", color_continuous_scale="Oranges")
    fig7.update_layout(**PLOTLY_LAYOUT, height=320, coloraxis_showscale=False)
    st.plotly_chart(fig7, use_container_width=True)

with tab3:
    st.markdown("**Automated Cleaning Actions Log**")
    st.caption("Every transformation the pipeline applied, with the exact number of rows affected — nothing is a silent fix.")
    fig8 = px.bar(log_df.sort_values("rows_affected"), x="rows_affected", y="step",
                 orientation="h", color="rows_affected", color_continuous_scale="Blues",
                 text="rows_affected")
    fig8.update_layout(**PLOTLY_LAYOUT, height=460, coloraxis_showscale=False)
    st.plotly_chart(fig8, use_container_width=True)
    st.dataframe(log_df, use_container_width=True, height=300)

with tab4:
    st.markdown(f"**Cleaned Dataset** — {len(filtered_df):,} rows matching current slicers")
    st.dataframe(filtered_df, use_container_width=True, height=480)

with tab5:
    st.markdown(
        """
        ### Key Features
        - **Automated cleaning pipeline in Python** — every fix is rule-based and logged, covering missing values, duplicates, and inconsistent formatting end to end.
        - **Missing values, duplicates, and inconsistent data handled automatically** — mixed date formats, inconsistent text casing, invalid emails/phone numbers, negative or zero quantities/prices, statistical outliers, exact and near-duplicate records.
        - **Automated reports and visual summaries** — a multi-sheet Excel report with native charts is generated on every run, alongside this interactive Power BI-style dashboard.

        ### Expected Outcome
        Demonstrates practical data preprocessing, automation, and reporting efficiency: a raw, messy export is
        transformed into a clean, analysis-ready dataset with a full audit trail and shareable visual reporting —
        without manual spreadsheet editing.
        """
    )
    st.info(
        "Contact fields (email/phone) that failed validation are left blank rather than "
        "auto-filled with a guessed value — imputing plausible-looking contact info would "
        "silently introduce wrong data, so those rows are flagged for manual follow-up instead.",
        icon="ℹ️",
    )

st.divider()
st.caption("Thiranex Internship · Task 4 — Data Cleaning & Reporting Automation")
