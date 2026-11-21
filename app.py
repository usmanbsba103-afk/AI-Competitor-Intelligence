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

# --- CUSTOM ROYAL GREEN & WHITE EXECUTIVE STYLING ---
st.markdown(
    """
    <style>
        .stApp {
            background-color: #FFFFFF;
            color: #0F291E;
        }
        [data-testid="stSidebar"] {
            background-color: #F2F8F5;
            border-right: 1px solid #D5E8DF;
        }
        .exec-header {
            background: linear-gradient(135deg, #0B4F32 0%, #146C43 100%);
            padding: 1.5rem 2rem;
            border-radius: 10px;
            color: #FFFFFF;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(11, 79, 50, 0.12);
        }
        .exec-header h1 {
            color: #FFFFFF !important;
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0;
        }
        .exec-header p {
            color: #E2F1EA !important;
            font-size: 0.95rem;
            margin: 0.4rem 0 0 0;
        }
        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #D5E8DF;
            border-left: 5px solid #0B4F32;
            padding: 1rem 1.2rem;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(15, 41, 30, 0.04);
        }
        .stButton > button {
            background-color: #0B4F32 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.2rem !important;
        }
        .stButton > button:hover {
            background-color: #083B25 !important;
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


# --- AUTHENTICATION PORTAL ---
def render_login_portal():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown(
            """
            <div class="exec-header" style="text-align:center; margin-top:2rem;">
                <h1>Competitor Intelligence Portal</h1>
                <p>Enterprise Market Analytics & Strategic Benchmarking System</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted:
                    if username in st.session_state.users_db and st.session_state.users_db[username] == password:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Use demo account: admin / fyp2026")
            st.caption("Demo Access — Username: `admin` | Password: `fyp2026`")

        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                reg_submit = st.form_submit_button("Register Account", use_container_width=True)
                if reg_submit:
                    if new_user and new_pass:
                        if new_user in st.session_state.users_db:
                            st.warning("Username already exists.")
                        else:
                            st.session_state.users_db[new_user] = new_pass
                            st.success("Account created. Please switch to Sign In.")
                    else:
                        st.warning("Please complete both fields.")


if not st.session_state.authenticated:
    render_login_portal()
    st.stop()


# --- SMART COLUMN DETECTOR & DATA ENGINE ---
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


def compute_smart_kpis(df: pd.DataFrame):
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    # 1. Price / Amount KPI
    price_col = find_column(df, ["price", "salesamount", "amount", "sales", "revenue", "cost"], numeric_only=True)
    if price_col:
        avg_val = df[price_col].mean()
        kpi2_label = f"Average {price_col}"
        kpi2_value = f"PKR {avg_val:,.0f}"
    else:
        kpi2_label = "Numeric Columns"
        kpi2_value = str(len(num_cols))

    # 2. Rating / Volume KPI
    rating_col = find_column(df, ["rating", "score", "review"], numeric_only=True)
    if rating_col and ("rating" in rating_col.lower() or "score" in rating_col.lower()):
        kpi3_label = "Average Customer Rating"
        kpi3_value = f"{df[rating_col].mean():.2f} / 5.0"
    elif len(num_cols) > 1:
        second_col = [c for c in num_cols if c != price_col][0]
        kpi3_label = f"Total {second_col}"
        kpi3_value = f"{df[second_col].sum():,.0f}"
    elif price_col:
        kpi3_label = f"Total {price_col}"
        kpi3_value = f"PKR {df[price_col].sum():,.0f}"
    else:
        kpi3_label = "Total Attributes"
        kpi3_value = str(len(df.columns))

    # 3. Leader / Top Category KPI
    name_col = find_column(df, ["competitor", "brand", "product", "category", "territory", "country", "name"], numeric_only=False)
    share_col = find_column(df, ["share", "salesamount", "sales", "revenue", "price"], numeric_only=True)

    if name_col and share_col and "competitor_name" in [c.lower() for c in df.columns]:
        leader = df.loc[df[share_col].idxmax(), name_col]
        kpi4_label = "Market Share Leader"
        kpi4_value = str(leader)
    elif name_col:
        top_item = df[name_col].dropna().value_counts().index[0]
        kpi4_label = f"Top {name_col}"
        kpi4_value = str(top_item)[:22]
    elif cat_cols:
        top_item = df[cat_cols[0]].dropna().value_counts().index[0]
        kpi4_label = f"Top {cat_cols[0]}"
        kpi4_value = str(top_item)[:22]
    else:
        kpi4_label = "Dataset Columns"
        kpi4_value = str(len(df.columns))

    return kpi2_label, kpi2_value, kpi3_label, kpi3_value, kpi4_label, kpi4_value


def generate_smart_swot(df: pd.DataFrame) -> str:
    total_rows = len(df)
    num_cols = df.select_dtypes(include="number").columns.tolist()

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
    if st.button("Sign Out", icon=":material/logout:", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.rerun()

    st.divider()
    st.markdown("### :material/database: Market Dataset")
    uploaded_file = st.file_uploader("Upload Competitor Data (.csv / .xlsx)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("Dataset loaded successfully.")
        except Exception as e:
            st.error(f"File error: {e}")
            df = load_sample_data()
    else:
        df = load_sample_data()
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
        <p>Automated Competitive Benchmarking, Pricing Analytics & Strategic SWOT Synthesis</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# DYNAMIC KPI SUMMARY ROW (WORKS FOR ANY DATASET)
k2_lbl, k2_val, k3_lbl, k3_val, k4_lbl, k4_val = compute_smart_kpis(df)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Tracked Records", f"{len(df):,}")
k2.metric(k2_lbl, k2_val)
k3.metric(k3_lbl, k3_val)
k4.metric(k4_lbl, k4_val)

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
    green_palette = ["#0B4F32", "#198754", "#2E9E6B", "#52B788", "#95D5B2"]

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

# TAB 2: EXECUTIVE SWOT REPORT (INSTANT & ZERO-ERROR)
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
