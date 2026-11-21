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

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "display_name" not in st.session_state:
    st.session_state.display_name = ""
if "show_tutorial" not in st.session_state:
    st.session_state.show_tutorial = True
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"


# --- SOFT PEARL-WHITE & WARM SLATE LIGHT THEME (WITH IPHONE DARK/LIGHT TOGGLE) ---
def apply_theme_styles():
    is_dark = st.session_state.authenticated and (st.session_state.theme_mode == "Dark")

    if is_dark:
        bg_main = "#111318"
        bg_card = "#1A1D24"
        bg_sidebar = "#161920"
        text_primary = "#F3F4F6"
        text_secondary = "#9CA3AF"
        border_color = "#2D323E"
        soft_bg = "#232732"
        accent = "#0D9488"
        accent_hover = "#0F766E"
        header_bg = "linear-gradient(135deg, #1F2937 0%, #111827 100%)"
        header_title = "#FFFFFF"
        header_sub = "#D1D5DB"
        pill_track = "#2D323E"
        pill_knob_pos = "translateX(34px)"
        pill_icon = "🌙"
        popup_text = "Switch to Light Mode"
    else:
        bg_main = "#FAF9F6"
        bg_card = "#FFFFFF"
        bg_sidebar = "#FFFFFF"
        text_primary = "#1F2937"
        text_secondary = "#6B7280"
        border_color = "#E5E7EB"
        soft_bg = "#F3F4F6"
        accent = "#0D9488"
        accent_hover = "#0F766E"
        header_bg = "linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%)"
        header_title = "#111827"
        header_sub = "#4B5563"
        pill_track = "#E5E7EB"
        pill_knob_pos = "translateX(0px)"
        pill_icon = "☀️"
        popup_text = "Switch to Dark Mode"

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {{
                font-family: 'Plus Jakarta Sans', sans-serif;
            }}
            .stApp {{
                background-color: {bg_main};
                color: {text_primary};
            }}
            .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
            .stApp p, .stApp span, .stApp label, .stApp li, .stMarkdown,
            [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] p {{
                color: {text_primary} !important;
            }}
            [data-testid="stSidebar"] {{
                background-color: {bg_sidebar};
                border-right: 1px solid {border_color};
            }}
            [data-testid="stSidebar"] * {{
                color: {text_primary} !important;
            }}
            input, textarea, [data-baseweb="select"] > div {{
                background-color: {bg_card} !important;
                color: {text_primary} !important;
                border-color: {border_color} !important;
            }}

            /* iPhone-Style Sliding Pill Toggle with Hover Popup */
            .ios-toggle-wrapper {{
                position: relative;
                display: inline-flex;
                align-items: center;
                justify-content: flex-end;
                width: 100%;
                padding-top: 4px;
            }}
            .ios-pill {{
                position: relative;
                width: 72px;
                height: 36px;
                background: {pill_track};
                border: 1.5px solid {border_color};
                border-radius: 999px;
                padding: 3px;
                display: flex;
                align-items: center;
                transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.08);
                pointer-events: none;
            }}
            .ios-knob {{
                width: 28px;
                height: 28px;
                border-radius: 50%;
                background: #FFFFFF;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transform: {pill_knob_pos};
                transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
            }}
            .ios-popup {{
                position: absolute;
                top: 44px;
                right: 0;
                background: #1F2937;
                color: #FFFFFF !important;
                font-size: 0.76rem;
                font-weight: 600;
                padding: 5px 11px;
                border-radius: 8px;
                white-space: nowrap;
                opacity: 0;
                transform: translateY(-6px);
                transition: all 0.22s ease;
                pointer-events: none;
                box-shadow: 0 6px 16px rgba(0,0,0,0.18);
                z-index: 999;
            }}
            .ios-toggle-col:hover .ios-popup {{
                opacity: 1;
                transform: translateY(0px);
            }}

            /* Soft Light Executive Header */
            .exec-header {{
                background: {header_bg};
                padding: 1.5rem 2rem;
                border-radius: 16px;
                border: 1px solid {border_color};
                border-left: 6px solid {accent};
                margin-bottom: 1.3rem;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
            }}
            .exec-header h1 {{
                color: {header_title} !important;
                font-size: 1.8rem;
                font-weight: 800;
                margin: 0;
            }}
            .exec-header p {{
                color: {header_sub} !important;
                font-size: 0.95rem;
                margin: 0.35rem 0 0 0;
                font-weight: 500;
            }}

            /* Interactive KPI Cards */
            .kpi-card {{
                background: {bg_card};
                border: 1px solid {border_color};
                border-top: 4px solid {accent};
                border-radius: 14px;
                padding: 1.15rem 1.25rem;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
                transition: all 0.25s ease;
                cursor: pointer;
                min-height: 126px;
            }}
            .kpi-card:hover {{
                transform: translateY(-4px);
                border-color: {accent};
                background-color: {soft_bg};
                box-shadow: 0 10px 22px rgba(0, 0, 0, 0.09);
            }}
            .kpi-label {{
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: {text_secondary} !important;
                margin-bottom: 0.35rem;
            }}
            .kpi-value {{
                font-size: 1.55rem;
                font-weight: 800;
                color: {text_primary} !important;
                line-height: 1.2;
            }}
            .kpi-hint {{
                font-size: 0.76rem;
                color: {accent} !important;
                margin-top: 0.4rem;
                font-weight: 600;
            }}
            .kpi-detail-box {{
                max-height: 0;
                opacity: 0;
                overflow: hidden;
                transition: all 0.28s ease;
                font-size: 0.82rem;
                color: {text_primary} !important;
                background: {soft_bg};
                border: 1px solid {accent};
                border-radius: 8px;
                padding: 0 0.6rem;
                font-weight: 500;
            }}
            .kpi-card:hover .kpi-detail-box {{
                max-height: 95px;
                opacity: 1;
                padding: 0.45rem 0.65rem;
                margin-top: 0.5rem;
            }}
            .kpi-card:hover .kpi-hint {{
                display: none;
            }}

            /* Chart Explanation Card */
            .chart-note {{
                background-color: {soft_bg};
                border-left: 4px solid {accent};
                padding: 0.7rem 1rem;
                border-radius: 8px;
                font-size: 0.87rem;
                color: {text_primary} !important;
                margin-top: -0.35rem;
                margin-bottom: 1.3rem;
                font-weight: 500;
            }}

            /* Tutorial Box */
            .tutorial-box {{
                background-color: {bg_card};
                border: 1px solid {border_color};
                border-left: 5px solid {accent};
                border-radius: 12px;
                padding: 1.15rem 1.4rem;
                margin-bottom: 1.2rem;
            }}

            /* Primary Buttons */
            .stButton > button, .stDownloadButton > button {{
                background-color: {accent} !important;
                color: #FFFFFF !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 0.5rem 1.15rem !important;
            }}
            .stButton > button p, .stDownloadButton > button p {{
                color: #FFFFFF !important;
            }}
            .stButton > button:hover, .stDownloadButton > button:hover {{
                background-color: {accent_hover} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return pill_icon, popup_text


pill_icon, popup_text = apply_theme_styles()


# --- 1. CLEAN LOGIN & SIGN-UP PORTAL ---
def render_login_portal():
    col1, col2, col3 = st.columns([1, 1.45, 1])
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


# --- SMART DATA & DATASET-TYPE DETECTOR ---
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


def detect_dataset_profile(df: pd.DataFrame) -> dict:
    cols_lower = [c.lower() for c in df.columns]
    date_cols = [c for c in df.columns if any(k in c.lower() for k in ["date", "time", "month", "year"])]
    has_competitor = any(k in c for c in cols_lower for k in ["competitor", "brand", "rival", "company"])
    has_sales = any(k in c for c in cols_lower for k in ["salesamount", "revenue", "sales", "profit", "order"])

    if has_competitor:
        profile_type = "Competitor Benchmarking Dataset"
    elif date_cols and has_sales:
        profile_type = "Time-Series Sales & Revenue Dataset"
    elif has_sales:
        profile_type = "Commercial Product & Revenue Dataset"
    else:
        profile_type = "Multi-Attribute Market Dataset"

    return {
        "type": profile_type,
        "date_col": date_cols[0] if date_cols else None,
        "has_competitor": has_competitor,
        "has_sales": has_sales,
    }


def style_plotly_chart(fig):
    is_dark = st.session_state.theme_mode == "Dark"
    bg_color = "#1A1D24" if is_dark else "#FFFFFF"
    font_color = "#F3F4F6" if is_dark else "#1F2937"
    grid_color = "#2D323E" if is_dark else "#F3F4F6"

    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color, size=12),
        title_font=dict(color=font_color, size=15),
        xaxis=dict(gridcolor=grid_color, tickfont=dict(color=font_color), title_font=dict(color=font_color)),
        yaxis=dict(gridcolor=grid_color, tickfont=dict(color=font_color), title_font=dict(color=font_color)),
        legend=dict(font=dict(color=font_color)),
        margin=dict(t=55, b=25),
    )
    return fig


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


