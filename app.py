import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai

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
        .login-card {
            background-color: #F2F8F5;
            border: 1px solid #D5E8DF;
            border-top: 5px solid #0B4F32;
            padding: 2rem;
            border-radius: 10px;
            margin-top: 2rem;
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


# --- HELPER FUNCTIONS ---
def get_gemini_client():
    api_key = ""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    return genai.Client(api_key=api_key.strip())


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


def scrape_competitor_page(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(url, headers=headers, timeout=12)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "N/A"
    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        meta_desc = meta_tag["content"].strip()
    headings = [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2"])[:8]]
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")[:6]]
    return (
        f"Page Title: {title}\n"
        f"Meta Description: {meta_desc}\n"
        f"Key Headings: {' | '.join(headings)}\n"
        f"Excerpt: {' '.join(paragraphs)[:1200]}"
    )


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

# KPI SUMMARY ROW
k1, k2, k3, k4 = st.columns(4)
avg_price = df["Price"].mean() if "Price" in df.columns else 0
avg_rating = df["Customer_Rating"].mean() if "Customer_Rating" in df.columns else 0
total_sales = df["Monthly_Sales"].sum() if "Monthly_Sales" in df.columns else 0
top_leader = (
    df.loc[df["Market_Share"].idxmax(), "Competitor_Name"]
    if "Market_Share" in df.columns and "Competitor_Name" in df.columns
    else "N/A"
)

k1.metric("Tracked Competitors", len(df))
k2.metric("Average Market Price", f"PKR {avg_price:,.0f}")
k3.metric("Average Customer Rating", f"{avg_rating:.2f} / 5.0")
k4.metric("Market Share Leader", str(top_leader))

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
    st.dataframe(df, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    green_palette = ["#0B4F32", "#198754", "#2E9E6B", "#52B788", "#95D5B2"]

    with c1:
        if "Competitor_Name" in df.columns and "Price" in df.columns:
            fig_price = px.bar(
                df,
                x="Competitor_Name",
                y="Price",
                title="Price Comparison",
                color="Competitor_Name",
                color_discrete_sequence=green_palette,
            )
            fig_price.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_price, use_container_width=True)

    with c2:
        if "Price" in df.columns and "Customer_Rating" in df.columns:
            fig_scatter = px.scatter(
                df,
                x="Price",
                y="Customer_Rating",
                size="Monthly_Sales" if "Monthly_Sales" in df.columns else None,
                color="Competitor_Name" if "Competitor_Name" in df.columns else None,
                title="Price vs. Rating Positioning",
                color_discrete_sequence=green_palette,
            )
            fig_scatter.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_scatter, use_container_width=True)

    with c3:
        if "Competitor_Name" in df.columns and "Market_Share" in df.columns:
            fig_share = px.pie(
                df,
                names="Competitor_Name",
                values="Market_Share",
                hole=0.45,
                title="Market Share Distribution",
                color_discrete_sequence=green_palette,
            )
            fig_share.update_layout(paper_bgcolor="white")
            st.plotly_chart(fig_share, use_container_width=True)

# TAB 2: CONCISE AI SWOT REPORT
with tab_swot:
    st.subheader(":material/psychology: Executive AI SWOT & Action Plan")
    st.caption("Generates a concise, boardroom-ready strategic synthesis directly from your dataset.")

    if st.button("Generate Concise SWOT Report", icon=":material/auto_awesome:"):
        client = get_gemini_client()
        if not client:
            st.error("System API key is missing in Streamlit Cloud Secrets.")
        else:
            with st.spinner("Synthesizing competitive intelligence..."):
                try:
                    data_csv = df.to_csv(index=False)
                    prompt = f"""
                    You are a senior corporate strategy analyst. Analyze this competitor dataset and produce a strictly concise, executive-level SWOT & Action Plan in formal English.
                    
                    Dataset:
                    {data_csv}
                    
                    Formatting Rules:
                    - Keep every bullet point under 15 words.
                    - Provide exactly 3 bullet points per section.
                    - Use bold headings: **Strengths**, **Weaknesses**, **Opportunities**, **Threats**, and **Top 3 Strategic Actions**.
                    - Cite exact numbers from the dataset. No introductory or closing filler text.
                    """
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# TAB 3: LIVE WEB SCRAPER INTELLIGENCE
with tab_scraper:
    st.subheader(":material/language: Live Competitor Website Analyzer")
    st.caption("Extract live positioning, headlines, and value propositions from any public competitor URL.")

    target_url = st.text_input("Competitor Website URL", placeholder="https://www.example.com")
    if st.button("Analyze Live Webpage", icon=":material/travel_explore:"):
        if not target_url.startswith("http"):
            st.warning("Please enter a valid URL starting with http:// or https://")
        else:
            client = get_gemini_client()
            if not client:
                st.error("System API key is missing in Streamlit Cloud Secrets.")
            else:
                with st.spinner("Extracting and analyzing live webpage..."):
                    try:
                        scraped_text = scrape_competitor_page(target_url)
                        prompt = f"""
                        Analyze this scraped competitor webpage content and summarize in 5 concise executive bullet points (max 15 words each):
                        1. Core Value Proposition
                        2. Target Audience
                        3. Pricing / Offer Positioning
                        4. Key Competitive Edge
                        5. Recommended Counter-Strategy
                        
                        Webpage Content:
                        {scraped_text}
                        """
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt,
                        )
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")
