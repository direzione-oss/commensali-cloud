"""pages/profilo.py — Cambio password"""
import streamlit as st
from utils.auth import hash_pw, ADMIN_EMAIL
from utils.db import get_supabase

ACCENT = "#f0a500"


def show():
    uid   = st.session_state["user_id"]
    email = st.session_state.get("user_email", "")
    nome  = st.session_state.get("user_nome", "")

    st.markdown(f"<h2 style='color:#f0f4f8;border-left:4px solid {ACCENT};padding-left:12px;'>👤 Il Mio Profilo</h2>", unsafe_allow_html=True)

    st.markdown(f"**👤 Nome:** {nome}")
    st.markdown(f"**📧 Email:** {email}")
    if email == ADMIN_EMAIL:
        st.markdown(f"<span style='background:rgba(240,165,0,.2);color:{ACCENT};border:1px solid {ACCENT};padding:2px 10px;border-radius:20px;font-size:.8em;font-weight:700;'>👑 Admin</span>", unsafe_allow_html=True)

    st.divider()
    st.subheader("🔑 Cambia Password")

    with st.form("change_pw"):
        old_pw  = st.text_input("Password attuale", type="password")
        new_pw1 = st.text_input("Nuova password", type="password")
        new_pw2 = st.text_input("Conferma nuova password", type="password")
        submit  = st.form_submit_button("Aggiorna Password", use_container_width=True)

    if submit:
        if not old_pw or not new_pw1:
            st.error("Compila tutti i campi.")
        elif new_pw1 != new_pw2:
            st.error("Le password nuove non corrispondono.")
        elif len(new_pw1) < 6:
            st.error("Minimo 6 caratteri.")
        else:
            sb = get_supabase()
            check = sb.table("comm_utenti").select("id").eq("id", uid).eq("password_hash", hash_pw(old_pw)).execute()
            if not check.data:
                st.error("❌ Password attuale errata.")
            else:
                sb.table("comm_utenti").update({"password_hash": hash_pw(new_pw1)}).eq("id", uid).execute()
                st.success("✅ Password aggiornata!")
