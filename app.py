"""
app.py — Entry point Commensali Cloud
"""
import streamlit as st
from utils.auth import check_auth, login_page, logout, is_admin, ACCENT

st.set_page_config(
    page_title="Commensali",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS Globale ────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    min-height: 100vh;
}

/* Bottoni */
.stButton > button {
    border-radius: 8px; font-weight: 500;
    border: 1px solid rgba(240,165,0,0.45);
    background: rgba(240,165,0,0.08); color: #f0a500;
    transition: all .2s ease;
}
.stButton > button:hover {
    border-color: #f0a500; background: rgba(240,165,0,0.18);
    box-shadow: 0 4px 15px rgba(240,165,0,.2); transform: translateY(-1px);
    color: #f0a500;
}

/* Input */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important; color: #f0f4f8 !important;
}

/* Testi */
h1, h2, h3, h4 { color: #f0f4f8 !important; }
p, label, div, span { color: #ccd6e0; }
hr { border-color: rgba(255,255,255,0.08) !important; }

/* Nav radio orizzontale */
div[data-testid="stHorizontalBlock"] label {
    color: #8899aa !important; font-weight: 500;
}

/* Expander */
.stExpander {
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.04) !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: rgba(240,165,0,.35); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── AUTH ───────────────────────────────────────────────────────────────────────
if not check_auth():
    login_page()
    st.stop()

# ── HEADER + NAVIGAZIONE ───────────────────────────────────────────────────────
nome = st.session_state.get("user_nome", "Chef")

pages_user  = ["🏠 Ricettario", "👥 Commensali", "📅 Nuovo Evento", "📖 Storico", "👤 Profilo"]
pages_admin = ["👑 Admin"] + pages_user

pages = pages_admin if is_admin() else pages_user

col_logo, col_nav, col_exit = st.columns([2, 7, 1])

with col_logo:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:.5rem;padding:.4rem 0;">
      <span style="font-size:1.5rem;">🍽️</span>
      <span style="font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:800;
                   background:linear-gradient(135deg,#f0a500,#e67e22);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        Commensali
      </span>
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    pagina = st.radio("nav", pages, horizontal=True, label_visibility="collapsed", key="main_nav")

with col_exit:
    if st.button("🚪", key="logout_btn", help=f"Esci ({nome})"):
        logout()

st.markdown(f"<hr style='border-color:{ACCENT}22;margin:.3rem 0 1rem;'>", unsafe_allow_html=True)

# ── ROUTING ────────────────────────────────────────────────────────────────────
if pagina == "👑 Admin":
    from pages import admin; admin.show()
elif pagina == "🏠 Ricettario":
    from pages import ricettario; ricettario.show()
elif pagina == "👥 Commensali":
    from pages import commensali; commensali.show()
elif pagina == "📅 Nuovo Evento":
    from pages import nuovo_evento; nuovo_evento.show()
elif pagina == "📖 Storico":
    from pages import storico; storico.show()
elif pagina == "👤 Profilo":
    from pages import profilo; profilo.show()
