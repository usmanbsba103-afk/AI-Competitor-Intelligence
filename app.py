import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(
    page_title="CompetitorIQ | AI Market Intelligence",
    page_icon=":material/analytics:",
    layout="wide"
)

# 2. Custom Royal Green & White Executive CSS
st.markdown("""
<style>
    /* Royal Green Hero Banner */
    .royal-banner {
        background: linear-gradient(135deg, #0B4F32 0%, #146C43 100%);
        padding: 26px 32px;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 22px;
        box-shadow: 0 6px 18px rgba(11, 79, 50, 0.14);
    }
    .royal-banner h1 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.3px;
    }
    .royal-banner p {
        color: #D8F3DC !important;
        margin: 6px 0 0 0;
        font-size: 14px;
    }
    /* Executive KPI Metric Cards */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #D8E8E0;
        border-left: 5px solid #0B4F32;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .kpi-title {
        color: #4A6B5D;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .kpi-value {
        color: #0B4F32;
        font-size: 24px;
        font-weight: 700;
    }
    /* Login Card Header */
    .login-header {
        background: linear-gradient(135deg, #0B4F32 0%, #146C43 100%);
        color: white;
        padding: 24px;
        border-radius: 12px 12px 0 0;
        text-align: center;
    }
    /* Primary Action Buttons */
    div.stButton > button:first-child {
        background-color: #0B4F32;
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 0.55rem 1.3rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #083B25;
        color: #FFFFFF;
        box-shadow: 0 4px 10px rgba(11, 79, 50, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# 3. Automatic Backend API Key Loader (Zero User Input Needed)
def get_gemini_model():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

# 4. Authentication Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "users_db" not in st.session_state:
    st.session_state["users_db"] = {"admin": "fyp2026", "usman": "12345"}
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""

# ================= LOGIN / SIGN-UP PORTAL =================
if not st.session_state["authenticated"]:
    col_l, col_c, col_r = st.columns([1, 1.25, 1])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="login-header">
            <h2 style="margin:0; color:white;">CompetitorIQ Portal</h2>
            <p style="margin:6px 0 0 0; color:#D8F3DC; font-size:14px;">AI-Powered Competitor Intelligence & Market Analysis</p>
        </div>
        """, unsafe_allow_html=True)

        tab_signin, tab_signup = st.tabs([":material/login: Sign In", ":material/person_add: Create Account"])

        with tab_signin:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In to Dashboard", use_container_width=True)

                if submitted:
                    if username in st.session_state["users_db"] and st.session_state["users_db"][username] == password:
                        st.session_state["authenticated"] = True
                        st.session_state["current_user"] = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify your username and password.")
            st.caption("Demo Credentials — Username: `admin` | Password: `fyp2026`")

        with tab_signup:
            with st.form("register_form"):
                new_user = st.text_input("Choose a Username")
                new_pass = st.text_input("Create Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                reg_submitted = st.form_submit_button("Register Account", use_container_width=True)

                if reg_submitted:
                    if not new_user or not new_pass:
                        st.warning("All fields are required.")
                    elif new_user in st.session_state["users_db"]:
                        st.error("This username is already taken.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    else:
                        st.session_state["users_db"][new_user] = new_pass
                        st.success("Account registered successfully! Please sign in.")
    st.stop()

# ================= MAIN EXECUTIVE DASHBOARD =================

# Top Royal Green Banner
st.markdown(f"""
<div class="royal-banner">
    <h1>AI-Powered Competitor Intelligence & Market Analysis System</h1>
    <p>Logged in as <b>{st.session_state['current_user'].capitalize()}</b> &bull; Real-Time Market Tracking, Sentiment Intelligence & Strategic Advisory</p>
</div>
""", unsafe_allow_html=True)

# Clean Sidebar (No API Key Box!)
st.sidebar.markdown(f"### :material/account_circle: {st.session_state['current_user'].capitalize()}")
if st.sidebar.button("Sign Out", icon=":material/logout:", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = ""
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader(":material/database: Market Dataset")
uploaded_file = st.sidebar.file_uploader("Upload Competitor Data (.csv / .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.sidebar.success("Custom dataset active", icon=":material/check_circle:")
else:
    df = pd.read_csv("sample_data.csv")
    st.sidebar.info("Using default benchmark dataset", icon=":material/info:")

# Downloadable Sample Template in Sidebar
st.sidebar.download_button(
    label="Download CSV Template",
    data=df.to_csv(index=False),
    file_name="competitor_template.csv",
    mime="text/csv",
    icon=":material/download:",
    use_container_width=True
)

# Sentiment Classification Engine
def classify_sentiment(review):
    text = str(review).lower()
    positive_words = ["amazing", "best", "good", "comfortable", "premium", "great", "love", "fast"]
    negative_words = ["late", "poor", "cheap", "expensive", "bad", "worst", "slow", "broken"]
    pos = sum(w in text for w in positive_words)
    neg = sum(w in text for w in negative_words)
    if pos > neg:
        return "Positive"
    elif neg > pos:
        return "Negative"
    return "Neutral"

df["Sentiment"] = df["Customer_Review"].apply(classify_sentiment)

# Executive KPI Summary Row
avg_price = int(df["Price"].mean())
top_comp = df.loc[df["Rating"].idxmax(), "Competitor_Name"]
top_rating = df["Rating"].max()
pos_rate = int((df["Sentiment"] == "Positive").mean() * 100)

my_brand_rows = df[df["Competitor_Name"].str.lower() == "my_brand"]
alert_count = 0
if not my_brand_rows.empty:
    my_price = my_brand_rows["Price"].mean()
    cheaper_comps = df[(df["Competitor_Name"].str.lower() != "my_brand") & (df["Price"] < my_price)]
    alert_count = len(cheaper_comps)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Average Market Price</div><div class="kpi-value">PKR {avg_price:,}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Top Rated Player</div><div class="kpi-value">{top_comp} ({top_rating}★)</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Positive Sentiment</div><div class="kpi-value">{pos_rate}%</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Active Price Alerts</div><div class="kpi-value">{alert_count}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Royal Green Chart Palette
ROYAL_PALETTE = ["#0B4F32", "#1B7A50", "#40916C", "#74C69D", "#2D6A4F"]

# Main Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    ":material/monitoring: Market Overview & AI SWOT",
    ":material/travel_explore: Live Web Intelligence",
    ":material/smart_toy: AI Strategy Advisor"
])

# ================= TAB 1: MARKET OVERVIEW & CONCISE AI SWOT =================
with tab1:
    st.subheader(":material/notifications_active: Automated Price Monitoring")
    if not my_brand_rows.empty:
        if alert_count > 0:
            for _, row in cheaper_comps.iterrows():
                diff = int(my_price - row["Price"])
                st.error(f"**Price Undercut Alert:** **{row['Competitor_Name']}** ({row['Product_Name']}) is priced **PKR {diff:,}** below your brand (Current Price: PKR {row['Price']:,}).", icon=":material/warning:")
        else:
            st.success("**Competitive Edge:** No competitor is currently undercutting your pricing.", icon=":material/verified:")
    else:
        st.info("Add 'My_Brand' rows to your dataset to activate automated price undercut alerts.", icon=":material/info:")

    st.subheader(":material/table_view: Competitor Benchmark Table")
    st.dataframe(df, width="stretch")

    st.subheader(":material/bar_chart: Visual Market Positioning")
    c1, c2, c3 = st.columns(3)
    with c1:
        fig_price = px.bar(df, x="Competitor_Name", y="Price", color="Product_Name", title="Price Comparison (PKR)", barmode="group", color_discrete_sequence=ROYAL_PALETTE)
        fig_price.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_price, width="stretch")
    with c2:
        fig_pos = px.scatter(df, x="Price", y="Rating", color="Competitor_Name", size="Price", hover_name="Product_Name", title="Price vs. Customer Rating", color_discrete_sequence=ROYAL_PALETTE)
        fig_pos.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_pos, width="stretch")
    with c3:
        fig_sent = px.pie(df, names="Sentiment", title="Review Sentiment Distribution", color_discrete_sequence=["#0B4F32", "#C0392B", "#7F8C8D"])
        st.plotly_chart(fig_sent, width="stretch")

    st.divider()
    st.subheader(":material/psychology: Executive AI SWOT & Action Plan")

    if st.button("Generate Concise SWOT Report", icon=":material/auto_awesome:"):
        model = get_gemini_model()
        if not model:
            st.error("System API key is not configured in server secrets.", icon=":material/error:")
        else:
            with st.spinner("Generating concise strategic insights..."):
                try:
                    prompt = f"""
                    You are a Senior Market Intelligence Analyst. Analyze this competitor dataset and provide a SHORT, CRISP, TO-THE-POINT executive brief.
                    Rules:
                    - NO long paragraphs. Use short bullet points (max 12-15 words per bullet).
                    - Provide:
                      1. **Competitor Pain Points** (3 short bullets)
                      2. **SWOT Matrix for My_Brand** (2 short bullets each for Strengths, Weaknesses, Opportunities, Threats)
                      3. **3 Immediate Strategic Actions** (3 short, actionable recommendations)
                    
                    Dataset:
                    {df.to_string()}
                    """
                    response = model.generate_content(prompt)
                    st.session_state["swot_report"] = response.text
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    if "swot_report" in st.session_state:
        st.success("Executive Report Ready", icon=":material/task_alt:")
        st.markdown(st.session_state["swot_report"])
        st.download_button(
            label="Export Strategy Report (.txt)",
            data=st.session_state["swot_report"],
            file_name="CompetitorIQ_Executive_Report.txt",
            mime="text/plain",
            icon=":material/download:"
        )

