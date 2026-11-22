import sqlite3
import hashlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Competitor Intelligence & Market Analysis",
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


# --- BRIGHT HIGH-CONTRAST THEME & 3D GLASSMORPHISM TOGGLE ---
def apply_glass_theme():
    is_dark = st.session_state.authenticated and (st.session_state.theme_mode == "Dark")

    if is_dark:
        bg_main = "#090D16"
        bg_card = "#131926"
        bg_sidebar = "#0E131F"
        text_bright = "#FFFFFF"
        text_sub = "#E2E8F0"
        border_col = "#2A344A"
        soft_tint = "#1C2538"
        accent = "#6366F1"
        accent_hover = "#4F46E5"
        header_bg = "linear-gradient(135deg, #1E1B4B 0%, #312E81 55%, #0F172A 100%)"
        # 3D Glass Dark State (Knob on Right with Crescent Moon, Text "Dark" on Left)
        glass_bg = "linear-gradient(145deg, rgba(35,39,47,0.92), rgba(18,20,26,0.96))"
        glass_border = "rgba(255, 255, 255, 0.14)"
        glass_shadow = "0 10px 25px rgba(0,0,0,0.6), inset 0 1px 2px rgba(255,255,255,0.18)"
        knob_transform = "translateX(76px)"
        knob_bg = "radial-gradient(circle at 30% 30%, #3B4252, #181B22)"
        knob_shadow = "0 4px 12px rgba(0,0,0,0.7), inset 0 1px 2px rgba(255,255,255,0.25)"
        knob_symbol = "🌙"
        label_text = "Dark"
        label_pos = "left: 20px;"
        label_color = "#F8FAFC"
    else:
        bg_main = "#F5F7FB"
        bg_card = "#FFFFFF"
        bg_sidebar = "#FFFFFF"
        text_bright = "#090D16"
        text_sub = "#1E293B"
        border_col = "#CBD5E1"
        soft_tint = "#EEF2FF"
        accent = "#4F46E5"
        accent_hover = "#4338CA"
        header_bg = "linear-gradient(135deg, #312E81 0%, #4F46E5 55%, #0EA5E9 100%)"
        # 3D Glass Light State (Knob on Left with Glowing Sun, Text "Light" on Right)
        glass_bg = "linear-gradient(145deg, rgba(226,232,240,0.88), rgba(203,213,225,0.95))"
        glass_border = "rgba(255, 255, 255, 0.85)"
        glass_shadow = "0 10px 25px rgba(15,23,42,0.14), inset 0 2px 4px rgba(255,255,255,0.9)"
        knob_transform = "translateX(0px)"
        knob_bg = "radial-gradient(circle at 35% 35%, #FFFFFF, #E2E8F0)"
        knob_shadow = "0 6px 14px rgba(15,23,42,0.22), inset 0 2px 3px #FFFFFF"
        knob_symbol = "☀️"
        label_text = "Light"
        label_
