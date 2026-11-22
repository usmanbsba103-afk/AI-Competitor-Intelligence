import sqlite3
import hashlib
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
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"


# --- NEO-TACTILE GLASS TOGGLE + HIGH-CLARITY BRIGHT THEME ---
def apply_theme_styles():
    is_dark = st.session_state.authenticated and (st.session_state.theme_mode == "Dark")

    if is_dark:
        bg_main = "#0B0F19"
        bg_card = "#131926"
        bg_sidebar = "#0F1420"
        text_primary = "#FFFFFF"
        text_secondary = "#CBD5E1"
        border_color = "#2A3447"
        soft_bg = "#1B2336"
        accent = "#6366F1"
        accent_hover = "#4F46E5"
        header_bg = "linear-gradient(135deg, #1E1B4B 0%, #312E81 55%, #1E293B 100%)"
        # Dark glass toggle state (matches image 1: "Dark" on left, glowing moon orb on right)
        glass_bg = "linear-gradient(145deg, rgba(38,42,52,0.92), rgba(22,25,32,0.96))"
        glass_border = "rgba(255, 255, 255, 0.16)"
        glass_shadow = "0 10px 25px rgba(0,0,0,0.45), inset 0 1px 1px rgba(255,255,255,0.15)"
        orb_left = "74px"
        orb_bg = "radial-gradient(circle at 30% 30%, #FFFFFF, #CBD5E1)"
        orb_icon = "🌙"
        label_left = "18px"
        label_text = "Dark"
        label_color = "#E2E8F0"
    else:
        bg_main = "#F7F8FC"
        bg_card = "#FFFFFF"
        bg_sidebar = "#FFFFFF"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        border_color = "#E2E8F0"
        soft_bg = "#EEF2FF"
        accent = "#4F46E5"
        accent_hover = "#4338CA"
        header_bg = "linear-gradient(135deg, #312E81 0%, #4F46E5 55%, #0EA5E9 100%)"
        # Light glass toggle state (matches image 2: glowing sun orb on left, "Light" on right)
        glass_bg = "linear-gradient(145deg, rgba(226,232,240,0.85), rgba(203,213,225,0.9))"
        glass_border = "rgba(255, 255, 255, 0.75)"
        glass_shadow = "0 8px 20px rgba(15,23,42,0.12), inset 0 2px 4px rgba(255,255,255,0.8)"
        orb_left = "6px"
        orb_bg = "radial-gradient(circle at 30% 30%, #FFFFFF, #F1F5F9)"
        orb_icon = "☀️"
        label_left = "62px"
        label_text = "Light"
        label_color = "#1E293B"

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {{
                font-family: 'Plus
