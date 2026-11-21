import sqlite3
import hashlib
import time
import re
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

# --- PERSISTENT SQLITE USER DATABASE ---
DB_PATH = "users_auth.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            full_name TEXT
        )
        """
    )
    # Ensure default demo account exists
    demo_hash = hashlib.sha256("fyp2026".encode()).hexdigest()
    c.execute(
        "INSERT OR IGNORE INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
        ("admin", demo_hash, "Admin Analyst"),
    )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode()).hexdigest()


def register_user(username: str, password: str, full_name: str = "") -> tuple[bool, str]:
    uname = username.strip().lower()
    if not uname or not password.strip():
        return False, "Username and password cannot be empty."
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username = ?", (uname,))
    if c.fetchone():
        conn.close()
        return False, "This username is already registered. Please switch to Sign In."
    c.execute(
        "INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
        (uname, hash_password(password), full_name.strip() or uname.title()),
    )
    conn.commit()
    conn.close()
    return True, "Account permanently saved!"


def verify_user(username: str, password: str) -> tuple[bool, str]:
    uname = username.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash, full_name FROM users WHERE username = ?", (uname,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True, row[1] or uname.title()
    return False, ""


init_db()

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

        /* Executive Header */
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
            font-size: 1.55rem;
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

        /* Tutorial Box */
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

        /* SWOT Cards */
        .swot-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
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
if "display_name" not in st.session_state:
    st.session_state.display_name = ""
if "show_tutorial" not in st.session_state:
    st.session_state.show_tutorial = True


# --- 1. PERSISTENT LOGIN & DIRECT SIGN-UP PORTAL ---
def render_login_portal():
    col1, col2, col3 = st.columns([1, 1.45, 1])
    with col2:
        st.markdown(
            """
            <div class="exec-header" style="text-align:center; margin-top:1.5rem;">
                <h1>Competitor Intelligence Portal</h1>
                <p>Persistent Account Access & Automated Market Analytics</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tab_login, tab_register = st.tabs(["Sign In (Existing Account)", "Create New Account"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your saved username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In to Dashboard", use_container_width=True)
                if submitted:
                    ok, dname = verify_user(username, password)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username.strip().lower()
                        st.session_state.display_name = dname
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please check your credentials or create an account.")
            st.caption("Default Demo Login — Username: `admin` | Password: `fyp2026`")

        with tab_register:
            with st.form("register_form"):
                full_name = st.text_input("Full Name", placeholder="e.g., Muhammad Usman")
                new_user = st.text_input("Choose Username", placeholder="e.g., usman123")
                new_pass = st.text_input("Create Password", type="password", placeholder="Choose a password")
                reg_submit = st.form_submit_button("Create Account & Login Directly", use_container_width=True)
                if reg_submit:
                    ok, msg = register_user(new_user, new_pass, full_name)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.current_user = new_user.strip().lower()
                        st.session_state.display_name = full_name.strip() or new_user.strip().title()
                        st.session_state.show_tutorial = True
                        st.rerun()
                    else:
                        st.warning(msg)


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
            "detail": f"Source: {file_label} | {total_cols} columns ({len(num_cols)} numeric, {len(cat_cols)} text).",
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
                "detail": f"Min: PKR {min_v:,.0f} | Max: PKR {max_v:,.0f} | Total: PKR {df[price_col].sum():,.0f}",
            }
        )
    else:
        kpis.append(
            {
                "label": "Data Completeness",
                "value": f"{(1 - df.isna().mean().mean()) * 100:.1f}%",
                "detail": f"Complete non-null values across all {total_rows:,} records.",
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
                    "detail": f"Mean per record: {df[sec_col].mean():,.2f} | Peak: {df[sec_col].max():,.2f}",
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
                "detail": f"Leads with {leader_row[share_col]}% share | Advantage: {leader_row.get('Key_Advantage', 'Top rank')}",
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


# --- COMPREHENSIVE, DEEP DATA-DRIVEN SWOT ENGINE ---
def generate_comprehensive_swot(df: pd.DataFrame) -> dict:
    total_rows = len(df)
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    cat_col = find_column(
        df, ["competitor", "brand", "product", "category", "territory", "country", "name"], numeric_only=False
    )
    primary_metric = find_column(
        df, ["price", "salesamount", "revenue", "amount", "sales", "cost"], numeric_only=True
    )
    rating_metric = find_column(df, ["rating", "score", "review", "satisfaction"], numeric_only=True)
    share_metric = find_column(df, ["share", "monthly_sales", "quantity", "volume", "units"], numeric_only=True)

    # Aggregate by main category/competitor if available
    if cat_col and primary_metric:
        agg_dict = {primary_metric: ["mean", "sum", "min", "max", "count"]}
        if rating_metric and rating_metric != primary_metric:
            agg_dict[rating_metric] = "mean"
        if share_metric and share_metric not in [primary_metric, rating_metric]:
            agg_dict[share_metric] = "sum"

        grouped = df.groupby(cat_col).agg(agg_dict)
        grouped.columns = ["_".join(col).strip() for col in grouped.columns.values]
        grouped = grouped.reset_index()

        mean_col = f"{primary_metric}_mean"
        sum_col = f"{primary_metric}_sum"
        cnt_col = f"{primary_metric}_count"

        grouped = grouped.sort_values(sum_col, ascending=False)
        top_player = grouped.iloc[0]
        bottom_player = grouped.iloc[-1]
        highest_avg_player = grouped.loc[grouped[mean_col].idxmax()]
        lowest_avg_player = grouped.loc[grouped[mean_col].idxmin()]

        overall_avg = df[primary_metric].mean()
        overall_median = df[primary_metric].median()
        overall_sum = df[primary_metric].sum()
        overall_std = df[primary_metric].std() if total_rows > 1 else 0
        top_share_pct = (top_player[sum_col] / overall_sum * 100) if overall_sum else 0
        top2_share_pct = (grouped.head(2)[sum_col].sum() / overall_sum * 100) if overall_sum else 0
        price_spread = highest_avg_player[mean_col] - lowest_avg_player[mean_col]

        rating_insight = ""
        if rating_metric and f"{rating_metric}_mean" in grouped.columns:
            r_col = f"{rating_metric}_mean"
            best_rated = grouped.loc[grouped[r_col].idxmax()]
            worst_rated = grouped.loc[grouped[r_col].idxmin()]
            rating_insight = f"Customer satisfaction peaks with **{best_rated[cat_col]}** ({best_rated[r_col]:.2f}/5.0) vs. **{worst_rated[cat_col]}** ({worst_rated[r_col]:.2f}/5.0)."
        else:
            rating_insight = f"Dataset tracks **{len(num_cols)} quantitative KPIs** and **{len(cat_cols)} categorical dimensions** across **{total_rows:,} records**."

        strengths = [
            f"**Clear Market Dominance by {top_player[cat_col]}:** Leads the dataset with **PKR {top_player[sum_col]:,.0f}** in total {primary_metric} (**{top_share_pct:.1f}%** of total market volume across {int(top_player[cnt_col]):,} records).",
            f"**Strong Benchmark Baseline:** Overall market average for {primary_metric} stands at **PKR {overall_avg:,.2f}** (Median: **PKR {overall_median:,.2f}**), establishing a reliable performance threshold.",
            f"**Quality & Satisfaction Leadership:** {rating_insight}",
            f"**Multi-Segment Breadth:** Covers **{grouped[cat_col].nunique()} distinct competitors/segments** ({', '.join(grouped[cat_col].astype(str).head(5).tolist())}), enabling accurate cross-segment benchmarking.",
        ]

        weaknesses = [
            f"**High Revenue/Volume Concentration:** The top 2 players (**{', '.join(grouped[cat_col].astype(str).head(2).tolist())}** ) control **{top2_share_pct:.1f}%** of total {primary_metric}, leaving remaining segments under-monetized.",
            f"**Lagging Tail Performance ({bottom_player[cat_col]}):** Contributes only **PKR {bottom_player[sum_col]:,.0f}** (**{(bottom_player[sum_col]/overall_sum*100) if overall_sum else 0:.1f}%** share), indicating weak customer pull or distribution gaps.",
            f"**Wide Pricing / Value Dispersion:** A **PKR {price_spread:,.2f}** gap separates highest-priced **{highest_avg_player[cat_col]}** (avg **PKR {highest_avg_player[mean_col]:,.0f}**) from budget leader **{lowest_avg_player[cat_col]}** (avg **PKR {lowest_avg_player[mean_col]:,.0f}**).",
            f"**High Volatility Across Transactions:** Standard deviation of **PKR {overall_std:,.2f}** shows inconsistent order sizes rather than predictable recurring volume.",
        ]

        opportunities = [
            f"**Capture the Mid-Market Corridor (PKR {lowest_avg_player[mean_col]:,.0f} – PKR {overall_avg:,.0f}):** Position value-bundled offers slightly below the **PKR {overall_avg:,.0f}** average to win price-sensitive buyers from **{highest_avg_player[cat_col]}**.",
            f"**Replicate {top_player[cat_col]}'s Playbook in Mid-Tier Segments:** Scaling top-performing product/pricing strategies into lower-share segments can unlock an estimated **15%–25% uplift** in total {primary_metric}.",
            f"**Premium Upsell Above Median (PKR {overall_median:,.0f}):** Customers already purchasing above the median threshold represent prime targets for extended warranties, loyalty tiers, and cross-selling.",
            f"**Data-Driven SKU & Regional Optimization:** Eliminating bottom-decile underperformers and reallocating budget toward high-velocity segments directly improves net margins.",
        ]

        threats = [
            f"**Aggressive Price Undercutting by {lowest_avg_player[cat_col]}:** Operating at an average of **PKR {lowest_avg_player[mean_col]:,.0f}** (**{((overall_avg - lowest_avg_player[mean_col])/overall_avg*100) if overall_avg else 0:.1f}%** below market average) threatens to trigger a margin-eroding price war.",
            f"**Over-Reliance on {top_player[cat_col]} ({top_share_pct:.1f}% Share):** Any competitive disruption or seasonal slowdown in this single segment could severely impact overall business performance.",
            f"**Margin Compression in High-Cost Tiers:** Competitors priced above **PKR {highest_avg_player[mean_col]:,.0f}** risk customer churn if perceived quality does not clearly outperform mid-tier alternatives.",
            f"**Market Saturation & Rapid Imitation:** Without continuous monitoring of competitor pricing and web positioning, differentiation erodes quickly.",
        ]

        actions = [
            f"**1. Immediate Pricing Calibration (0–30 Days):** Anchor core offerings near **PKR {overall_avg:,.0f}** (market average) while introducing an entry-level fighter SKU around **PKR {lowest_avg_player[mean_col]:,.0f}** to counter budget rivals.",
            f"**2. Defend & Expand Leader Segment ({top_player[cat_col]}):** Allocate priority retention marketing to protect the **{top_share_pct:.1f}%** core share while bundling high-margin add-ons.",
            f"**3. Turnaround Plan for {bottom_player[cat_col]} (30–60 Days):** Audit why **{bottom_player[cat_col]}** trails at **PKR {bottom_player[sum_col]:,.0f}**—either reposition with targeted promotions or reallocate resources to top-3 segments.",
            f"**4. Automated Weekly KPI & Competitor Web Audits (Ongoing):** Track shifts against the **PKR {overall_median:,.0f}** median benchmark and monitor rival website changes via the Live Web Intelligence module.",
        ]

        return {
            "summary": f"Comprehensive statistical audit of **{total_rows:,} records** across **{grouped[cat_col].nunique()} competitors/segments**, analyzing **{primary_metric}** (Total: **PKR {overall_sum:,.0f}** | Mean: **PKR {overall_avg:,.2f}** | Median: **PKR {overall_median:,.2f}**).",
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
            "actions": actions,
        }

    return {
        "summary": f"Dataset audit across **{total_rows:,} records** and **{len(df.columns)} columns**.",
        "strengths": [f"Tracks {total_rows:,} structured records across {len(df.columns)} attributes."],
        "weaknesses": ["No numeric pricing/sales column detected for financial variance modeling."],
        "opportunities": ["Add numeric revenue, price, or rating columns to unlock deeper competitive benchmarking."],
        "threats": ["Limited quantitative tracking may delay detection of market shifts."],
        "actions": ["1. Upload a dataset containing numeric price, sales, or rating columns for full statistical SWOT synthesis."],
    }


# --- UPGRADED MULTI-FEATURE WEB INTELLIGENCE SCRAPER ---
def analyze_competitor_url(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    start_t = time.time()
    resp = requests.get(url, headers=headers, timeout=14)
    load_time = round(time.time() - start_t, 2)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "No Title Found"

    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if meta_tag and meta_tag.get("content"):
        meta_desc = meta_tag["content"].strip()

    og_site = ""
    og_tag = soup.find("meta", attrs={"property": "og:site_name"})
    if og_tag and og_tag.get("content"):
        og_site = og_tag["content"].strip()

    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:8] if h.get_text(strip=True)]
    links = soup.find_all("a")
    images = soup.find_all("img")

    page_text = soup.get_text(" ", strip=True).lower()
    promo_keywords = [kw for kw in ["sale", "discount", "% off", "free shipping", "new arrival", "flat", "winter", "summer", "warranty"] if kw in page_text]
    prices_found = re.findall(r"(?:PKR|Rs\.?|USD|\$)\s?[\d,]+(?:\.\d{2})?", soup.get_text(" ", strip=True))[:6]

    return {
        "url": url,
        "brand": og_site or title.split("|")[0].split("-")[0].strip()[:35],
        "title": title,
        "meta_desc": meta_desc or "No public meta description exposed.",
        "headings": headings,
        "links_count": len(links),
        "images_count": len(images),
        "load_time_sec": load_time,
        "promo_signals": ", ".join(promo_keywords).upper() if promo_keywords else "None Detected",
        "sample_prices": ", ".join(prices_found) if prices_found else "Dynamic / JS-rendered pricing",
    }


# --- SIDEBAR (MULTIPLE FILES + PERSISTENT ACCOUNT) ---
with st.sidebar:
    st.markdown(f"### :material/account_circle: {st.session_state.display_name}")
    st.caption(f"Logged in as `@{st.session_state.current_user}`")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Tutorial", icon=":material/help:", use_container_width=True):
            st.session_state.show_tutorial = True
            st.rerun()
    with col_s2:
        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = ""
            st.session_state.display_name = ""
            st.rerun()

    st.divider()
    st.markdown("### :material/folder_open: Upload Multiple Datasets")
    uploaded_files = st.file_uploader(
        "Upload 1 or More CSV / Excel Files",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        dfs = []
        loaded_names = []
        for f in uploaded_files:
            try:
                temp_df = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f)
                temp_df["Source_File"] = f.name
                dfs.append(temp_df)
                loaded_names.append(f.name)
            except Exception as e:
                st.error(f"Error reading {f.name}: {e}")

        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            file_label = f"{len(loaded_names)} File(s): {', '.join(loaded_names)}"
            st.success(f"Loaded {len(loaded_names)} file(s) ({len(df):,} total rows)")
        else:
            df = load_sample_data()
            file_label = "Default Benchmark"
    else:
        df = load_sample_data()
        file_label = "Default Benchmark"
        st.info("Using Default Benchmark Data")

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
        <p>Multi-File Benchmarking, Clear Visual Analytics, Deep SWOT Synthesis & Live Web Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- INTERACTIVE ONBOARDING TUTORIAL ---
if st.session_state.show_tutorial:
    st.markdown(
        """
        <div class="tutorial-box">
            <h4>Quick Guide — Platform Capabilities</h4>
            <ul style="margin:0; padding-left:1.2rem; color:#334155; font-size:0.92rem; line-height:1.6;">
                <li><strong>1. Upload Multiple Files (Left Sidebar):</strong> Select one or several CSV/Excel files at once to merge and compare them side-by-side.</li>
                <li><strong>2. Hover on KPI Cards:</strong> Move your cursor over any KPI card below to reveal minimum, maximum, and total breakdowns.</li>
                <li><strong>3. Easy-to-Read Graphs:</strong> Every chart shows exact numbers on bars/slices and a red Market Average line for instant comparison.</li>
                <li><strong>4. Comprehensive SWOT & Multi-URL Web Intelligence:</strong> Generate a full data-backed SWOT report or compare multiple live competitor websites at once.</li>
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
        ":material/monitoring: Clear Market Graphs & Scorecard",
        ":material/psychology: Comprehensive SWOT Analysis",
        ":material/language: Live Web Intelligence",
    ]
)

# --- TAB 1: CRYSTAL-CLEAR & DETAILED GRAPHS ---
with tab_overview:
    cat_options = [
        c for c in df.select_dtypes(exclude="number").columns.tolist()
    ]
    default_cat = find_column(
        df, ["competitor", "brand", "product", "category", "territory", "country", "source_file", "name"], numeric_only=False
    )
    num_cols = df.select_dtypes(include="number").columns.tolist()
    default_val = find_column(df, ["price", "salesamount", "amount", "sales", "revenue"], numeric_only=True)

    c_head, c_cat, c_met = st.columns([1.6, 1, 1])
    with c_head:
        st.subheader(":material/analytics: Visual Market & Competitor Breakdown")
        st.caption("Every chart displays exact values and market averages so anyone can understand trends immediately.")
    with c_cat:
        selected_cat = (
            st.selectbox(
                "Group / Compare By:",
                options=cat_options,
                index=cat_options.index(default_cat) if default_cat in cat_options else 0,
            )
            if cat_options
            else None
        )
    with c_met:
        selected_metric = (
            st.selectbox(
                "Metric to Analyze:",
                options=num_cols,
                index=num_cols.index(default_val) if default_val in num_cols else 0,
            )
            if num_cols
            else None
        )

    light_palette = ["#059669", "#0284C7", "#D97706", "#7C3AED", "#E11D48", "#0D9488", "#2563EB", "#4F46E5"]

    if selected_cat and selected_metric:
        summary_df = (
            df.groupby(selected_cat, as_index=False)
            .agg(
                Average_Value=(selected_metric, "mean"),
                Total_Value=(selected_metric, "sum"),
                Min_Value=(selected_metric, "min"),
                Max_Value=(selected_metric, "max"),
                Records=(selected_metric, "count"),
            )
            .sort_values("Total_Value", ascending=False)
            .head(12)
        )
        overall_avg = summary_df["Average_Value"].mean()
        total_sum = summary_df["Total_Value"].sum()
        summary_df["Share_%"] = (summary_df["Total_Value"] / total_sum * 100).round(2) if total_sum else 0
        summary_df["Diff_From_Avg_%"] = (
            ((summary_df["Average_Value"] - overall_avg) / overall_avg * 100).round(1) if overall_avg else 0
        )

        # ROW 1: Clear Bar Chart with Exact Labels + Market Share Donut
        g1, g2 = st.columns([1.35, 1])

        with g1:
            fig_bar = px.bar(
                summary_df,
                x=selected_cat,
                y="Average_Value",
                text="Average_Value",
                color=selected_cat,
                title=f"1. Average {selected_metric} by {selected_cat} (Exact Values & Market Average)",
                labels={"Average_Value": f"Avg {selected_metric}", selected_cat: selected_cat},
                color_discrete_sequence=light_palette,
                hover_data={"Total_Value": ":,.0f", "Min_Value": ":,.0f", "Max_Value": ":,.0f", "Share_%": ":.1f"},
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
                names=selected_cat,
                values="Total_Value",
                hole=0.42,
                title=f"2. Total {selected_metric} Share (%)",
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

        # ROW 2: Horizontal Total Volume Ranking + Strategic Quadrant / Multi-Metric Chart
        g3, g4 = st.columns(2)

        with g3:
            ranked_df = summary_df.sort_values("Total_Value", ascending=True)
            fig_hbar = px.bar(
                ranked_df,
                x="Total_Value",
                y=selected_cat,
                orientation="h",
                text="Total_Value",
                color="Share_%",
                color_continuous_scale="Tealgrn",
                title=f"3. Total Cumulative {selected_metric} Ranking (Lowest to Highest)",
                labels={"Total_Value": f"Total {selected_metric}", selected_cat: selected_cat},
            )
            fig_hbar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_hbar.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(color="#1E293B"),
                xaxis=dict(gridcolor="#F1F5F9"),
            )
            st.plotly_chart(fig_hbar, use_container_width=True)

        with g4:
            if len(num_cols) >= 2:
                x_col = num_cols[0]
                y_col = num_cols[1]
                scatter_df = df.head(500).copy()
                fig_quad = px.scatter(
                    scatter_df,
                    x=x_col,
                    y=y_col,
                    color=selected_cat,
                    title=f"4. Positioning Matrix: {x_col} vs. {y_col} (with Market Avg Lines)",
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
                fig_box = px.box(
                    df,
                    x=selected_cat,
                    y=selected_metric,
                    color=selected_cat,
                    title=f"4. Min, Median & Max Spread of {selected_metric}",
                    color_discrete_sequence=light_palette,
                )
                fig_box.update_layout(showlegend=False, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
                st.plotly_chart(fig_box, use_container_width=True)

        # ROW 3: Full Performance Scorecard Table
        st.subheader(":material/leaderboard: Complete Competitor & Segment Scorecard")
        scorecard = summary_df.copy()
        scorecard.insert(0, "Rank", range(1, len(scorecard) + 1))
        scorecard["Market_Position"] = scorecard["Diff_From_Avg_%"].apply(
            lambda x: "Above Market Avg" if x > 0 else ("At Market Avg" if x == 0 else "Below Market Avg")
        )
        st.dataframe(scorecard, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader(":material/table_view: Combined Dataset Preview (Top 500 Rows)")
    st.dataframe(df.head(500), use_container_width=True, hide_index=True)

# --- TAB 2: COMPREHENSIVE DATA-DRIVEN SWOT ANALYSIS ---
with tab_swot:
    st.subheader(":material/psychology: Comprehensive Data-Driven SWOT & Strategic Roadmap")
    st.caption("Deep multi-dimensional SWOT synthesis calculated directly from your active dataset(s).")

    if st.button("Generate Full Executive SWOT Report", icon=":material/auto_awesome:"):
        swot = generate_comprehensive_swot(df)
        st.info(swot["summary"])

        s_col1, s_col2 = st.columns(2)
        with s_col1:
            st.markdown("### :material/trending_up: Strengths (Internal Advantages)")
            for item in swot["strengths"]:
                st.markdown(f"- {item}")

            st.markdown("### :material/lightbulb: Opportunities (Growth Levers)")
            for item in swot["opportunities"]:
                st.markdown(f"- {item}")

        with s_col2:
            st.markdown("### :material/warning: Weaknesses (Internal Gaps)")
            for item in swot["weaknesses"]:
                st.markdown(f"- {item}")

            st.markdown("### :material/shield: Threats (External Market Risks)")
            for item in swot["threats"]:
                st.markdown(f"- {item}")

        st.divider()
        st.markdown("### :material/flag: Prioritized Strategic Action Roadmap")
        for act in swot["actions"]:
            st.markdown(act)

# --- TAB 3: UPGRADED MULTI-COMPETITOR LIVE WEB INTELLIGENCE ---
with tab_scraper:
    st.subheader(":material/language: Live Competitor Website & Positioning Intelligence")
    st.caption("Analyze and compare multiple competitor URLs side-by-side (Headings, Value Proposition, Promo Signals, Price Mentions & Load Speed).")

    default_urls = "https://www.limelight.pk/\nhttps://www.gulahmedshop.com/"
    urls_input = st.text_area(
        "Enter Competitor Website URLs (One URL per line):",
        value=default_urls,
        height=100,
    )

    if st.button("Run Live Competitor Web Audit", icon=":material/travel_explore:"):
        url_list = [u.strip() for u in urls_input.splitlines() if u.strip().startswith("http")]
        if not url_list:
            st.warning("Please enter at least one valid URL starting with http:// or https://")
        else:
            results = []
            with st.spinner(f"Auditing {len(url_list)} live website(s)..."):
                for u in url_list:
                    try:
                        results.append(analyze_competitor_url(u))
                    except Exception as e:
                        st.error(f"Could not access {u}: {e}")

            if results:
                # Side-by-side comparison table
                comp_table = pd.DataFrame(
                    [
                        {
                            "Brand / Site": r["brand"],
                            "Page Title": r["title"][:55],
                            "Detected Promo Signals": r["promo_signals"],
                            "Sample Prices Found": r["sample_prices"],
                            "Links Count": r["links_count"],
                            "Images Count": r["images_count"],
                            "Response Time (s)": r["load_time_sec"],
                        }
                        for r in results
                    ]
                )
                st.markdown("### :material/compare_arrows: Live Competitor Web Comparison Matrix")
                st.dataframe(comp_table, use_container_width=True, hide_index=True)

                # Detailed breakdown per website
                for r in results:
                    with st.expander(f"Detailed Intelligence Brief — {r['brand']} ({r['url']})", expanded=True):
                        st.markdown(f"**Core Positioning (Meta Description):** {r['meta_desc']}")
                        headings_str = " | ".join(r["headings"]) if r["headings"] else "No H1–H3 headings exposed"
                        st.markdown(f"**Key Landing Page Headlines:** {headings_str}")
                        st.markdown(f"**Active Promotional Keywords:** `{r['promo_signals']}` | **Detected Price Tags:** `{r['sample_prices']}`")