# --- COMPREHENSIVE DATA-DRIVEN SWOT ENGINE ---
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

        if rating_metric and f"{rating_metric}_mean" in grouped.columns:
            r_col = f"{rating_metric}_mean"
            best_rated = grouped.loc[grouped[r_col].idxmax()]
            worst_rated = grouped.loc[grouped[r_col].idxmin()]
            rating_insight = f"Customer satisfaction peaks with **{best_rated[cat_col]}** ({best_rated[r_col]:.2f}/5.0) vs. **{worst_rated[cat_col]}** ({worst_rated[r_col]:.2f}/5.0)."
        else:
            rating_insight = f"Dataset tracks **{len(num_cols)} quantitative KPIs** and **{len(cat_cols)} categorical dimensions** across **{total_rows:,} records**."

        strengths = [
            f"**Clear Market Dominance by {top_player[cat_col]}:** Leads with **PKR {top_player[sum_col]:,.0f}** in total {primary_metric} (**{top_share_pct:.1f}%** of total market volume across {int(top_player[cnt_col]):,} records).",
            f"**Strong Benchmark Baseline:** Overall market average for {primary_metric} is **PKR {overall_avg:,.2f}** (Median: **PKR {overall_median:,.2f}**), establishing a clear performance threshold.",
            f"**Quality & Satisfaction Leadership:** {rating_insight}",
            f"**Multi-Segment Breadth:** Covers **{grouped[cat_col].nunique()} distinct competitors/segments** ({', '.join(grouped[cat_col].astype(str).head(5).tolist())}), enabling accurate cross-segment benchmarking.",
        ]

        weaknesses = [
            f"**High Revenue/Volume Concentration:** The top 2 players (**{', '.join(grouped[cat_col].astype(str).head(2).tolist())}** ) control **{top2_share_pct:.1f}%** of total {primary_metric}, leaving remaining segments under-monetized.",
            f"**Lagging Tail Performance ({bottom_player[cat_col]}):** Contributes only **PKR {bottom_player[sum_col]:,.0f}** (**{(bottom_player[sum_col]/overall_sum*100) if overall_sum else 0:.1f}%** share), indicating weak customer pull or distribution gaps.",
            f"**Wide Pricing / Value Dispersion:** A **PKR {price_spread:,.2f}** gap separates highest-priced **{highest_avg_player[cat_col]}** (avg **PKR {highest_avg_player[mean_col]:,.0f}**) from budget leader **{lowest_avg_player[cat_col]}** (avg **PKR {lowest_avg_player[mean_col]:,.0f}**).",
            f"**High Volatility Across Transactions:** Standard deviation of **PKR {overall_std:,.2f}** shows uneven order sizes rather than predictable recurring volume.",
        ]

        opportunities = [
            f"**Capture the Mid-Market Corridor (PKR {lowest_avg_player[mean_col]:,.0f} – PKR {overall_avg:,.0f}):** Position value-bundled offers slightly below the **PKR {overall_avg:,.0f}** average to win price-sensitive buyers from **{highest_avg_player[cat_col]}**.",
            f"**Replicate {top_player[cat_col]}'s Playbook in Mid-Tier Segments:** Scaling top-performing strategies into lower-share segments can unlock an estimated **15%–25% uplift** in total {primary_metric}.",
            f"**Premium Upsell Above Median (PKR {overall_median:,.0f}):** Customers buying above the median threshold are prime targets for extended warranties, loyalty tiers, and cross-selling.",
            f"**Data-Driven SKU & Regional Optimization:** Eliminating bottom-decile underperformers and reallocating budget toward high-velocity segments directly improves net margins.",
        ]

        threats = [
            f"**Aggressive Price Undercutting by {lowest_avg_player[cat_col]}:** Operating at an average of **PKR {lowest_avg_player[mean_col]:,.0f}** (**{((overall_avg - lowest_avg_player[mean_col])/overall_avg*100) if overall_avg else 0:.1f}%** below market average) threatens to trigger a margin-eroding price war.",
            f"**Over-Reliance on {top_player[cat_col]} ({top_share_pct:.1f}% Share):** Any competitive disruption or seasonal slowdown in this single segment could severely impact overall business performance.",
            f"**Margin Compression in High-Cost Tiers:** Competitors priced above **PKR {highest_avg_player[mean_col]:,.0f}** risk customer churn if perceived quality does not clearly outperform mid-tier alternatives.",
            f"**Market Saturation & Rapid Imitation:** Without continuous monitoring of competitor pricing and web positioning, differentiation erodes quickly.",
        ]

        actions = [
            f"**1. Immediate Pricing Calibration (0–30 Days):** Anchor core offerings near **PKR {overall_avg:,.0f}** (market average) while introducing an entry-level SKU around **PKR {lowest_avg_player[mean_col]:,.0f}** to counter budget rivals.",
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


# --- LIVE WEB INTELLIGENCE SCRAPER ---
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
    promo_keywords = [
        kw
        for kw in ["sale", "discount", "% off", "free shipping", "new arrival", "flat", "winter", "summer", "warranty"]
        if kw in page_text
    ]
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


# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### :material/account_circle: {st.session_state.display_name}")
    st.caption(f"Logged in as `@{st.session_state.current_user}`")
    c_sb1, c_sb2 = st.columns(2)
    with c_sb1:
        if st.button("Guide", icon=":material/help:", use_container_width=True):
            st.session_state.show_tutorial = True
            st.rerun()
    with c_sb2:
        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = ""
            st.session_state.display_name = ""
            st.rerun()

    st.divider()
    st.markdown("### :material/folder_open: Upload Market Data")
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
            st.success(f"Loaded {len(loaded_names)} file(s) ({len(df):,} rows)")
        else:
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


# --- TOP-RIGHT IPHONE-STYLE LIGHT/DARK PILL TOGGLE (ONLY AFTER LOGIN) ---
top_left, top_right = st.columns([5.5, 1])
with top_right:
    st.markdown(
        f"""
        <div class="ios-toggle-col">
            <div class="ios-toggle-wrapper">
                <div class="ios-pill">
                    <div class="ios-knob">{pill_icon}</div>
                </div>
                <div class="ios-popup">{popup_text}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    btn_label = "Dark" if st.session_state.theme_mode == "Light" else "Light"
    if st.button(f"Toggle {btn_label}", key="ios_theme_btn", use_container_width=True):
        st.session_state.theme_mode = "Dark" if st.session_state.theme_mode == "Light" else "Light"
        st.rerun()


# --- MAIN EXECUTIVE DASHBOARD ---
profile = detect_dataset_profile(df)

st.markdown(
    f"""
    <div class="exec-header">
        <h1>AI-Powered Competitor Intelligence & Market Analysis</h1>
        <p>Detected Profile: <strong>{profile['type']}</strong> — 4 Distinct Visual Graphs, Competitor Duel, SWOT & Live Web Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- INTERACTIVE ONBOARDING TUTORIAL ---
if st.session_state.show_tutorial:
    st.markdown(
        """
        <div class="tutorial-box">
            <h4>Quick Guide — 4 Specific Graphs & Intelligence Modules</h4>
            <ul style="margin:0; padding-left:1.2rem; font-size:0.92rem; line-height:1.6;">
                <li><strong>1. Four Distinct Graphs:</strong> (1) <em>Pricing Comparison</em>, (2) <em>Customer Quality/Rating</em>, (3) <em>Market Share %</em>, and (4) <em>Sales Volume Performance</em> — each chart tells a unique story.</li>
                <li><strong>2. Head-to-Head Competitor Duel:</strong> Select any two competitors to compare them side-by-side across every metric.</li>
                <li><strong>3. Comprehensive SWOT Intelligence:</strong> Generates a full data-backed SWOT report with strategic actions.</li>
                <li><strong>4. Live Web Intelligence:</strong> Audit and compare live competitor websites for headlines, promos, and pricing.</li>
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
        ":material/monitoring: 4 Specific Graphs & Competitor Duel",
        ":material/psychology: Comprehensive SWOT Intelligence",
        ":material/language: Live Web Intelligence",
    ]
)

# --- TAB 1: 4 COMPLETELY DISTINCT, SPECIFIC GRAPHS ---
with tab_overview:
    cat_options = df.select_dtypes(exclude="number").columns.tolist()
    default_cat = find_column(
        df, ["competitor", "brand", "product", "category", "territory", "country", "source_file", "name"], numeric_only=False
    )
    num_cols = df.select_dtypes(include="number").columns.tolist()

    # Assign 4 distinct numeric columns to the 4 charts
    price_col = find_column(df, ["price", "cost", "unitprice", "amount", "salesamount"], numeric_only=True)
    rating_col = find_column(df, ["rating", "score", "review", "satisfaction"], numeric_only=True)
    share_col = find_column(df, ["market_share", "share", "revenue", "salesamount"], numeric_only=True)
    volume_col = find_column(df, ["monthly_sales", "sales", "quantity", "volume", "units"], numeric_only=True)

    # Ensure distinct columns if generic dataset is uploaded
    remaining_nums = [c for c in num_cols if c != price_col]
    if rating_col == price_col and remaining_nums:
        rating_col = remaining_nums[0]
    remaining_nums2 = [c for c in num_cols if c not in [price_col, rating_col]]
    if share_col in [price_col, rating_col] and remaining_nums2:
        share_col = remaining_nums2[0]
    remaining_nums3 = [c for c in num_cols if c not in [price_col, rating_col, share_col]]
    if volume_col in [price_col, rating_col, share_col] and remaining_nums3:
        volume_col = remaining_nums3[0]

    c_head, c_cat = st.columns([2.2, 1])
    with c_head:
        st.subheader(f":material/analytics: 4-Angle Competitor & Market Analysis ({profile['type']})")
        st.caption("Each of the 4 graphs below reveals a specific, non-overlapping insight from your dataset.")
    with c_cat:
        selected_cat = (
            st.selectbox(
                "Compare Competitor / Segment By:",
                options=cat_options,
                index=cat_options.index(default_cat) if default_cat in cat_options else 0,
            )
            if cat_options
            else None
        )

    soft_palette = ["#0D9488", "#3B82F6", "#F59E0B", "#8B5CF6", "#EC4899", "#10B981", "#6366F1"]

    if selected_cat and num_cols:
        agg_spec = {}
        for col in set([c for c in [price_col, rating_col, share_col, volume_col] if c]):
            agg_spec[col] = "mean" if col in [price_col, rating_col] else "sum"

        summary_df = df.groupby(selected_cat, as_index=False).agg(agg_spec).head(12)

        # ROW 1: Graph 1 (Price Positioning) + Graph 2 (Customer Quality/Rating)
        g1, g2 = st.columns(2)

        with g1:
            if price_col:
                p_df = summary_df.sort_values(price_col, ascending=False)
                avg_p = p_df[price_col].mean()
                fig_price = px.bar(
                    p_df,
                    x=selected_cat,
                    y=price_col,
                    text=price_col,
                    color=selected_cat,
                    title=f"Graph 1 — Price & Cost Positioning ({price_col})",
                    color_discrete_sequence=soft_palette,
                )
                fig_price.update_traces(texttemplate="%{text:,.1f}", textposition="outside")
                fig_price.add_hline(
                    y=avg_p,
                    line_dash="dash",
                    line_color="#EF4444",
                    annotation_text=f"Market Avg: {avg_p:,.1f}",
                    annotation_position="top right",
                )
                fig_price.update_layout(showlegend=False)
                st.plotly_chart(style_plotly_chart(fig_price), use_container_width=True)
                highest_p = p_df.iloc[0]
                lowest_p = p_df.iloc[-1]
                st.markdown(
                    f"<div class='chart-note'><b>Specific Insight (Pricing):</b> <b>{highest_p[selected_cat]}</b> is priced highest ({highest_p[price_col]:,.1f}), while <b>{lowest_p[selected_cat]}</b> offers the lowest entry price ({lowest_p[price_col]:,.1f}).</div>",
                    unsafe_allow_html=True,
                )

        with g2:
            if rating_col and rating_col != price_col:
                r_df = summary_df.sort_values(rating_col, ascending=True)
                avg_r = r_df[rating_col].mean()
                fig_rating = px.bar(
                    r_df,
                    x=rating_col,
                    y=selected_cat,
                    orientation="h",
                    text=rating_col,
                    color=selected_cat,
                    title=f"Graph 2 — Customer Satisfaction & Quality ({rating_col})",
                    color_discrete_sequence=soft_palette,
                )
                fig_rating.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
                fig_rating.add_vline(
                    x=avg_r,
                    line_dash="dash",
                    line_color="#EF4444",
                    annotation_text=f"Avg: {avg_r:,.2f}",
                    annotation_position="top right",
                )
                fig_rating.update_layout(showlegend=False)
                st.plotly_chart(style_plotly_chart(fig_rating), use_container_width=True)
                top_r = r_df.iloc[-1]
                st.markdown(
                    f"<div class='chart-note'><b>Specific Insight (Quality):</b> <b>{top_r[selected_cat]}</b> leads customer satisfaction with <b>{top_r[rating_col]:,.2f}</b> vs. market average {avg_r:,.2f}.</div>",
                    unsafe_allow_html=True,
                )
            else:
                cnt_df = df[selected_cat].value_counts().reset_index().head(10)
                cnt_df.columns = [selected_cat, "Order_Count"]
                fig_cnt = px.bar(
                    cnt_df,
                    x="Order_Count",
                    y=selected_cat,
                    orientation="h",
                    text="Order_Count",
                    color=selected_cat,
                    title=f"Graph 2 — Transaction Frequency per {selected_cat}",
                    color_discrete_sequence=soft_palette,
                )
                fig_cnt.update_traces(texttemplate="%{text:,}", textposition="outside")
                fig_cnt.update_layout(showlegend=False)
                st.plotly_chart(style_plotly_chart(fig_cnt), use_container_width=True)
                st.markdown(
                    f"<div class='chart-note'><b>Specific Insight (Frequency):</b> Shows exact number of orders/entries recorded for each {selected_cat}.</div>",
                    unsafe_allow_html=True,
                )

        # ROW 2: Graph 3 (Market Share %) + Graph 4 (Sales Volume Performance)
        g3, g4 = st.columns(2)

        with g3:
            if share_col:
                s_df = summary_df.sort_values(share_col, ascending=False)
                fig_share = px.pie(
                    s_df,
                    names=selected_cat,
                    values=share_col,
                    hole=0.50,
                    title=f"Graph 3 — Market Share Distribution (% of {share_col})",
                    color_discrete_sequence=soft_palette,
                )
                fig_share.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    pull=[0.05 if i == 0 else 0 for i in range(len(s_df))],
                    hovertemplate="<b>%{label}</b><br>Value: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
                )
                st.plotly_chart(style_plotly_chart(fig_share), use_container_width=True)
                top_s = s_df.iloc[0]
                tot_s = s_df[share_col].sum()
                pct_s = (top_s[share_col] / tot_s * 100) if tot_s else 0
                st.markdown(
                    f"<div class='chart-note'><b>Specific Insight (Market Share):</b> <b>{top_s[selected_cat]}</b> captures the largest market share at <b>{pct_s:.1f}%</b>.</div>",
                    unsafe_allow_html=True,
                )

        with g4:
            if volume_col and volume_col not in [price_col, rating_col]:
                v_df = summary_df.sort_values(volume_col, ascending=False)
                fig_vol = px.area(
                    v_df,
                    x=selected_cat,
                    y=volume_col,
                    markers=True,
                    text=volume_col,
                    title=f"Graph 4 — Sales Volume & Demand Strength ({volume_col})",
                    color_discrete_sequence=["#0D9488"],
                )
                fig_vol.update_traces(texttemplate="%{text:,.0f}", textposition="top center")
                st.plotly_chart(style_plotly_chart(fig_vol), use_container_width=True)
                top_v = v_df.iloc[0]
                st.markdown(
                    f"<div class='chart-note'><b>Specific Insight (Sales Volume):</b> <b>{top_v[selected_cat]}</b> drives the highest demand volume with <b>{top_v[volume_col]:,.0f}</b> units/sales.</div>",
                    unsafe_allow_html=True,
                )
            elif profile["date_col"] and price_col:
                ts_df = df[[profile["date_col"], price_col]].dropna().copy()
                ts_df[profile["date_col"]] = pd.to_datetime(ts_df[profile["date_col"]], errors="coerce")
                ts_df = ts_df.dropna().sort_values(profile["date_col"])
                ts_grouped = ts_df.groupby(ts_df[profile["date_col"]].dt.to_period("M"))[price_col].sum().reset_index()
                ts_grouped[profile["date_col"]] = ts_grouped[profile["date_col"]].astype(str)
                fig_trend = px.line(
                    ts_grouped,
                    x=profile["date_col"],
                    y=price_col,
                    markers=True,
                    title=f"Graph 4 — Monthly Timeline Trend ({price_col})",
                    color_discrete_sequence=["#0D9488"],
                )
                st.plotly_chart(style_plotly_chart(fig_trend), use_container_width=True)
                st.markdown(
                    f"<div class='chart-note'><b>Specific Insight (Timeline):</b> Tracks monthly growth and seasonal peaks of <b>{price_col}</b>.</div>",
                    unsafe_allow_html=True,
                )
            else:
                fig_dist = px.histogram(
                    df,
                    x=price_col or num_cols[0],
                    nbins=20,
                    title=f"Graph 4 — Value Range Distribution ({price_col or num_cols[0]})",
                    color_discrete_sequence=["#0D9488"],
                )
                st.plotly_chart(style_plotly_chart(fig_dist), use_container_width=True)
                st.markdown(
                    "<div class='chart-note'><b>Specific Insight (Distribution):</b> Shows which price/value brackets have the highest transaction density.</div>",
                    unsafe_allow_html=True,
                )

        # --- HEAD-TO-HEAD COMPETITOR COMPARISON DUEL ---
        st.divider()
        st.subheader(":material/swords: Head-to-Head Competitor Comparison")
        st.caption("Select any two competitors or segments to compare them side-by-side and see who wins on each metric.")

        entities = summary_df[selected_cat].astype(str).tolist()
        if len(entities) >= 2:
            h1, h2 = st.columns(2)
            with h1:
                comp_a = st.selectbox("Select Competitor A:", options=entities, index=0)
            with h2:
                comp_b = st.selectbox("Select Competitor B:", options=entities, index=1)

            row_a = summary_df[summary_df[selected_cat].astype(str) == comp_a].iloc[0]
            row_b = summary_df[summary_df[selected_cat].astype(str) == comp_b].iloc[0]

            duel_rows = []
            for m_col in [c for c in summary_df.columns if c != selected_cat]:
                val_a = float(row_a[m_col])
                val_b = float(row_b[m_col])
                diff = val_a - val_b
                if any(k in m_col.lower() for k in ["price", "cost"]):
                    winner = comp_a if val_a < val_b else (comp_b if val_b < val_a else "Tie")
                else:
                    winner = comp_a if val_a > val_b else (comp_b if val_b > val_a else "Tie")
                duel_rows.append(
                    {
                        "Metric": m_col,
                        comp_a: round(val_a, 2),
                        comp_b: round(val_b, 2),
                        "Difference (A - B)": round(diff, 2),
                        "Advantage": winner,
                    }
                )
            st.dataframe(pd.DataFrame(duel_rows), use_container_width=True, hide_index=True)

        # ROW 3: Complete Scorecard Table
        st.subheader(":material/leaderboard: Unified Competitor & Segment Scorecard")
        scorecard = summary_df.copy()
        if share_col and scorecard[share_col].sum() > 0:
            scorecard["Market_Share_%"] = (scorecard[share_col] / scorecard[share_col].sum() * 100).round(2)
            scorecard = scorecard.sort_values("Market_Share_%", ascending=False)
        scorecard.insert(0, "Rank", range(1, len(scorecard) + 1))
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

# --- TAB 3: LIVE WEB INTELLIGENCE ---
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

                for r in results:
                    with st.expander(f"Detailed Intelligence Brief — {r['brand']} ({r['url']})", expanded=True):
                        st.markdown(f"**Core Positioning (Meta Description):** {r['meta_desc']}")
                        headings_str = " | ".join(r["headings"]) if r["headings"] else "No H1–H3 headings exposed"
                        st.markdown(f"**Key Landing Page Headlines:** {headings_str}")
                        st.markdown(f"**Active Promotional Keywords:** `{r['promo_signals']}` | **Detected Price Tags:** `{r['sample_prices']}`")
