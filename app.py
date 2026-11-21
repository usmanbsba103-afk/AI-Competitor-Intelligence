import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="AI Competitor Intelligence", page_icon="🚀", layout="wide")

st.title("🚀 AI-Powered Competitor Intelligence & Market Analysis System")
st.write("Automated Competitor Tracking, Price Alerts, Sentiment Analysis, Live Scraping & AI Strategy Chatbot.")

# 2. Sidebar Setup
st.sidebar.header("🔑 1. AI Configuration")
api_key = st.sidebar.text_input("Apni Free Gemini API Key dalein:", type="password")

st.sidebar.header("📂 2. Upload Market Data")
uploaded_file = st.sidebar.file_uploader("Excel (.xlsx) ya CSV file upload karein", type=["csv", "xlsx"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.sidebar.success("✅ File upload ho gayi!")
else:
    df = pd.read_csv("sample_data.csv")

# Sentiment Analysis Function
def get_sentiment(review):
    text = str(review).lower()
    positive_words = ["amazing", "best", "good", "comfortable", "premium", "great", "love", "fast"]
    negative_words = ["late", "poor", "cheap", "expensive", "bad", "worst", "slow", "broken"]
    pos = sum(word in text for word in positive_words)
    neg = sum(word in text for word in negative_words)
    if pos > neg:
        return "Positive 😊"
    elif neg > pos:
        return "Negative 😡"
    return "Neutral 😐"

df["AI_Sentiment"] = df["Customer_Review"].apply(get_sentiment)

# 3. Main Navigation Tabs (Ab 3 Tabs hain!)
tab1, tab2, tab3 = st.tabs([
    "📊 Market & AI SWOT Report",
    "🌐 Live Competitor Scraper",
    "💬 AI Strategy Chatbot"
])

# ================= TAB 1: DATASET, PRICE ALERTS & AI SWOT =================
with tab1:
    # Smart Price Alert Engine
    st.subheader("🚨 Real-Time Competitor Price Alerts")
    my_brand_rows = df[df["Competitor_Name"].str.lower() == "my_brand"]
    if not my_brand_rows.empty:
        my_price = my_brand_rows["Price"].mean()
        cheaper_comps = df[(df["Competitor_Name"].str.lower() != "my_brand") & (df["Price"] < my_price)]
        if not cheaper_comps.empty:
            for _, row in cheaper_comps.iterrows():
                diff = int(my_price - row["Price"])
                st.error(f"⚠️ **Price Drop Alert:** **{row['Competitor_Name']}** ({row['Product_Name']}) aapse **PKR {diff}** sasta bech raha hai (Price: PKR {row['Price']})!")
        else:
            st.success("✅ **Good News:** Market mein koi bhi competitor aapse sasta nahi bech raha!")
    else:
        st.info("💡 Price alerts ke liye dataset mein 'My_Brand' shamil karein.")

    st.subheader("📋 Competitor Data & AI Sentiment Overview")
    st.dataframe(df, width="stretch")

    st.subheader("📈 Visual Market & Positioning Charts")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_price = px.bar(df, x="Competitor_Name", y="Price", color="Product_Name", title="Price Comparison (PKR)", barmode="group")
        st.plotly_chart(fig_price, width="stretch")
    with col2:
        fig_pos = px.scatter(df, x="Price", y="Rating", color="Competitor_Name", size="Price", hover_name="Product_Name", title="Price vs. Rating Matrix")
        st.plotly_chart(fig_pos, width="stretch")
    with col3:
        fig_sent = px.pie(df, names="AI_Sentiment", title="Customer Sentiment Breakdown")
        st.plotly_chart(fig_sent, width="stretch")

    st.divider()
    st.subheader("🧠 AI SWOT Analysis & Winning Strategy")

    if st.button("✨ Generate AI SWOT Report"):
        if not api_key:
            st.warning("⚠️ Pehle left sidebar mein apni Free Gemini API Key dalein!")
        else:
            with st.spinner("AI aapke competitors ka data analyze kar raha hai..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    prompt = f"""
                    You are an expert Market Intelligence Analyst. Analyze the following competitor dataset and provide:
                    1. Key Competitor Weaknesses (Customer Pain Points)
                    2. SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats) for 'My_Brand'
                    3. 3 Actionable Pricing & Marketing Strategies to beat the competitors.
                    
                    Dataset:
                    {df.to_string()}
                    """
                    response = model.generate_content(prompt)
                    st.session_state["swot_report"] = response.text
                except Exception as e:
                    st.error(f"Error aaya hai: {e}")

    if "swot_report" in st.session_state:
        st.success("✅ AI Analysis Mukammal!")
        st.markdown(st.session_state["swot_report"])
        st.download_button(
            label="📥 Download AI Strategy Report (.txt)",
            data=st.session_state["swot_report"],
            file_name="AI_Competitor_SWOT_Report.txt",
            mime="text/plain"
        )

# ================= TAB 2: LIVE WEB SCRAPER =================
with tab2:
    st.subheader("🌐 Live Competitor Website Analyzer")
    st.write("Kisi bhi competitor ki website ya product page ka link (URL) paste karein—AI khud us page ko scrape karke analyze karega.")
    
    url_input = st.text_input("Competitor Website URL dalein (e.g., https://www.apple.com/airpods/):", placeholder="https://...")
    
    if st.button("🔍 Scrape & Analyze Website"):
        if not url_input:
            st.warning("⚠️ Pehle koi valid website URL dalein!")
        elif not api_key:
            st.warning("⚠️ Left sidebar mein apni Free Gemini API Key dalein!")
        else:
            with st.spinner("Website se live data scrape ho raha hai..."):
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    res = requests.get(url_input, headers=headers, timeout=10)
                    soup = BeautifulSoup(res.text, "html.parser")
                    
                    page_title = soup.title.string.strip() if soup.title else "No Title Found"
                    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:12]]
                    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")[:8]]
                    
                    scraped_summary = f"Page Title: {page_title}\nKey Headings: {headings}\nContent Snippets: {paragraphs}"
                    
                    with st.expander("📄 Scraped Raw Website Data Dekhein"):
                        st.text(scraped_summary)
                    
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    scrape_prompt = f"""
                    Analyze this scraped competitor webpage content and provide:
                    1. What product/service they are selling and their main value proposition
                    2. Their target audience and marketing angle
                    3. How our brand can differentiate and beat them.
                    
                    Scraped Data:
                    {scraped_summary}
                    """
                    ai_web_analysis = model.generate_content(scrape_prompt)
                    st.success("✅ Live Website Analysis Mukammal!")
                    st.markdown(ai_web_analysis.text)
                except Exception as e:
                    st.error(f"Website scrape karne mein masla aaya: {e}")

# ================= TAB 3: AI STRATEGY CHATBOT =================
with tab3:
    st.subheader("💬 AI Market Strategy Assistant (Chat with Your Data)")
    st.write("Apne competitor dataset ke baare mein AI se koi bhi sawal poochein (e.g., 'Competitor A ko kaise beat karein?' ya 'Best price kya honi chahiye?').")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Purani chat messages dikhayein
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Naya sawal likhne ka box
    user_question = st.chat_input("Apna sawal yahan likhein aur Enter dabayein...")

    if user_question:
        if not api_key:
            st.warning("⚠️ Pehle left sidebar mein apni Free Gemini API Key dalein!")
        else:
            st.session_state["chat_history"].append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Soch raha hoon..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        chat_prompt = f"""
                        You are an AI Competitor Intelligence Advisor for 'My_Brand'. Answer the user's question based strictly on this market dataset. Keep the answer practical, clear, and concise.
                        
                        Dataset:
                        {df.to_string()}
                        
                        User Question: {user_question}
                        """
                        reply = model.generate_content(chat_prompt).text
                        st.markdown(reply)
                        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"Error: {e}")