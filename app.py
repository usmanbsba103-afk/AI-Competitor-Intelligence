import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Competitor Intelligence & Market Analysis",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CLEAN, BRIGHT & EASY-TO-READ LIGHT THEME ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        .stApp {
            background-color: #F8FAFC;
            color: #1E293B;
        }
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        [data-testid="stSidebar"] * {
            color: #1E293B !important;
        }

        /* Light & Welcoming Executive Header */
        .exec-header {
            background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
            padding: 1.6rem 2rem;
            border-radius: 14px;
            border: 1px solid #A7F3D0;
            border-left: 6px solid #059669;
            margin-bottom: 1.4rem;
            box-shadow: 0 2px 10px rgba(5, 150, 105, 0.06);
        }
        .exec-header h1 {
            color: #064E3B !important;
            font-size: 1.85rem;
            font-weight: 800;
            margin: 0;
        }
        .exec-header p {
            color: #047857 !important;
            font-size: 0.96rem;
            margin: 0.4rem 0 0 0;
            font-weight: 500;
        }

        /* Interactive Light KPI Cards with Hover Details */
        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #10B981;
            border-radius: 12px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            transition: all 0.25s ease;
            cursor: pointer;
            min-height: 125px;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            border-color: #10B981;
            background-color: #F0FDF4;
            box-shadow: 0 10px 22px rgba(16, 185, 129, 0.14);
        }
        .kpi-label {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #64748B;
            margin-bottom: 0.35rem;
        }
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.2;
        }
        .kpi-hint {
            font-size: 0.76rem;
            color: #059669;
            margin-top: 0.4rem;
            font-weight: 500;
        }
        .kpi-detail-box {
            max-height: 0;
            opacity: 0;
            overflow: hidden;
            transition: all 0.28s ease;
            font-size: 0.81rem;
            color: #064E3B;
            background: #DCFCE7;
            border-radius: 6px;
            padding: 0 0.6rem;
        }
        .kpi-card:hover .kpi-detail-box {
            max-height: 95px;
            opacity: 1;
            padding: 0.45rem 0.65rem;
            margin-top: 0.5rem;
        }
        .kpi-card:hover .kpi-hint {
            display: none;
        }

        /* Light Tutorial Box */
        .tutorial-box {
            background-color: #FFFFFF;
            border: 1px solid #BAE6FD;
            border-left: 5px solid #0284C7;
            border-radius: 12px;
            padding: 1.15rem 1.4rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.06);
        }
        .tutorial-box h4 {
            margin: 0 0 0.45rem 0;
            color: #0369A1;
            font-weight: 700;
        }

        /* Clean Emerald Buttons */
        .stButton > button, .stDownloadButton > button {
            background-color: #059669 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.2rem !important;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background-color: #047857 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "users_db" not in st.session_state:
    st.session_state.users_db = {"admin": "fyp2026"}
if "show_tutorial" not in st.session_state:
    st.session_state.show_tutorial = True


# --- 1. DIRECT LOGIN & SIGN-UP PORTAL ---
def render_login_portal():
    col1, col2, col3 = st.columns([1, 1.45, 1])
    with col2:
        st.markdown(
            """
            <div class="exec-header" style="text-align:center; margin-top:1.5rem;">
                <h1>Competitor Intelligence Portal</h1>
                <p>Clear, Visual & Automated Market Analysis System</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tab_login, tab_register = st.tabs(["Sign In", "Create Account (Direct Login)"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted:
                    if username in st.session_state.users_db and st.session_state.users_db[username] == password:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.session_state.show_tutorial = True
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Demo account: admin / fyp2026")
            st.caption("Demo Access — Username: `admin` | Password: `fyp2026`")

        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username", placeholder="e.g., usman_analyst")
                new_pass = st.text_input("Create Password", type="password", placeholder="Enter password")
                reg_submit = st.form_submit_button("Create Account & Login Now", use_container_width=True)
                if reg_submit:
                    if new_user.strip() and new_pass.strip():
                        if new_user in st.session_state.users_db:
                            st.warning("Username already exists. Please sign in or pick another.")
                        else:
                            st.session_state.users_db[new_user.strip()] = new_pass.strip()
                            st.session_state.authenticated = True
                            st.session_state.current_user = new_user.strip()
                            st.session_state.show_tutorial = True
                            st.rerun()
                    else:
                        st.warning("Please enter both username and password.")


if not st.session_state.authenticated:
    render_login_portal()
    st.stop()


# --- SMART DATA & ANALYTICS ENGINE ---
def load_sample_data():
    return pd.DataFrame(
        {
            "Competitor_Name": ["My_Brand", "Competitor_A", "Competitor_B", "Competitor_C", "Competitor_D"],
            "Price": [4500, 4200, 5200, 3900, 4800],
            "Customer_Rating": [4.6, 4.2, 4.8, 3.9, 4.4],
            "Market_Share": [24, 28, 22, 14, 12],
            "Monthly_Sales": [1850, 2100, 1620, 1150, 980],
            "Key_Advantage": [
                "Fast delivery & warranty",
                "Aggressive discounting",
                "Premium build quality",
                "Lowest entry price",
                "Strong retail presence",
            ],
        }
    )


def find_column(df: pd.DataFrame, keywords: list, numeric_only: bool = False):
    cols = df.select_dtypes(include="number").columns.tolist() if numeric_only else df.columns.tolist()
    for kw in keywords:
        for col in cols:
            if kw in col.lower():
                return col
    return cols[0] if cols else None


def build_adaptive_kpis(df: pd.DataFrame, file_label: str) -> list:
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    total_rows = len(df)
    total_cols = len(df.columns)

    kpis = [
        {
            "label": "Total Records Analyzed",
            "value": f"{total_rows:,}",
            "detail": f"File: {file_label} | {total_cols} columns ({len(num_cols)} numeric, {len(cat_cols)} categorical).",
        }
    ]

    price_col = find_column(
        df, ["price", "salesamount", "revenue", "amount", "sales", "cost", "profit"], numeric_only=True
    )
    if price_col:
        avg_v = df[price_col].mean()
        min_v = df[price_col].min()
        max_v = df[price_col].max()
        kpis.append(
            {
                "label": f"Average {price_col}",
                "value": f"PKR {avg_v:,.0f}",
                "detail": f"Lowest: PKR {min_v:,.0f} | Highest: PKR {max_v:,.0f} | Sum: PKR {df[price_col].sum():,.0f}",
            }
        )
    else:
        kpis.append(
            {
                "label": "Data Quality Score",
                "value": f"{(1 - df.isna().mean().mean()) * 100:.1f}%",
                "detail": f"Complete non-empty entries across {total_rows:,} rows.",
            }
        )

    rating_col = find_column(df, ["rating", "score", "review", "satisfaction"], numeric_only=True)
    if rating_col and any(k in rating_col.lower() for k in ["rating", "score", "review", "satisfaction"]):
        kpis.append(
            {
                "label": f"Average {rating_col}",
                "value": f"{df[rating_col].mean():.2f} / 5.0",
                "detail": f"Top Rating: {df[rating_col].max():.2f} | Lowest Rating: {df[rating_col].min():.2f}",
            }
        )
    else:
        other_nums = [c for c in num_cols if c != price_col]
        if other_nums:
            sec_col = other_nums[0]
            kpis.append(
                {
                    "label": f"Total {sec_col}",
                    "value": f"{df[sec_col].sum():,.0f}",
                    "detail": f"Average per record: {df[sec_col].mean():,.2f} | Maximum: {df[sec_col].max():,.2f}",
                }
            )
        elif price_col:
            kpis.append(
                {
                    "label": f"Total {price_col}",
                    "value": f"PKR {df[price_col].sum():,.0f}",
                    "detail": f"Median {price_col}: PKR {df[price_col].median():,.0f}",
                }
            )
        else:
            kpis.append(
                {
                    "label": "Unique Groups",
                    "value": f"{df[cat_cols[0]].nunique():,}" if cat_cols else "0",
                    "detail": f"Distinct categories in {cat_cols[0]}." if cat_cols else "No text columns.",
                }
            )

    name_col = find_column(
        df, ["competitor", "brand", "product", "category", "territory", "country", "region", "name"], numeric_only=False
    )
    share_col = find_column(df, ["share", "salesamount", "revenue", "sales", "price"], numeric_only=True)

    if name_col and share_col and "competitor_name" in [c.lower() for c in df.columns]:
        leader_row = df.loc[df[share_col].idxmax()]
        kpis.append(
            {
                "label": "Market Leader",
                "value": str(leader_row[name_col]),
                "detail": f"Leads with {leader_row[share_col]}% share | Strength: {leader_row.get('Key_Advantage', 'Top rank')}",
            }
        )
    elif name_col and not df[name_col].dropna().empty:
        vc = df[name_col].dropna().value_counts()
        top_name = str(vc.index[0])
        top_pct = (vc.iloc[0] / total_rows) * 100
        kpis.append(
            {
                "label": f"Top {name_col}",
                "value": top_name[:20],
                "detail": f"{vc.iloc[0]:,} records ({top_pct:.1f}% share of entire dataset).",
            }
        )
    else:
        kpis.append(
            {
                "label": "Dataset Columns",
                "value": str(total_cols),
                "detail": f"Fields: {', '.join(df.columns[:4])}",
            }
        )

    return kpis


def generate_smart_swot(df: pd.DataFrame) -> str:
    total_rows = len(df)
    if "Competitor_Name" in df.columns and "Price" in df.columns:
        avg_p = df["Price"].mean()
        min_row = df.loc[df["Price"].idxmin()]
        max_row = df.loc[df["Price"].idxmax()]
        top_rating = df.loc[df["Customer_Rating"].idxmax()] if "Customer_Rating" in df.columns else max_row
        leader = df.loc[df["Market_Share"].idxmax()] if "Market_Share" in df.columns else max_row

        return f"""
**Strengths**
* Tracks **{total_rows} active competitors** with a clear market average price of **PKR {avg_p:,.0f}**.
* **{top_rating['Competitor_Name']}** achieves the highest customer satisfaction (**{top_rating.get('Customer_Rating', 'N/A')} / 5.0**).
* **{leader['Competitor_Name']}** commands the largest market footprint at **{leader.get('Market_Share', 'N/A')}%** share.

**Weaknesses**
* **{max_row['Competitor_Name']}** faces the steepest entry barrier at **PKR {max_row['Price']:,.0f}**.
* Mid-market players face margin pressure from **{min_row['Competitor_Name']}** (**PKR {min_row['Price']:,.0f}**).
* Heavy share concentration among top players restricts smaller rivals.

**Opportunities**
* Capture value-driven buyers in the **PKR {min_row['Price']:,.0f} – PKR {avg_p:,.0f}** pricing sweet spot.
* Pair high customer ratings (**>4.5**) with warranty bundles to justify premium pricing.
* Target customers dissatisfied with low-cost, lower-rated competitors.

**Threats**
* Aggressive price cuts by **{min_row['Competitor_Name']}** could spark a sector-wide price war.
* Market leader **{leader['Competitor_Name']}** holds scale advantages in marketing and distribution.
* Rising price sensitivity may shift demand away from high-ticket offerings.

**Top 3 Strategic Actions**
1. **Optimize Core Price Around PKR {avg_p:,.0f}:** Stay competitive against average market pricing while adding service value.
2. **Promote Quality Leadership:** Use **{top_rating.get('Customer_Rating', 4.6)}/5.0** rating proof points in campaigns.
3. **Counter {leader['Competitor_Name']} in Key Segments:** Launch targeted loyalty offers to protect market share.
"""

    primary_col = find_column(df, ["salesamount", "price", "amount", "sales", "revenue"], numeric_only=True)
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    top_cat = str(df[cat_cols[0]].dropna().value_counts().index[0]) if cat_cols else "Primary Segment"
    top_cat_share = (df[cat_cols[0]].value_counts().iloc[0] / total_rows * 100) if cat_cols else 100.0
    p_mean = df[primary_col].mean() if primary_col else 0
    p_max = df[primary_col].max() if primary_col else 0
    p_sum = df[primary_col].sum() if primary_col else 0

    return f"""
**Strengths**
* Full dataset analysis across **{total_rows:,} records** and **{len(df.columns)} attributes**.
* Leading category **{top_cat}** accounts for **{top_cat_share:.1f}%** of total activity.
* Average **{primary_col or 'Metric'}** is **PKR {p_mean:,.2f}** with total cumulative volume of **PKR {p_sum:,.0f}**.

**Weaknesses**
* High reliance on **{top_cat}** creates concentration risk if segment demand slows.
* Large gap between average (**{p_mean:,.2f}**) and peak (**{p_max:,.2f}**) shows uneven order distribution.
* Adding direct competitor pricing columns would enable deeper price-war simulations.

**Opportunities**
* Replicate **{top_cat}** best practices across underperforming categories.
* Upsell mid-tier orders to raise average **{primary_col or 'Metric'}** above **PKR {p_mean:,.2f}**.
* Monitor high-value transactions across all **{total_rows:,} rows** for margin expansion.

**Threats**
* Any downturn in **{top_cat}** directly impacts total volume (**PKR {p_sum:,.0f}**).
* Competitive discounting in high-volume segments can erode profit margins.
* Seasonal demand swings require proactive inventory and pricing adjustments.

**Top 3 Strategic Actions**
1. **Safeguard Top Segment ({top_cat}):** Focus retention campaigns where **{top_cat_share:.1f}%** of volume originates.
2. **Boost Below-Average Tiers:** Offer bundled deals on items below **PKR {p_mean:,.2f}**.
3. **Track Weekly Benchmark Shifts:** Monitor **{primary_col or 'key metrics'}** continuously for early market signals.
"""


def scrape_competitor_page(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(url, headers=headers, timeout=12)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "N/A"
    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_desc = meta_tag["content"].strip()
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2"])[:6] if h.get_text(strip=True)]
    links_count = len(soup.find_all("a"))
    return {
        "title": title,
        "meta_desc": meta_desc or "No meta description exposed on landing page.",
        "headings": headings,
        "links_count": links_count,
    }


# --- SIDEBAR (LIGHT & CLEAN) ---
with st.sidebar:
    st.markdown(f"### :material/account_circle: Welcome, {st.session_state.current_user.title()}")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Tutorial", icon=":material/help:", use_container_width=True):
            st.session_state.show_tutorial = True
            st.rerun()
    with col_s2:
        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = ""
            st.rerun()

    st.divider()
    st.markdown("### :material/upload_file: Upload Market Data")
    uploaded_file = st.file_uploader("Choose CSV or Excel File", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            file_label = uploaded_file.name
            st.success(f"Active File: {file_label}")
        except Exception as e:
            st.error(f"File error: {e}")
            df = load_sample_data()
            file_label = "Default Benchmark"
    else:
        df = load_sample_data()
        file_label = "Default Benchmark"
        st.info("Showing Default Benchmark Data")

    sample_csv = load_sample_data().to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Sample Template",
        data=sample_csv,
        file_name="competitor_benchmark_template.csv",
        mime="text/csv",
        icon=":material/download:",
        use_container_width=True,
    )


# --- MAIN LIGHT EXECUTIVE DASHBOARD ---
st.markdown(
    """
    <div class="exec-header">
        <h1>AI-Powered Competitor Intelligence & Market Analysis</h1>
        <p>Clear Visual Benchmarking, Competitor Performance Breakdown & Strategic SWOT Insights</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- INTERACTIVE ONBOARDING TUTORIAL ---
if st.session_state.show_tutorial:
    st.markdown(
        """
        <div class="tutorial-box">
            <h4>Quick Guide — How This Dashboard Works</h4>
            <ul style="margin:0; padding-left:1.2rem; color:#334155; font-size:0.92rem; line-height:1.6;">
                <li><strong>Step 1 — Upload File (Left Sidebar):</strong> Upload any CSV or Excel dataset. All KPIs and graphs automatically adjust to your file.</li>
                <li><strong>Step 2 — Hover on KPI Cards:</strong> Move your mouse cursor over any KPI card below to see exact minimum, maximum, and total breakdowns.</li>
                <li><strong>Step 3 — Detailed Competitor Graphs:</strong> Open <em>Market Analytics & Graphs</em> to inspect competitor rankings, market average lines, share %, and positioning quadrants.</li>
                <li><strong>Step 4 — SWOT & Live Web Analyzer:</strong> Generate an instant SWOT report or analyze any competitor's live website URL.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Got it, Hide Guide", icon=":material/check_circle:"):
        st.session_state.show_tutorial = False
        st.rerun()

# --- FILE-ADAPTIVE HOVER KPI CARDS ---
kpis = build_adaptive_kpis(df, file_label)
kpi_cols = st.columns(4)
for idx, kpi in enumerate(kpis):
    with kpi_cols[idx]:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-value">{kpi['value']}</div>
                <div class="kpi-hint">Hover cursor for full details</div>
                <div class="kpi-detail-box">{kpi['detail']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# --- NAVIGATION TABS ---
tab_overview, tab_swot, tab_scraper = st.tabs(
    [
        ":material/monitoring: Market Analytics & Detailed Graphs",
        ":material/psychology: Executive SWOT Report",
        ":material/language: Live Web Intelligence",
    ]
)

# --- TAB 1: COMPREHENSIVE, ACCURATE COMPETITOR GRAPHS & ANALYSIS ---
with tab_overview:
    cat_col = find_column(
        df, ["competitor", "brand", "product", "category", "territory", "country", "name"], numeric_only=False
    )
    num_cols = df.select_dtypes(include="number").columns.tolist()
    default_val = find_column(df, ["price", "salesamount", "amount", "sales", "revenue"], numeric_only=True)

    # Interactive Metric Selector so user can analyze ANY numeric column in their file
    ctrl1, ctrl2 = st.columns([2, 1])
    with ctrl1:
        st.subheader(":material/analytics: Deep Competitor & Market Visual Analysis")
        st.caption("Hover over any bar, slice, or point in the graphs below for exact figures and comparisons.")
    with ctrl2:
        selected_metric = (
            st.selectbox(
                "Select Metric to Analyze:",
                options=num_cols,
                index=num_cols.index(default_val) if default_val in num_cols else 0,
            )
            if num_cols
            else None
        )

    light_palette = ["#059669", "#0284C7", "#D97706", "#7C3AED", "#E11D48", "#0D9488", "#2563EB"]

    if cat_col and selected_metric:
        # Prepare clean aggregated summary per competitor/category
        summary_df = (
            df.groupby(cat_col, as_index=False)
            .agg(
                Average_Value=(selected_metric, "mean"),
                Total_Value=(selected_metric, "sum"),
                Record_Count=(selected_metric, "count"),
            )
            .sort_values("Total_Value", ascending=False)
            .head(12)
        )
        overall_avg = summary_df["Average_Value"].mean()
        total_sum = summary_df["Total_Value"].sum()
        summary_df["Market_Share_%"] = (summary_df["Total_Value"] / total_sum * 100).round(2) if total_sum else 0
        summary_df["Vs_Market_Avg_%"] = (
            ((summary_df["Average_Value"] - overall_avg) / overall_avg * 100).round(1) if overall_avg else 0
        )

        # ROW 1: Detailed Bar Comparison with Market Average Line + Exact Share Donut
        g1, g2 = st.columns([1.35, 1])

        with g1:
            fig_bar = px.bar(
                summary_df,
                x=cat_col,
                y="Average_Value",
                text="Average_Value",
                color=cat_col,
                title=f"1. Competitor Comparison: Average {selected_metric} (with Market Benchmark Line)",
                labels={"Average_Value": f"Average {selected_metric}", cat_col: "Competitor / Segment"},
                color_discrete_sequence=light_palette,
                hover_data={"Total_Value": ":,.0f", "Market_Share_%": ":.1f", "Vs_Market_Avg_%": "+.1f"},
            )
            fig_bar.update_traces(texttemplate="%{text:,.1f}", textposition="outside")
            fig_bar.add_hline(
                y=overall_avg,
                line_dash="dash",
                line_color="#DC2626",
                annotation_text=f"Market Avg: {overall_avg:,.1f}",
                annotation_position="top right",
            )
            fig_bar.update_layout(
                showlegend=False,
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(color="#1E293B"),
                yaxis=dict(gridcolor="#F1F5F9"),
                margin=dict(t=55, b=30),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with g2:
            fig_pie = px.pie(
                summary_df,
                names=cat_col,
                values="Total_Value",
                hole=0.45,
                title=f"2. Market Share Breakdown by {selected_metric} (%)",
                color_discrete_sequence=light_palette,
            )
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Total: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
            )
            fig_pie.update_layout(
                paper_bgcolor="#FFFFFF",
                font=dict(color="#1E293B"),
                margin=dict(t=55, b=30),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # ROW 2: Strategic Positioning Quadrant + Multi-Metric Comparison
        g3, g4 = st.columns(2)

        with g3:
            if len(num_cols) >= 2:
                x_col = num_cols[0]
                y_col = num_cols[1]
                scatter_df = df.head(500).copy()
                fig_quad = px.scatter(
                    scatter_df,
                    x=x_col,
                    y=y_col,
                    color=cat_col,
                    size=num_cols[2] if len(num_cols) >= 3 and (scatter_df[num_cols[2]] > 0).all() else None,
                    title=f"3. Strategic Positioning Matrix: {x_col} vs. {y_col}",
                    color_discrete_sequence=light_palette,
                    hover_data=num_cols[:4],
                )
                fig_quad.add_vline(x=scatter_df[x_col].mean(), line_dash="dot", line_color="#94A3B8")
                fig_quad.add_hline(y=scatter_df[y_col].mean(), line_dash="dot", line_color="#94A3B8")
                fig_quad.update_layout(
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    font=dict(color="#1E293B"),
                    xaxis=dict(gridcolor="#F1F5F9"),
                    yaxis=dict(gridcolor="#F1F5F9"),
                )
                st.plotly_chart(fig_quad, use_container_width=True)
            else:
                fig_hist = px.histogram(
                    df,
                    x=selected_metric,
                    nbins=20,
                    title=f"3. Value Distribution of {selected_metric}",
                    color_discrete_sequence=["#059669"],
                )
                fig_hist.update_layout(plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
                st.plotly_chart(fig_hist, use_container_width=True)

        with g4:
            # Multi-metric normalized comparison across top competitors
            comp_metrics = num_cols[:3]
            multi_df = df.groupby(cat_col, as_index=False)[comp_metrics].mean().head(8)
            melted_df = multi_df.melt(id_vars=cat_col, value_vars=comp_metrics, var_name="Metric", value_name="Value")
            fig_grouped = px.bar(
                melted_df,
                x=cat_col,
                y="Value",
                color="Metric",
                barmode="group",
                title="4. Multi-Metric Competitor Side-by-Side Comparison",
                color_discrete_sequence=["#059669", "#0284C7", "#D97706"],
            )
            fig_grouped.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(color="#1E293B"),
                yaxis=dict(gridcolor="#F1F5F9"),
            )
            st.plotly_chart(fig_grouped, use_container_width=True)

        # ROW 3: Accurate Competitor-by-Competitor Scorecard Table
        st.subheader(":material/leaderboard: Competitor Performance Scorecard")
        scorecard = summary_df.copy()
        scorecard.insert(0, "Rank", range(1, len(scorecard) + 1))
        scorecard["Positioning"] = scorecard["Vs_Market_Avg_%"].apply(
            lambda x: "Above Market Avg" if x > 0 else ("At Market Avg" if x == 0 else "Below Market Avg")
        )
        st.dataframe(scorecard, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader(":material/table_view: Raw Dataset Preview (Top 500 Records)")
    st.dataframe(df.head(500), use_container_width=True, hide_index=True)

# --- TAB 2: EXECUTIVE SWOT REPORT ---
with tab_swot:
    st.subheader(":material/psychology: Executive SWOT & Strategic Action Plan")
    st.caption("Generates a clear, data-backed strategic summary tailored to your active dataset.")

    if st.button("Generate Concise SWOT Report", icon=":material/auto_awesome:"):
        swot_output = generate_smart_swot(df)
        st.markdown(swot_output)

# --- TAB 3: LIVE WEB SCRAPER INTELLIGENCE ---
with tab_scraper:
    st.subheader(":material/language: Live Competitor Website Analyzer")
    st.caption("Extract live positioning, headlines, and link footprint from any public competitor URL.")

    target_url = st.text_input("Competitor Website URL", placeholder="https://www.example.com")
    if st.button("Analyze Live Webpage", icon=":material/travel_explore:"):
        if not target_url.startswith("http"):
            st.warning("Please enter a valid URL starting with http:// or https://")
        else:
            with st.spinner("Extracting live webpage intelligence..."):
                try:
                    info = scrape_competitor_page(target_url)
                    headings_str = " | ".join(info["headings"]) if info["headings"] else "No H1/H2 headlines detected"
                    st.markdown(
                        f"""
                        **Executive Webpage Intelligence Brief**
                        * **Brand / Page Title:** {info['title']}
                        * **Core Positioning:** {info['meta_desc']}
                        * **Primary Headlines:** {headings_str}
                        * **Navigation Footprint:** {info['links_count']} internal/external links detected
                        * **Recommended Counter-Strategy:** Benchmark landing-page value propositions and differentiate on warranty, delivery speed, and transparent pricing.
                        """
                    )
                except Exception as e:
                    st.error(f"Extraction failed: {e}")
