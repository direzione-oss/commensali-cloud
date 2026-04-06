"""
utils/auth.py — Autenticazione Commensali Cloud
"""
import streamlit as st
import hashlib
from utils.db import get_supabase

ADMIN_EMAIL = "direzione@serrastudio.it"

# Accent color
ACCENT = "#f0a500"


def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


MAX_LOGIN_ATTEMPTS = 5


def _check_rate_limit() -> bool:
    """Ritorna True se l'utente ha superato il limite tentativi."""
    attempts = st.session_state.get("_login_attempts", 0)
    return attempts >= MAX_LOGIN_ATTEMPTS


def _increment_attempts():
    st.session_state["_login_attempts"] = st.session_state.get("_login_attempts", 0) + 1


def _reset_attempts():
    st.session_state["_login_attempts"] = 0


def _auth_style():
    st.markdown("""
    <style>
    .auth-card {
        max-width: 420px; margin: 2rem auto; padding: 2.5rem 2rem;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(240,165,0,0.35);
        border-radius: 18px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    }
    .auth-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem; font-weight: 800;
        text-align: center; margin-bottom: 0.2rem;
        background: linear-gradient(135deg, #f0a500, #e67e22);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .auth-sub {
        color: #8899aa; text-align: center;
        font-size: .88rem; letter-spacing: .5px;
        margin-bottom: 1.8rem;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)


def login_page():
    """Pagina login/registrazione/reset unificata."""
    _auth_style()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="auth-title">🍽️ Commensali</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">GESTORE MENU ANTI-RIPETIZIONE</div>', unsafe_allow_html=True)

        if "auth_mode" not in st.session_state:
            st.session_state["auth_mode"] = "login"

        mode = st.session_state["auth_mode"]

        # ── LOGIN ─────────────────────────────────────────────
        if mode == "login":
            with st.form("login_form"):
                email    = st.text_input("📧 Email", placeholder="la-tua@email.it")
                password = st.text_input("🔑 Password", type="password")
                submit   = st.form_submit_button("Accedi →", use_container_width=True)

            if submit:
                if _check_rate_limit():
                    st.error(f"⛔ Troppi tentativi falliti ({MAX_LOGIN_ATTEMPTS}). Ricarica la pagina per riprovare.")
                elif not email or not password:
                    st.error("Inserisci email e password.")
                else:
                    sb = get_supabase()
                    res = (sb.table("comm_utenti")
                             .select("id, nome, email, ruolo")
                             .eq("email", email.strip().lower())
                             .eq("password_hash", hash_pw(password))
                             .execute())
                    if res.data:
                        user = res.data[0]
                        if user.get("ruolo") == "disabilitato":
                            st.error("⛔ Account disabilitato. Contatta l'amministratore.")
                        else:
                            _reset_attempts()
                            st.session_state["user_id"]    = user["id"]
                            st.session_state["user_nome"]  = user.get("nome") or email.split("@")[0]
                            st.session_state["user_email"] = user["email"]
                            st.session_state["user_ruolo"] = user.get("ruolo", "utente")
                            st.session_state["logged_in"]  = True
                            st.rerun()
                    else:
                        _increment_attempts()
                        rimasti = MAX_LOGIN_ATTEMPTS - st.session_state.get("_login_attempts", 0)
                        st.error(f"❌ Credenziali non corrette. Tentativi rimasti: {max(rimasti, 0)}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("📝 Registrati", key="goto_reg", use_container_width=True):
                    st.session_state["auth_mode"] = "register"
                    st.rerun()
            with c2:
                if st.button("🔑 Password dimenticata", key="goto_reset", use_container_width=True):
                    st.session_state["auth_mode"] = "reset"
                    st.rerun()

        # ── REGISTRAZIONE ─────────────────────────────────────
        elif mode == "register":
            st.markdown(f"<h3 style='color:{ACCENT};text-align:center;'>📝 Nuovo Account</h3>", unsafe_allow_html=True)

            with st.form("reg_form"):
                nome   = st.text_input("👤 Nome", placeholder="Mario Rossi")
                email  = st.text_input("📧 Email", placeholder="mario@email.it")
                pw1    = st.text_input("🔑 Password", type="password")
                pw2    = st.text_input("🔑 Conferma Password", type="password")
                submit = st.form_submit_button("✓ Crea account", use_container_width=True)

            if submit:
                if not email or not pw1:
                    st.error("Email e password obbligatorie.")
                elif pw1 != pw2:
                    st.error("Le password non corrispondono.")
                elif len(pw1) < 6:
                    st.error("Minimo 6 caratteri.")
                else:
                    sb = get_supabase()
                    existing = sb.table("comm_utenti").select("id").eq("email", email.strip().lower()).execute()
                    if existing.data:
                        st.error("❌ Email già registrata.")
                    else:
                        sb.table("comm_utenti").insert({
                            "nome": nome.strip(),
                            "email": email.strip().lower(),
                            "password_hash": hash_pw(pw1),
                            "ruolo": "utente",
                        }).execute()
                        st.success("✅ Account creato! Ora puoi accedere.")
                        st.session_state["auth_mode"] = "login"
                        st.rerun()

            if st.button("← Torna al login", key="back_reg", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

        # ── RESET PASSWORD ────────────────────────────────────
        elif mode == "reset":
            st.markdown(f"<h3 style='color:{ACCENT};text-align:center;'>🔑 Password dimenticata?</h3>", unsafe_allow_html=True)
            st.info(
                "Per motivi di sicurezza il reset password non è disponibile in modo autonomo.\n\n"
                "Contatta l'amministratore all'indirizzo **direzione@serrastudio.it** "
                "per richiedere il ripristino del tuo account."
            )
            if st.button("← Torna al login", key="back_reset", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

    return False


def check_auth() -> bool:
    return st.session_state.get("logged_in", False)


def is_admin() -> bool:
    return st.session_state.get("user_email", "") == ADMIN_EMAIL


def logout():
    for k in ["user_id", "user_nome", "user_email", "user_ruolo", "logged_in", "auth_mode"]:
        st.session_state.pop(k, None)
    st.rerun()
