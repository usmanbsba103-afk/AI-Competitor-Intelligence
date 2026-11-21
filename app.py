import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Competitor Intelligence & Market Analysis",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- UPGRADED LUXURY ROYAL EMERALD & GOLD-ACCENTED EXECUTIVE THEME ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .stApp {
            background: linear-gradient(180deg, #F6FBF8 0%, #FFFFFF 35%);
            color: #0B251A;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #093D26 0%, #0B4F32 100%);
            border-right: 1px solid #146C43;
        }
        [data-testid="stSidebar"] * {
            color: #F0FAF5 !important;
        }
        [data-testid="stSidebar"] .stFileUploader section {
            background-color: rgba(255, 255, 255, 0.08) !important;
            border: 1px dashed #6EE7B7 !important;
            border-radius: 10px;
        }
        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] .stDownloadButton > button {
            background-color: #10B981 !important;
            color: #052E1C !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover,
        [data-testid="stSidebar"] .stDownloadButton > button:hover {
            background-color: #34D399 !important;
            transform: translateY(-1px);
        }

        /* Executive Banner */
        .exec-header {
            background: linear-gradient(120deg, #063722 0%, #0B4F32 55%, #157347 100%);
            padding: 1.8rem 2.2rem;
            border-radius: 14px;
            color: #FFFFFF;
            margin-bottom: 1.5rem;
            border-bottom: 4px solid #D4AF37;
            box-shadow: 0 10px 25px rgba(11, 79, 50, 0.16);
        }
        .exec-header h1 {
            color: #FFFFFF !important;
            font-size: 1.95rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0;
        }
        .exec-header p {
            color: #D1FAE5 !important;
            font-size: 0.98rem;
            margin: 0.45rem 0 0 0;
        }

        /* Interactive Hover KPI Cards */
        .kpi-card {
            position: relative;
            background: #FFFFFF;
            border: 1px solid #D1E7DD;
            border-left: 5px solid #0B4F32;
            border-radius: 12px;
            padding: 1.15rem 1.3rem;
            box-shadow: 0 4px 12px rgba(11, 79, 50, 0.05);
            transition: all 0.28s cubic-bezier(0.25, 0.8, 0.25, 1);
            cursor: pointer;
            overflow: hidden;
            min-height: 128px;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            border-color: #10B981;
            border-left: 6px solid #D4AF37;
            background: linear-gradient(135deg, #FFFFFF 0%, #ECFDF5 100%);
            box-shadow: 0 14px 28px rgba(11, 79, 50, 0.16);
        }
        .kpi-label {
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #3B6E57;
            margin-bottom: 0.35rem;
        }
        .kpi-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #083B25;
            line-height: 1.2;
        }
        .kpi-hint {
            font-size: 0.76rem;
            color: #6B9080;
            margin-top: 0.4rem;
        }
        .kpi-detail-box {
            max-height: 0;
            opacity: 0;
            overflow: hidden;
            transition: all 0.3s ease;
            font-size: 0.82rem;
            color: #064E3B;
            background: #D1FAE5;
            border-radius: 6px;
            padding: 0 0.6rem;
            margin-top: 0;
        }
        .kpi-card:hover .kpi-detail-box {
            max-height: 90px;
            opacity: 1;
            padding: 0.45rem 0.65rem;
            margin-top: 0.55rem;
        }
        .kpi-card:hover .kpi-hint {
            display: none;
        }

        /* Tutorial Card */
        .tutorial-box {
            background: linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%);
            border: 1px solid #6EE7B7;
            border-left: 6px solid #10B981;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.08);
        }
        .tutorial-box h4 {
            margin: 0 0 0.5rem 0;
            color: #064E3B;
            font-weight: 800;
        }

        /* Primary Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #0B4F32 0%, #146C43 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.3rem !important;
            box-shadow: 0 4px 10px rgba(11, 79, 50, 0.15) !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #083B25 0%, #0B4F32 100%) !important;
            transform: translateY(-1px);
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
                <p>Enterprise Market Analytics & Strategic Benchmarking System</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tab_login, tab_register = st.tabs(["Sign In", "Create Account (Instant Access)"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In to Dashboard", use_container_width=True)
                if submitted:
                    if username in st.session_state.users_db and st.session_state.users_db[username] == password:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.session_state.show_tutorial = True
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Use demo account: admin / fyp2026")
            st.caption("Quick Demo Login — Username: `admin` | Password: `fyp2026`")

        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username", placeholder="e.g., usman_analyst")
                new_pass = st.text_input("Create Password", type="password", placeholder="Enter strong password")
                reg_submit = st.form_submit_button("Create Account & Login Directly", use_container_width=True)
                if reg_submit:
                    if new_user.strip() and new_pass.strip():
                        if new_user in st.session_state.users_db:
                            st.warning("This username is already taken. Please sign in or pick another.")
                        else:
                            st.session_state.users_db[new_user.strip()] = new_pass.strip()
                            st.session_state.authenticated = True
                            st.session_state.current_user = new_user.strip()
                            st.session_state.show_tutorial = True
                            st.rerun()
                    else:
                        st.warning("Please enter both a username and password.")


if not st.session_state.authenticated:
    render_login_portal()
    st.stop()


# --- SMART DATA & FILE-ADAPTIVE KPI ENGINE ---
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
    """Dynamically builds 4 tailored KPI cards with rich hover breakdowns based on uploaded file."""
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    total_rows = len(df)
    total_cols = len(df.columns)

    # KPI 1: Dataset Scale
    kpis = [
        {
            "label": "Tracked Records",
            "value": f"{total_rows:,}",
            "detail": f"Source: {file_label} | {total_cols} total columns ({len(num_cols)} numeric, {len(cat_cols)} text).",
        }
    ]

    # KPI 2: Primary Monetary / Price / Sales Metric
    price_col = find_column(
        df, ["price", "salesamount", "revenue", "amount", "sales", "cost", "profit"], numeric_only=True
    )
    if price_col:
        avg_v = df[price_col].mean()
        min_v = df[price_col].min()
        max_v = df[price_col].max()
        kpis.append(
            {
                "label": f"Avg {price_col}",
                "value": f"PKR {avg_v:,.0f}",
                "detail": f"Min: PKR {min_v:,.0f} | Max: PKR {max_v:,.0f} | Total: PKR {df[price_col].sum():,.0f}",
            }
        )
    else:
        kpis.append(
            {
                "label": "Data Completeness",
                "value": f"{(1 - df.isna().mean().mean()) * 100:.1f}%",
                "detail": f"Non-null cell coverage across all {total_rows:,} records.",
            }
        )

    # KPI 3: Rating / Secondary Numeric Metric
    rating_col = find_column(df, ["rating", "score", "review", "satisfaction"], numeric_only=True)
    if rating_col and any(k in rating_col.lower() for k in ["rating", "score", "review", "satisfaction"]):
        kpis.append(
            {
                "label": f"Avg {rating_col}",
                "value": f"{df[rating_col].mean():.2f} / 5.0",
                "detail": f"Highest: {df[rating_col].max():.2f} | Lowest: {df[rating_col].min():.2f} across dataset.",
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
                    "detail": f"Mean per record: {df[sec_col].mean():,.2f} | Peak value: {df[sec_col].max():,.2f}",
                }
            )
        elif price_col:
            kpis.append(
                {
                    "label": f"Cumulative {price_col}",
                    "value": f"PKR {df[price_col].sum():,.0f}",
                    "detail": f"Median {price_col}: PKR {df[price_col].median():,.0f}",
                }
            )
        else:
            kpis.append(
                {
                    "label": "Unique Categories",
                    "value": f"{df[cat_cols[0]].nunique():,}" if cat_cols else "0",
                    "detail": f"Distinct groups found in {cat_cols[0]}." if cat_cols else "No categorical columns.",
                }
            )

    # KPI 4: Dominant Entity / Market Leader
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
                "detail": f"Leads with {leader_row[share_col]}% share | Advantage: {leader_row.get('Key_Advantage', 'Top position')}",
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
                "detail": f"Appears in {vc.iloc[0]:,} records ({top_pct:.1f}% of total dataset).",
            }
        )
    else:
        kpis.append(
            {
                "label": "Active Columns",
                "value": str(total_cols),
                "detail": f"Attributes: {', '.join(df.columns[:4])}...",
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
* Benchmark tracks **{total_rows} competitors** with an average market price of **PKR {avg_p:,.0f}**.
* **{top_rating['Competitor_Name']}** leads customer satisfaction with a **{top_rating.get('Customer_Rating', 'N/A')} / 5.0** rating.
* **{leader['Competitor_Name']}** holds the strongest market position at **{leader.get('Market_Share', 'N/A')}%** share.

**Weaknesses**
* **{max_row['Competitor_Name']}** carries the highest price barrier at **PKR {max_row['Price']:,.0f}**.
* Mid-tier brands face margin compression against **{min_row['Competitor_Name']}** (**PKR {min_row['Price']:,.0f}**).
* High concentration among top two players leaves smaller competitors vulnerable.

**Opportunities**
* Capture value-conscious buyers in the **PKR {min_row['Price']:,.0f} – PKR {avg_p:,.0f}** mid-price corridor.
* Leverage high customer ratings (**>4.5**) to justify value-added bundles and warranties.
* Target underserved segments where low-cost rivals suffer lower satisfaction scores.

**Threats**
* Aggressive discounting by **{min_row['Competitor_Name']}** risks triggering a sector-wide price war.
* Market leader **{leader['Competitor_Name']}** can use scale to outspend rivals on acquisition.
* Shifting customer sensitivity toward lower entry pricing may erode premium margins.

**Top 3 Strategic Actions**
1. **Anchor Pricing Near PKR {avg_p:,.0f}:** Position core offerings slightly below average market price with bundled support.
2. **Differentiate on Quality:** Highlight superior rating benchmarks (**{top_rating.get('Customer_Rating', 4.6)}/5.0**) against discount competitors.
3. **Defend Share Against {leader['Competitor_Name']}:** Launch targeted retention campaigns in high-volume sales tiers.
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
* Comprehensive dataset covering **{total_rows:,} records** across **{len(df.columns)} attributes**.
* Dominant segment **{top_cat}** drives **{top_cat_share:.1f}%** of total operational volume.
* Average **{primary_col or 'Metric'}** is **PKR {p_mean:,.2f}** with total volume reaching **PKR {p_sum:,.0f}**.

**Weaknesses**
* High dependency on **{top_cat}** creates concentration risk if demand shifts.
* Wide gap between average (**{p_mean:,.2f}**) and peak (**{p_max:,.2f}**) indicates uneven order values.
* Missing direct competitor price columns limits head-to-head price-elasticity modeling.

**Opportunities**
* Expand high-performing **{top_cat}** strategies into under-penetrated secondary segments.
* Optimize mid-tier transactions to lift average **{primary_col or 'Metric'}** above **{p_mean:,.2f}**.
* Use automated anomaly tracking across all **{total_rows:,} rows** to capture high-margin orders.

**Threats**
* Demand slowdown in **{top_cat}** would disproportionately impact cumulative revenue (**PKR {p_sum:,.0f}**).
* Competitive undercutting in high-frequency segments could compress unit margins.
* Seasonal volatility across large transaction volumes requires proactive inventory alignment.

**Top 3 Strategic Actions**
1. **Protect Core Segment ({top_cat}):** Prioritize retention and upselling where **{top_cat_share:.1f}%** of activity occurs.
2. **Lift Underperforming Tiers:** Target records below the **{p_mean:,.2f}** benchmark with bundled incentives.
3. **Automate Weekly KPI Audits:** Track shifts across **{primary_col or 'key metrics'}** to detect market changes early.
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


# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### :material/account_circle: {st.session_state.current_user.title()}")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Guide", icon=":material/help:", use_container_width=True):
            st.session_state.show_tutorial = True
            st.rerun()
    with col_s2:
        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = ""
            st.rerun()

    st.divider()
    st.markdown("### :material/database: Market Dataset")
    uploaded_file = st.file_uploader("Upload Dataset (.csv / .xlsx)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            file_label = uploaded_file.name
            st.success(f"Loaded: {file_label}")
        except Exception as e:
            st.error(f"File error: {e}")
            df = load_sample_data()
            file_label = "Default Benchmark"
    else:
        df = load_sample_data()
        file_label = "Default Benchmark"
        st.info("Using default benchmark dataset")

    sample_csv = load_sample_data().to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV Template",
        data=sample_csv,
        file_name="competitor_benchmark_template.csv",
        mime="text/csv",
        icon=":material/download:",
        use_container_width=True,
    )


# --- MAIN EXECUTIVE DASHBOARD ---
st.markdown(
    """
    <div class="exec-header">
        <h1>AI-Powered Competitor Intelligence & Market Analysis</h1>
        <p>Automated Competitive Benchmarking, Adaptive KPI Analytics & Strategic SWOT Synthesis</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 2. INTERACTIVE ONBOARDING TUTORIAL ---
if st.session_state.show_tutorial:
    st.markdown(
        """
        <div class="tutorial-box">
            <h4>Quick-Start Platform Tour — Welcome!</h4>
            <p style="margin-bottom:0.5rem; color:#065F46;">
                Here is how to get the most out of your Competitor Intelligence Dashboard in 4 quick steps:
            </p>
            <ul style="margin:0; padding-left:1.2rem; color:#064E3B; font-size:0.92rem;">
                <li><strong>1. Upload Any Dataset (Left Sidebar):</strong> Upload any CSV or Excel file — KPIs and charts automatically adapt to your file's columns.</li>
                <li><strong>2. Hover Over KPI Cards Below:</strong> Move your cursor over any KPI card to highlight it and inspect min, max, and cumulative details.</li>
                <li><strong>3. Market Analytics & Charts:</strong> Explore interactive price comparisons, scatter positioning, and market share breakdowns.</li>
                <li><strong>4. Executive SWOT & Live Web Scraper:</strong> Generate an instant strategic SWOT report or analyze any live competitor website URL.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Got it, Hide Tutorial", icon=":material/check_circle:"):
        st.session_state.show_tutorial = False
        st.rerun()

# --- 3. FILE-ADAPTIVE HOVER KPI CARDS ---
kpis = build_adaptive_kpis(df, file_label)
kpi_cols = st.columns(4)
for idx, kpi in enumerate(kpis):
    with kpi_cols[idx]:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-value">{kpi['value']}</div>
                <div class="kpi-hint">Hover cursor for breakdown</div>
                <div class="kpi-detail-box">{kpi['detail']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# NAVIGATION TABS
tab_overview, tab_swot, tab_scraper = st.tabs(
    [
        ":material/bar_chart: Market Analytics & Charts",
        ":material/psychology: Executive AI SWOT",
        ":material/language: Live Web Intelligence",
    ]
)

# TAB 1: CHARTS & DATA TABLE
with tab_overview:
    st.subheader(":material/table_view: Competitive Benchmark Matrix")
    st.dataframe(df.head(500), use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    green_palette = ["#0B4F32", "#157347", "#10B981", "#34D399", "#D4AF37"]

    cat_col = find_column(df, ["competitor", "product", "category", "territory", "country", "name"], numeric_only=False)
    val_col = find_column(df, ["price", "salesamount", "amount", "sales", "revenue"], numeric_only=True)
    num_cols = df.select_dtypes(include="number").columns.tolist()

    with c1:
        if cat_col and val_col:
            chart_df = df.groupby(cat_col, as_index=False)[val_col].mean().head(10)
            fig_price = px.bar(
                chart_df,
                x=cat_col,
                y=val_col,
                title=f"Average {val_col} by {cat_col}",
                color=cat_col,
                color_discrete_sequence=green_palette,
            )
            fig_price.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_price, use_container_width=True)

    with c2:
        if len(num_cols) >= 2:
            sample_scatter = df.head(500)
            fig_scatter = px.scatter(
                sample_scatter,
                x=num_cols[0],
                y=num_cols[1],
                color=cat_col if cat_col else None,
                title=f"{num_cols[0]} vs. {num_cols[1]}",
                color_discrete_sequence=green_palette,
            )
            fig_scatter.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_scatter, use_container_width=True)

    with c3:
        if cat_col and val_col:
            pie_df = df.groupby(cat_col, as_index=False)[val_col].sum().head(8)
            fig_share = px.pie(
                pie_df,
                names=cat_col,
                values=val_col,
                hole=0.45,
                title=f"{val_col} Distribution",
                color_discrete_sequence=green_palette,
            )
            fig_share.update_layout(paper_bgcolor="white")
            st.plotly_chart(fig_share, use_container_width=True)

# TAB 2: EXECUTIVE SWOT REPORT
with tab_swot:
    st.subheader(":material/psychology: Executive AI SWOT & Action Plan")
    st.caption("Generates a concise, boardroom-ready strategic synthesis directly from your dataset.")

    if st.button("Generate Concise SWOT Report", icon=":material/auto_awesome:"):
        swot_output = generate_smart_swot(df)
        st.markdown(swot_output)

# TAB 3: LIVE WEB SCRAPER INTELLIGENCE
with tab_scraper:
    st.subheader(":material/language: Live Competitor Website Analyzer")
    st.caption("Extract live positioning, headlines, and structure from any public competitor URL.")

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
