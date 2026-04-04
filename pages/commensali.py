"""pages/commensali.py"""
import streamlit as st
from utils.db import get_commensali, insert_commensale, delete_commensale

ACCENT = "#f0a500"


def show():
    uid = st.session_state["user_id"]
    st.markdown(f"<h2 style='color:#f0f4f8;border-left:4px solid {ACCENT};padding-left:12px;'>👥 I Tuoi Commensali</h2>", unsafe_allow_html=True)

    with st.form("add_commensale", clear_on_submit=True):
        c1, c2 = st.columns([4, 1])
        with c1:
            nome = st.text_input("Nome commensale", placeholder="es. Mario Rossi", label_visibility="collapsed")
        with c2:
            submit = st.form_submit_button("➕ Aggiungi", use_container_width=True)
        if submit and nome.strip():
            insert_commensale(uid, nome.strip())
            st.success(f"✅ {nome.strip()} aggiunto!")
            st.rerun()

    st.divider()

    commensali = get_commensali(uid)
    if not commensali:
        st.info("Nessun commensale ancora.")
        return

    st.markdown(f"**{len(commensali)} commensali**")
    for c in commensali:
        col_n, col_d = st.columns([6, 1])
        with col_n:
            st.markdown(f"👤 {c['nome']}")
        with col_d:
            if st.button("🗑️", key=f"del_c_{c['id']}", help="Elimina"):
                delete_commensale(c["id"])
                st.rerun()