# ================= TAB 2: LIVE COMPETITOR WEB SCRAPER =================
with tab2:
    st.subheader(":material/language: Live Competitor Webpage Analyzer")
    st.write("Enter a competitor product or landing page URL to extract live positioning data and generate counter-strategies.")
    
    url_input = st.text_input("Target Competitor URL:", placeholder="https://www.apple.com/airpods/")
    
    if st.button("Extract & Analyze Page", icon=":material/search:"):
        model = get_gemini_model()
        if not url_input:
            st.warning("Please enter a valid URL.", icon=":material/link_off:")
        elif not model:
            st.error("System API key is not configured in server secrets.", icon=":material/error:")
        else:
            with st.spinner("Extracting live webpage content..."):
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    res = requests.get(url_input, headers=headers, timeout=10)
                    soup = BeautifulSoup(res.text, "html.parser")
                    
                    page_title = soup.title.string.strip() if soup.title else "No Title"
                    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:10]]
                    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")[:6]]
                    
                    scraped_summary = f"Title: {page_title}\nHeadings: {headings}\nHighlights: {paragraphs}"
                    
                    with st.expander("Inspect Extracted Raw Content", icon=":material/code:"):
                        st.text(scraped_summary)
                    
                    scrape_prompt = f"""
                    Provide a concise, bulleted competitive intelligence brief based on this scraped webpage:
                    1. **Core Offering & Value Proposition** (2 short bullets)
                    2. **Target Audience & Positioning** (2 short bullets)
                    3. **Recommended Counter-Strategy** (2 short actionable bullets)
                    
                    Scraped Content:
                    {scraped_summary}
                    """
                    ai_web_analysis = model.generate_content(scrape_prompt)
                    st.success("Web Intelligence Analysis Complete", icon=":material/task_alt:")
                    st.markdown(ai_web_analysis.text)
                except Exception as e:
                    st.error(f"Unable to extract webpage content: {e}")

# ================= TAB 3: AI STRATEGY ADVISOR CHATBOT =================
with tab3:
    st.subheader(":material/forum: Interactive AI Strategy Advisor")
    st.write("Ask direct strategic questions about pricing, customer pain points, or market positioning based on your live dataset.")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_question = st.chat_input("Ask a strategic question (e.g., How can we outperform Competitor A?)...")

    if user_question:
        model = get_gemini_model()
        if not model:
            st.error("System API key is not configured in server secrets.", icon=":material/error:")
        else:
            st.session_state["chat_history"].append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Formulating strategic response..."):
                    try:
                        chat_prompt = f"""
                        You are an Executive Market Strategy Advisor for 'My_Brand'. Answer the user's question concisely using short bullet points based strictly on this dataset.
                        
                        Dataset:
                        {df.to_string()}
                        
                        Question: {user_question}
                        """
                        reply = model.generate_content(chat_prompt).text
                        st.markdown(reply)
                        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"Error: {e}")