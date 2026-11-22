import sqlite3
import hashlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="STRATEX AI | Competitor Intelligence & Market Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. PERSISTENT SQLITE DATABASE ---
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
        ("admin", demo_hash, "Usman Naveed"),
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
    return True, "Account saved!"


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

# --- 3. SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "display_name" not in st.session_state:
    st.session_state.display_name = ""
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"


# --- 4. SAFE, HIGH-CONTRAST LIGHT/DARK THEME & 3D GLASS TOGGLE ---
def apply_safe_theme():
    is_dark = st.session_state.authenticated and (st.session_state.theme_mode == "Dark")

    if is_dark:
        bg_main = "#0B1120"
        bg_card = "#111827"
        bg_sidebar = "#0F172A"
        text_bright = "#FFFFFF"
        text_sub = "#E2E8F0"
        border_col = "#334155"
        soft_tint = "#1E1B4B"
        accent = "#6366F1"
        accent_2 = "#EC4899"
        hero_bg = "linear-gradient(135deg, #1E1B4B 0%, #312E81 100%)"
        glass_bg = "linear-gradient(145deg, #1E293B, #0F172A)"
        glass_border = "rgba(255, 255, 255, 0.22)"
        knob_pos = "translateX(84px)"
        knob_bg = "#334155"
        left_op = "1"
        right_op = "0"
    else:
        bg_main = "#F8FAFC"
        bg_card = "#FFFFFF"
        bg_sidebar = "#FFFFFF"
        text_bright = "#0F172A"
        text_sub = "#334155"
        border_col = "#CBD5E1"
        soft_tint = "#EEF2FF"
        accent = "#4F46E5"
        accent_2 = "#0EA5E9"
        hero_bg = "linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%)"
        glass_bg = "linear-gradient(145deg, #E2E8F0, #CBD5E1)"
        glass_border = "#FFFFFF"
        knob_pos = "translateX(0px)"
        knob_bg = "#FFFFFF"
        left_op = "0"
        right_op = "1"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {bg_main};
            color: {text_bright};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {bg_sidebar};
            border-right: 1px solid {border_col};
        }}
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {{
            color: {text_bright} !important;
        }}
        .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
        label[data-testid="stWidgetLabel"] p, div[data-testid="stCaptionContainer"] p,
        div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {{
            color: {text_bright} !important;
        }}

        /* 3D Glassmorphism Sliding Toggle */
        .glass-wrap {{
            display: flex;
            justify-content: flex-end;
            width: 100%;
            margin-bottom: 6px;
        }}
        .glass-pill {{
            position: relative;
            width: 146px;
            height: 52px;
            border-radius: 999px;
            background: {glass_bg};
            border: 1.5px solid {glass_border};
            box-shadow: 0 8px 20px rgba(0,0,0,0.18);
            display: flex;
            align-items: center;
            padding: 4px;
            transition: all 0.4s ease;
        }}
        .glass-knob {{
            position: relative;
            z-index: 2;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: {knob_bg};
            box-shadow: 0 3px 8px rgba(0,0,0,0.25);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 19px;
            transform: {knob_pos};
            transition: transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        .glass-lbl-left {{
            position: absolute;
            left: 22px;
            font-size: 1rem;
            font-weight: 700;
            color: #FFFFFF !important;
            opacity: {left_op};
            transition: opacity 0.3s ease;
        }}
        .glass-lbl-right {{
            position: absolute;
            right: 22px;
            font-size: 1rem;
            font-weight: 700;
            color: #0F172A !important;
            opacity: {right_op};
            transition: opacity 0.3s ease;
        }}

        /* Executive Hero Header */
        .hero-box {{
            background: {hero_bg};
            padding: 1.7rem 2rem;
            border-radius: 16px;
            border: 1px solid {border_col};
            border-left: 7px solid {accent};
            margin-bottom: 1.3rem;
            box-shadow: 0 8px 24px rgba(79, 70, 229, 0.12);
        }}
        .hero-tag {{
            display: inline-block;
            background: {accent};
            color: #FFFFFF !important;
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 999px;
            margin-bottom: 0.5rem;
        }}
        .hero-heading {{
            color: {text_bright} !important;
            font-size: 2.05rem;
            font-weight: 900;
            margin: 0;
            line-height: 1.2;
        }}
        .hero-sub {{
            color: {text_sub} !important;
            font-size: 0.96rem;
            font-weight: 600;
            margin: 0.4rem 0 0 0;
        }}

        /* Interactive KPI Cards */
        .kpi-card {{
            background: {bg_card};
            border: 1px solid {border_col};
            border-top: 4px solid {accent};
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.25s ease;
            cursor: pointer;
            min-height: 125px;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
            border-color: {accent};
            background-color: {soft_tint};
            box-shadow: 0 10px 24px rgba(79, 70, 229, 0.18);
        }}
        .kpi-label {{
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            color: {text_sub} !important;
            margin-bottom: 0.35rem;
        }}
        .kpi-value {{
            font-size: 1.6rem;
            font-weight: 800;
            color: {text_bright} !important;
        }}
        .kpi-hint {{
            font-size: 0.76rem;
            color: {accent} !important;
            margin-top: 0.4rem;
            font-weight: 700;
        }}
        .kpi-detail {{
            max-height: 0;
            opacity: 0;
            overflow: hidden;
            transition: all 0.28s ease;
            font-size: 0.82rem;
            color: {text_bright} !important;
            background: {soft_tint};
            border: 1px solid {accent};
            border-radius: 8px;
            padding: 0 0.6rem;
            font-weight: 600;
        }}
        .kpi-card:hover .kpi-detail {{
            max-height: 95px;
            opacity: 1;
            padding: 0.45rem 0.65rem;
            margin-top: 0.5rem;
        }}
        .kpi-card:hover .kpi-hint {{
            display: none;
        }}

        /* Chart Takeaway Box */
        .chart-note {{
            background-color: {soft_tint};
            border-left: 4px solid {accent};
            padding: 0.72rem 1rem;
            border-radius: 8px;
            font-size: 0.88rem;
            color: {text_bright} !important;
            margin-top: -0.35rem;
            margin-bottom: 1.3rem;
            font-weight: 600;
        }}

        /* Primary Buttons */
        .stButton > button, .stDownloadButton > button {{
            background: linear-gradient(135deg, {accent} 0%, {accent_2} 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
        }}
        .stButton > button p, .stDownloadButton > button p {{
            color: #FFFFFF !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return "🌙" if is_dark else "☀️"


knob_icon = apply_safe_theme()


# --- 5. LOGIN & SIGN-UP PORTAL ---
def render_login():
    col1, col2, col3 = st.columns([1, 1.45, 1])
    with col2:
        st.markdown(
            """
            <div class="hero-box" style="text-align:center; margin-top:2rem;">
                <div class="hero-tag">FMS • IIUI Enterprise Analytics</div>
                <h1 class="hero-heading">AI-Powered Competitor Intelligence</h1>
                <p class="hero-sub">Strategic Market Benchmarking, SWOT Engine & What-If Profit Simulator</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        t_in, t_up = st.tabs(["Sign In (Existing Account)", "Create New Account"])

        with t_in:
            with st.form("login_form"):
                u_in = st.text_input("Username", placeholder="Enter your username")
                p_in = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Sign In to Dashboard", use_container_width=True):
                    ok, dname = verify_user(u_in, p_in)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.current_user = u_in.strip().lower()
                        st.session_state.display_name = dname
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            st.caption("Default Demo Login — Username: `admin` | Password: `fyp2026`")

        with t_up:
            with st.form("register_form"):
                f_name = st.text_input("Full Name", placeholder="e.g., Usman Naveed")
                new_u = st.text_input("Choose Username", placeholder="e.g., usman103")
                new_p = st.text_input("Create Password", type="password", placeholder="Choose a password")
                if st.form_submit_button("Create Account & Login Directly", use_container_width=True):
                    ok, msg = register_user(new_u, new_p, f_name)
                    if ok:
                        st.session_state.authenticated = True
                        st.session_state.current_user = new_u.strip().lower()
                        st.session_state.display_name = f_name.strip() or new_u.strip().title()
                        st.rerun()
                    else:
                        st.warning(msg)


if not st.session_state.authenticated:
    render_login()
    st.stop()


# --- 6. DATA HELPERS ---
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


def detect_dataset_profile(df: pd.DataFrame) -> str:
    cols_lower = [c.lower() for c in df.columns]
    if any(k in c for c in cols_lower for k in ["competitor", "brand", "rival", "company"]):
        return "Competitor Benchmarking Dataset"
    if any(k in c for c in cols_lower for k in ["salesamount", "revenue", "sales", "profit"]):
        return "Commercial Sales & Revenue Dataset"
    return "Multi-Attribute Market Dataset"


def style_chart(fig):
    is_dark = st.session_state.theme_mode == "Dark"
    bg = "#111827" if is_dark else "#FFFFFF"
    fg = "#FFFFFF" if is_dark else "#0F172A"
    grid = "#1E293B" if is_dark else "#F1F5F9"
    fig.update_layout(
        plot_bgcolor=bg,
        paper_bgcolor=bg,
        font=dict(color=fg, size=12),
        title_font=dict(color=fg, size=15),
        xaxis=dict(gridcolor=grid, tickfont=dict(color=fg), title_font=dict(color=fg)),
        yaxis=dict(gridcolor=grid, tickfont=dict(color=fg), title_font=dict(color=fg)),
        legend=dict(font=dict(color=fg)),
        margin=dict(t=55, b=25),
    )
    return fig


def build_kpis(df: pd.DataFrame, file_label: str) -> list:
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    total_rows = len(df)

    kpis = [
        {
            "label": "Total Records Analyzed",
            "value": f"{total_rows:,}",
            "detail": f"Source: {file_label} | {len(df.columns)} columns ({len(num_cols)} numeric).",
        }
    ]

    p_col = find_column(df, ["price", "salesamount", "revenue", "amount", "sales", "cost"], numeric_only=True)
    if p_col:
        kpis.append(
            {
                "label": f"Average {p_col}",
                "value": f"PKR {df[p_col].mean():,.0f}",
                "detail": f"Min: PKR {df[p_col].min():,.0f} | Max: PKR {df[p_col].max():,.0f} | Total: PKR {df[p_col].sum():,.0f}",
            }
        )
    else:
        kpis.append(
            {
                "label": "Data Completeness",
                "value": f"{(1 - df.isna().mean().mean()) * 100:.1f}%",
                "detail": f"Verified across {total_rows:,} rows.",
            }
        )

    r_col = find_column(df, ["rating", "score", "review", "satisfaction"], numeric_only=True)
    if r_col and any(k in r_col.lower() for k in ["rating", "score", "review", "satisfaction"]):
        kpis.append(
            {
                "label": f"Average {r_col}",
                "value": f"{df[r_col].mean():.2f} / 5.0",
                "detail": f"Highest: {df[r_col].max():.2f} | Lowest: {df[r_col].min():.2f}",
            }
        )
    else:
        others = [c for c in num_cols if c != p_col]
        if others:
            sec = others[0]
            kpis.append(
                {
                    "label": f"Total {sec}",
                    "value": f"{df[sec].sum():,.0f}",
                    "detail": f"Average: {df[sec].mean():,.2f} | Peak: {df[sec].max():,.2f}",
                }
            )
        else:
            kpis.append(
                {
                    "label": "Categories",
                    "value": f"{df[cat_cols[0]].nunique():,}" if cat_cols else "0",
                    "detail": "Distinct groups in dataset.",
                }
            )

    n_col = find_column(df, ["competitor", "brand", "product", "category", "territory", "name"], numeric_only=False)
    s_col = find_column(df, ["share", "salesamount", "revenue", "sales", "price"], numeric_only=True)
    if n_col and s_col and "competitor_name" in [c.lower() for c in df.columns]:
        leader = df.loc[df[s_col].idxmax()]
        kpis.append(
            {
                "label": "Market Leader",
                "value": str(leader[n_col]),
                "detail": f"Leads with {leader[s_col]}% share | {leader.get('Key_Advantage', 'Top rank')}",
            }
        )
    elif n_col and not df[n_col].dropna().empty:
        vc = df[n_col].dropna().value_counts()
        kpis.append(
            {
                "label": f"Top {n_col}",
                "value": str(vc.index[0])[:20],
                "detail": f"{vc.iloc[0]:,} records ({(vc.iloc[0]/total_rows)*100:.1f}% share).",
            }
        )
    else:
        kpis.append({"label": "Columns", "value": str(len(df.columns)), "detail": "Active dataset fields."})

    return kpis


def generate_swot(df: pd.DataFrame) -> dict:
    total_rows = len(df)
    cat_col = find_column(df, ["competitor", "brand", "product", "category", "territory", "name"], numeric_only=False)
    p_col = find_column(df, ["price", "salesamount", "revenue", "amount", "sales", "cost"], numeric_only=True)
    r_col = find_column(df, ["rating", "score", "review", "satisfaction"], numeric_only=True)

    if cat_col and p_col:
        grouped = df.groupby(cat_col)[p_col].agg(["mean", "sum", "count"]).reset_index().sort_values("sum", ascending=False)
        top_p = grouped.iloc[0]
        bot_p = grouped.iloc[-1]
        hi_avg = grouped.loc[grouped["mean"].idxmax()]
        lo_avg = grouped.loc[grouped["mean"].idxmin()]

        avg_all = df[p_col].mean()
        med_all = df[p_col].median()
        sum_all = df[p_col].sum()
        top_share = (top_p["sum"] / sum_all * 100) if sum_all else 0
        top2_share = (grouped.head(2)["sum"].sum() / sum_all * 100) if sum_all else 0
        spread = hi_avg["mean"] - lo_avg["mean"]

        r_note = ""
        if r_col and r_col != p_col:
            r_grp = df.groupby(cat_col)[r_col].mean()
            r_note = f" Customer satisfaction peaks with **{r_grp.idxmax()}** ({r_grp.max():.2f}/5.0)."

        return {
            "summary": f"Statistical SWOT Audit of **{total_rows:,} records** across **{grouped[cat_col].nunique()} competitors/segments** (Total {p_col}: **PKR {sum_all:,.0f}** | Mean: **PKR {avg_all:,.2f}**).",
            "strengths": [
                f"**Market Leadership by {top_p[cat_col]}:** Leads with **PKR {top_p['sum']:,.0f}** (**{top_share:.1f}%** of total market volume).",
                f"**Strong Sector Baseline:** Average {p_col} sits at **PKR {avg_all:,.2f}** (Median: **PKR {med_all:,.2f}**).{r_note}",
                f"**Multi-Competitor Visibility:** Tracks **{grouped[cat_col].nunique()} distinct players** for accurate benchmarking.",
            ],
            "weaknesses": [
                f"**High Market Concentration:** Top 2 players control **{top2_share:.1f}%** of total {p_col}, leaving tail segments under-monetized.",
                f"**Lagging Segment ({bot_p[cat_col]}):** Generates only **PKR {bot_p['sum']:,.0f}** (**{(bot_p['sum']/sum_all*100) if sum_all else 0:.1f}%** share).",
                f"**Wide Price Dispersion:** A **PKR {spread:,.2f}** gap separates **{hi_avg[cat_col]}** (PKR {hi_avg['mean']:,.0f}) from **{lo_avg[cat_col]}** (PKR {lo_avg['mean']:,.0f}).",
            ],
            "opportunities": [
                f"**Mid-Market Value Corridor (PKR {lo_avg['mean']:,.0f} – PKR {avg_all:,.0f}):** Capture price-sensitive buyers switching from **{hi_avg[cat_col]}**.",
                f"**Scale {top_p[cat_col]}'s Winning Strategy:** Replicating top-segment tactics across mid-tier segments can lift volume by **15%–25%**.",
                f"**Premium Upsell Above Median (PKR {med_all:,.0f}):** Introduce bundled warranties and loyalty tiers for high-ticket customers.",
            ],
            "threats": [
                f"**Budget Price War from {lo_avg[cat_col]}:** Priced at **PKR {lo_avg['mean']:,.0f}** (**{((avg_all - lo_avg['mean'])/avg_all*100) if avg_all else 0:.1f}%** below market average).",
                f"**Dependency on {top_p[cat_col]} ({top_share:.1f}%):** Over-reliance on a single segment exposes revenue to competitive disruption.",
                f"**Margin Pressure at Top Tier:** Offerings above **PKR {hi_avg['mean']:,.0f}** risk churn without superior perceived quality.",
            ],
            "actions": [
                f"**1. Price Calibration (0–30 Days):** Position core SKU near **PKR {avg_all:,.0f}** and test elasticity in the **What-If Profit Simulator** tab.",
                f"**2. Defend Leader Share ({top_p[cat_col]}):** Lock in top-tier buyers with retention bundles.",
                f"**3. Reposition {bot_p[cat_col]} (30–60 Days):** Audit promotional gaps or reallocate budget to top-3 performers.",
            ],
        }

    return {
        "summary": f"Dataset audit of **{total_rows:,} records**.",
        "strengths": [f"Structured dataset with {total_rows:,} records."],
        "weaknesses": ["Numeric price/sales column not found."],
        "opportunities": ["Upload numeric sales/price columns for full modeling."],
        "threats": ["Limited quantitative tracking."],
        "actions": ["1. Upload a CSV/Excel file with numeric columns."],
    }


# --- 7. SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.display_name}")
    st.caption(f"Analyst ID: `@{st.session_state.current_user}`")
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.session_state.display_name = ""
        st.rerun()

    st.divider()
    st.markdown("### 📂 Upload Market Data")
    uploaded_files = st.file_uploader(
        "Upload 1 or More CSV / Excel Files",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        dfs, names = [], []
        for f in uploaded_files:
            try:
                t_df = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f)
                t_df["Source_File"] = f.name
                dfs.append(t_df)
                names.append(f.name)
            except Exception as e:
                st.error(f"Error reading {f.name}: {e}")
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
            file_label = f"{len(names)} File(s): {', '.join(names)}"
            st.success(f"Loaded {len(names)} file(s) ({len(df):,} rows)")
        else:
            df = load_sample_data()
            file_label = "Default Benchmark"
    else:
        df = load_sample_data()
        file_label = "Default Benchmark"
        st.info("Showing Default Benchmark Data")

    st.download_button(
        label="Download Sample Template",
        data=load_sample_data().to_csv(index=False).encode("utf-8"),
        file_name="competitor_benchmark_template.csv",
        mime="text/csv",
        use_container_width=True,
    )


# --- 8. TOP-RIGHT 3D GLASSMORPHISM SLIDING TOGGLE ---
_, top_right = st.columns([4.8, 1.2])
with top_right:
    st.markdown(
        f"""
        <div class="glass-wrap">
            <div class="glass-pill">
                <span class="glass-lbl-left">Dark</span>
                <div class="glass-knob">{knob_icon}</div>
                <span class="glass-lbl-right">Light</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    btn_txt = "Switch to Dark" if st.session_state.theme_mode == "Light" else "Switch to Light"
    if st.button(btn_txt, key="theme_toggle_btn", use_container_width=True):
        st.session_state.theme_mode = "Dark" if st.session_state.theme_mode == "Light" else "Light"
        st.rerun()


# --- 9. EXECUTIVE HERO BANNER (NO TUTORIAL BOX) ---
profile_name = detect_dataset_profile(df)
st.markdown(
    f"""
    <div class="hero-box">
        <div class="hero-tag">STRATEX AI • {profile_name}</div>
        <h1 class="hero-heading">AI-Powered Competitor Intelligence & Market Analysis</h1>
        <p class="hero-sub">Executive Multi-Metric Analytics, Competitor Duel, Data-Driven SWOT & What-If Profit Simulator</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 10. HOVER KPI CARDS ---
kpis = build_kpis(df, file_label)
k_cols = st.columns(4)
for idx, kpi in enumerate(kpis):
    with k_cols[idx]:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-value">{kpi['value']}</div>
                <div class="kpi-hint">Hover cursor for full details</div>
                <div class="kpi-detail">{kpi['detail']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# --- 11. MAIN TABS ---
tab1, tab2, tab3 = st.tabs(
    [
        "📊 Executive Visual Analytics & Duel",
        "🧠 Comprehensive SWOT Intelligence",
        "🎛️ What-If Price & Profit Simulator",
    ]
)

with tab1:
    cat_options = df.select_dtypes(exclude="number").columns.tolist()
    default_cat = find_column(df, ["competitor", "brand", "product", "category", "territory", "name"], numeric_only=False)
    num_cols = df.select_dtypes(include="number").columns.tolist()

    price_col = find_column(df, ["price", "cost", "unitprice", "amount", "salesamount"], numeric_only=True)
    rating_col = find_column(df, ["rating", "score", "review", "satisfaction"], numeric_only=True)
    share_col = find_column(df, ["market_share", "share", "revenue", "salesamount"], numeric_only=True)
    volume_col = find_column(df, ["monthly_sales", "sales", "quantity", "volume", "units"], numeric_only=True)

    rem1 = [c for c in num_cols if c != price_col]
    if rating_col == price_col and rem1:
        rating_col = rem1[0]
    rem2 = [c for c in num_cols if c not in [price_col, rating_col]]
    if share_col in [price_col, rating_col] and rem2:
        share_col = rem2[0]
    rem3 = [c for c in num_cols if c not in [price_col, rating_col, share_col]]
    if volume_col in [price_col, rating_col, share_col] and rem3:
        volume_col = rem3[0]

    c_h, c_s = st.columns([2.2, 1])
    with c_h:
        st.subheader(f"4-Dimension Visual Intelligence ({profile_name})")
        st.caption("Each chart presents a unique visual angle with exact values and executive insights.")
    with c_s:
        selected_cat = (
            st.selectbox(
                "Compare Competitor / Segment By:",
                options=cat_options,
                index=cat_options.index(default_cat) if default_cat in cat_options else 0,
            )
            if cat_options
            else None
        )

    palette = ["#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6", "#14B8A6"]

    if selected_cat and num_cols:
        agg_spec = {}
        for col in set([c for c in [price_col, rating_col, share_col, volume_col] if c]):
            agg_spec[col] = "mean" if col in [price_col, rating_col] else "sum"

        summary_df = df.groupby(selected_cat, as_index=False).agg(agg_spec).head(12)

        g1, g2 = st.columns(2)
        with g1:
            if price_col:
                p_df = summary_df.sort_values(price_col, ascending=False)
                avg_p = p_df[price_col].mean()
                fig1 = px.bar(
                    p_df,
                    x=selected_cat,
                    y=price_col,
                    text=price_col,
                    color=selected_cat,
                    title=f"1. Price & Cost Benchmark ({price_col})",
                    color_discrete_sequence=palette,
                )
                fig1.update_traces(texttemplate="%{text:,.1f}", textposition="outside")
                fig1.add_hline(
                    y=avg_p,
                    line_dash="dash",
                    line_color="#EF4444",
                    annotation_text=f"Market Avg: {avg_p:,.1f}",
                    annotation_position="top right",
                )
                fig1.update_layout(showlegend=False)
                st.plotly_chart(style_chart(fig1), use_container_width=True)
                st.markdown(
                    f"<div class='chart-note'><b>Pricing Takeaway:</b> <b>{p_df.iloc[0][selected_cat]}</b> has the highest price ({p_df.iloc[0][price_col]:,.1f}), while <b>{p_df.iloc[-1][selected_cat]}</b> is lowest ({p_df.iloc[-1][price_col]:,.1f}).</div>",
                    unsafe_allow_html=True,
                )

        with g2:
            radar_cols = list(dict.fromkeys([c for c in [price_col, rating_col, share_col, volume_col] if c and c in summary_df.columns]))
            if len(radar_cols) >= 3:
                fig2 = go.Figure()
                for _, row_r in summary_df.head(5).iterrows():
                    norm = [round((row_r[rc] / summary_df[rc].max() * 100) if summary_df[rc].max() else 0, 1) for rc in radar_cols]
                    fig2.add_trace(
                        go.Scatterpolar(
                            r=norm + [norm[0]],
                            theta=radar_cols + [radar_cols[0]],
                            fill="toself",
                            name=str(row_r[selected_cat]),
                        )
                    )
                fig2.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 105])),
                    title="2. 360° Multi-Metric Competitor Radar (Normalized %)",
                )
                st.plotly_chart(style_chart(fig2), use_container_width=True)
                st.markdown(
                    "<div class='chart-note'><b>Radar Takeaway:</b> Compares overall strength across all KPIs simultaneously—wider shapes show stronger all-round dominance.</div>",
                    unsafe_allow_html=True,
                )
            elif rating_col:
                r_df = summary_df.sort_values(rating_col, ascending=True)
                fig2 = px.bar(
                    r_df,
                    x=rating_col,
                    y=selected_cat,
                    orientation="h",
                    text=rating_col,
                    color=selected_cat,
                    title=f"2. Customer Satisfaction Ranking ({rating_col})",
                    color_discrete_sequence=palette,
                )
                fig2.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
                fig2.update_layout(showlegend=False)
                st.plotly_chart(style_chart(fig2), use_container_width=True)
                st.markdown(
                    "<div class='chart-note'><b>Quality Takeaway:</b> Ranks competitors from lowest to highest satisfaction score.</div>",
                    unsafe_allow_html=True,
                )

        g3, g4 = st.columns(2)
        with g3:
            if share_col:
                s_df = summary_df.sort_values(share_col, ascending=False)
                fig3 = px.pie(
                    s_df,
                    names=selected_cat,
                    values=share_col,
                    hole=0.52,
                    title=f"3. Market Share Distribution (% of {share_col})",
                    color_discrete_sequence=palette,
                )
                fig3.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    pull=[0.06 if i == 0 else 0 for i in range(len(s_df))],
                )
                st.plotly_chart(style_chart(fig3), use_container_width=True)
                tot_s = s_df[share_col].sum()
                pct_s = (s_df.iloc[0][share_col] / tot_s * 100) if tot_s else 0
                st.markdown(
                    f"<div class='chart-note'><b>Market Share Takeaway:</b> <b>{s_df.iloc[0][selected_cat]}</b> leads the market with <b>{pct_s:.1f}%</b> share.</div>",
                    unsafe_allow_html=True,
                )

        with g4:
            if price_col and volume_col and price_col != volume_col:
                fig4 = px.scatter(
                    summary_df,
                    x=price_col,
                    y=volume_col,
                    size=share_col if share_col and (summary_df[share_col] > 0).all() else None,
                    color=selected_cat,
                    text=selected_cat,
                    size_max=44,
                    title=f"4. Value-for-Money Bubble Matrix: {price_col} vs. {volume_col}",
                    color_discrete_sequence=palette,
                )
                fig4.update_traces(textposition="top center")
                fig4.add_vline(x=summary_df[price_col].mean(), line_dash="dot", line_color="#94A3B8")
                fig4.add_hline(y=summary_df[volume_col].mean(), line_dash="dot", line_color="#94A3B8")
                fig4.update_layout(showlegend=False)
                st.plotly_chart(style_chart(fig4), use_container_width=True)
                st.markdown(
                    f"<div class='chart-note'><b>Positioning Takeaway:</b> Bubble size shows share; top-left players achieve high <b>{volume_col}</b> at competitive prices.</div>",
                    unsafe_allow_html=True,
                )
            else:
                fig4 = px.area(
                    summary_df,
                    x=selected_cat,
                    y=price_col or num_cols[0],
                    markers=True,
                    title=f"4. Demand & Value Curve ({price_col or num_cols[0]})",
                    color_discrete_sequence=["#4F46E5"],
                )
                st.plotly_chart(style_chart(fig4), use_container_width=True)
                st.markdown(
                    "<div class='chart-note'><b>Curve Takeaway:</b> Shows peaks and gaps across segments.</div>",
                    unsafe_allow_html=True,
                )

        st.divider()
        st.subheader("⚔️ Head-to-Head Competitor Comparison")
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
                va, vb = float(row_a[m_col]), float(row_b[m_col])
                if any(k in m_col.lower() for k in ["price", "cost"]):
                    win = comp_a if va < vb else (comp_b if vb < va else "Tie")
                else:
                    win = comp_a if va > vb else (comp_b if vb > va else "Tie")
                duel_rows.append(
                    {"Metric": m_col, comp_a: round(va, 2), comp_b: round(vb, 2), "Difference": round(va - vb, 2), "Advantage": win}
                )
            st.dataframe(pd.DataFrame(duel_rows), use_container_width=True, hide_index=True)

        st.subheader("🏆 Unified Competitor Scorecard")
        sc = summary_df.copy()
        if share_col and sc[share_col].sum() > 0:
            sc["Market_Share_%"] = (sc[share_col] / sc[share_col].sum() * 100).round(2)
            sc = sc.sort_values("Market_Share_%", ascending=False)
        sc.insert(0, "Rank", range(1, len(sc) + 1))
        st.dataframe(sc, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📋 Dataset Preview (Top 500 Rows)")
    st.dataframe(df.head(500), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("🧠 Comprehensive Data-Driven SWOT & Strategic Roadmap")
    if st.button("Generate Full Executive SWOT Report"):
        swot = generate_swot(df)
        st.info(swot["summary"])
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📈 Strengths")
            for x in swot["strengths"]:
                st.markdown(f"- {x}")
            st.markdown("### 💡 Opportunities")
            for x in swot["opportunities"]:
                st.markdown(f"- {x}")
        with c2:
            st.markdown("### ⚠️ Weaknesses")
            for x in swot["weaknesses"]:
                st.markdown(f"- {x}")
            st.markdown("### 🛡️ Threats")
            for x in swot["threats"]:
                st.markdown(f"- {x}")
        st.divider()
        st.markdown("### 🚩 Prioritized Strategic Action Roadmap")
        for a in swot["actions"]:
            st.markdown(a)

with tab3:
    st.subheader("🎛️ What-If Price, Demand & Profit Decision Simulator")
    st.caption("Simulate how price adjustments, unit costs, and marketing campaigns impact your revenue and net profit.")

    cat_sim = find_column(df, ["competitor", "brand", "product", "category", "name"], numeric_only=False)
    p_sim = find_column(df, ["price", "cost", "unitprice", "amount", "salesamount"], numeric_only=True)
    v_sim = find_column(df, ["monthly_sales", "sales", "quantity", "volume", "units"], numeric_only=True)

    base_p = float(df[p_sim].mean()) if p_sim else 4500.0
    base_v = float(df[v_sim].mean()) if (v_sim and v_sim != p_sim) else 1850.0

    if cat_sim and not df[cat_sim].dropna().empty:
        b_list = df[cat_sim].dropna().astype(str).unique().tolist()
        target_b = st.selectbox("Select Brand / Segment to Simulate:", options=b_list, index=0)
        b_df = df[df[cat_sim].astype(str) == target_b]
        if p_sim:
            base_p = float(b_df[p_sim].mean())
        if v_sim and v_sim != p_sim:
            base_v = float(b_df[v_sim].mean())
    else:
        target_b = "My_Brand"

    s1, s2, s3 = st.columns(3)
    with s1:
        p_chg = st.slider("Price Adjustment (%)", -30, 30, 0, 1)
    with s2:
        cost_pct = st.slider("Product Unit Cost (% of Base Price)", 20, 85, 55, 5)
    with s3:
        promo_pct = st.slider("Marketing / Promo Demand Boost (%)", 0, 40, 10, 2)

    new_p = base_p * (1 + p_chg / 100.0)
    mult = max(0.2, 1 + (-1.35 * (p_chg / 100.0)) + (promo_pct / 100.0))
    new_v = base_v * mult
    u_cost = base_p * (cost_pct / 100.0)

    old_rev, new_rev = base_p * base_v, new_p * new_v
    old_prof, new_prof = (base_p - u_cost) * base_v, (new_p - u_cost) * new_v
    rev_d = ((new_rev - old_rev) / old_rev * 100) if old_rev else 0
    prof_d = ((new_prof - old_prof) / abs(old_prof) * 100) if old_prof else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Simulated Unit Price", f"PKR {new_p:,.0f}", f"{p_chg:+}%")
    m2.metric("Projected Sales Volume", f"{new_v:,.0f} units", f"{(mult - 1)*100:+.1f}%")
    m3.metric("Projected Total Revenue", f"PKR {new_rev:,.0f}", f"{rev_d:+.1f}%")
    m4.metric("Projected Net Profit", f"PKR {new_prof:,.0f}", f"{prof_d:+.1f}%")

    sim_df = pd.DataFrame(
        {
            "Scenario": ["Current Baseline", "Simulated Strategy", "Current Baseline", "Simulated Strategy"],
            "Metric": ["Total Revenue (PKR)", "Total Revenue (PKR)", "Net Profit (PKR)", "Net Profit (PKR)"],
            "Amount": [old_rev, new_rev, old_prof, new_prof],
        }
    )
    fig_s = px.bar(
        sim_df,
        x="Metric",
        y="Amount",
        color="Scenario",
        barmode="group",
        text="Amount",
        title=f"Financial Impact Simulation for {target_b}",
        color_discrete_sequence=["#94A3B8", "#4F46E5"],
    )
    fig_s.update_traces(texttemplate="PKR %{text:,.0f}", textposition="outside")
    st.plotly_chart(style_chart(fig_s), use_container_width=True)

    rep = (
        f"EXECUTIVE COMPETITOR & PRICING SIMULATION REPORT\n"
        f"Brand: {target_b} | Dataset: {profile_name} ({len(df):,} rows)\n\n"
        f"Baseline Price: PKR {base_p:,.2f} -> Simulated Price: PKR {new_p:,.2f} ({p_chg:+}%)\n"
        f"Baseline Volume: {base_v:,.0f} -> Projected Volume: {new_v:,.0f} ({(mult-1)*100:+.1f}%)\n"
        f"Baseline Revenue: PKR {old_rev:,.2f} -> Projected Revenue: PKR {new_rev:,.2f} ({rev_d:+.1f}%)\n"
        f"Baseline Profit: PKR {old_prof:,.2f} -> Projected Profit: PKR {new_prof:,.2f} ({prof_d:+.1f}%)\n"
    )
    st.download_button(
        label="Download Simulation Report (.txt)",
        data=rep.encode("utf-8"),
        file_name=f"{target_b}_simulation_report.txt",
        mime="text/plain",
    )
