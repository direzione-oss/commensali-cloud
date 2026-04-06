"""pages/admin.py — Pannello amministratore"""
import streamlit as st
from utils.db import get_supabase, get_all_users, set_user_role, delete_user, get_ricette, get_eventi
from utils.auth import is_admin

ACCENT = "#f0a500"


def show():
    if not is_admin():
        st.error("⛔ Accesso negato.")
        return

    st.markdown(f"<h2 style='color:#f0f4f8;border-left:4px solid {ACCENT};padding-left:12px;'>👑 Pannello Admin</h2>", unsafe_allow_html=True)

    # ── Stats globali ──────────────────────────────────────
    utenti = get_all_users()
    sb     = get_supabase()
    n_ric  = sb.table("comm_ricette").select("id", count="exact").execute().count or 0
    n_ev   = sb.table("comm_eventi").select("id", count="exact").execute().count or 0

    c1, c2, c3 = st.columns(3)
    def stat(col, icon, label, val):
        with col:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,.05);border:1px solid rgba(240,165,0,.3);
                        border-radius:14px;padding:1.2rem;text-align:center;">
              <div style="font-size:2rem;">{icon}</div>
              <div style="font-size:1.8rem;font-weight:800;color:{ACCENT};">{val}</div>
              <div style="color:#8899aa;font-size:.85rem;">{label}</div>
            </div>""", unsafe_allow_html=True)

    stat(c1, "👥", "Utenti registrati", len(utenti))
    stat(c2, "📖", "Ricette totali", n_ric)
    stat(c3, "📅", "Eventi totali", n_ev)

    st.divider()

    # ── Gestione utenti ────────────────────────────────────
    st.subheader("👥 Gestione Utenti")

    ROLES = ["utente", "disabilitato"]

    for u in utenti:
        with st.container(border=True):
            c_info, c_role, c_del = st.columns([4, 2, 1])
            with c_info:
                safe_nome  = (u.get('nome','—') or '—').replace('<','&lt;').replace('>','&gt;')
                safe_email = (u.get('email','') or '').replace('<','&lt;').replace('>','&gt;')
                badge = f"<span style='background:rgba(240,165,0,.2);color:{ACCENT};border:1px solid rgba(240,165,0,.4);padding:1px 8px;border-radius:20px;font-size:.72em;'>{u.get('ruolo','utente')}</span>"
                st.markdown(f"**{safe_nome}** &nbsp; {badge} &nbsp; `{safe_email}`", unsafe_allow_html=True)
            with c_role:
                current = u.get("ruolo", "utente")
                new_role = st.selectbox("Ruolo", ROLES,
                    index=ROLES.index(current) if current in ROLES else 0,
                    key=f"role_{u['id']}", label_visibility="collapsed")
                if new_role != current:
                    if st.button("✓ Applica", key=f"apply_{u['id']}", use_container_width=True):
                        set_user_role(u["id"], new_role)
                        st.rerun()
            with c_del:
                if u["email"] != st.session_state.get("user_email"):
                    if st.button("🗑️", key=f"del_u_{u['id']}", help="Elimina utente"):
                        delete_user(u["id"])
                        st.rerun()

    # ── Crea utente manualmente ────────────────────────────
    st.divider()
    st.subheader("➕ Crea Utente")
    with st.form("create_user"):
        cu1, cu2 = st.columns(2)
        with cu1:
            new_nome  = st.text_input("Nome")
            new_email = st.text_input("Email")
        with cu2:
            new_pw    = st.text_input("Password", type="password")
            new_ruolo = st.selectbox("Ruolo", ROLES)
        submit = st.form_submit_button("Crea Utente", use_container_width=True)

    if submit:
        if not new_email or not new_pw:
            st.error("Email e password obbligatorie.")
        else:
            from utils.auth import hash_pw
            sb = get_supabase()
            existing = sb.table("comm_utenti").select("id").eq("email", new_email.strip().lower()).execute()
            if existing.data:
                st.error("Email già esistente.")
            else:
                sb.table("comm_utenti").insert({
                    "nome": new_nome.strip(),
                    "email": new_email.strip().lower(),
                    "password_hash": hash_pw(new_pw),
                    "ruolo": new_ruolo,
                }).execute()
                st.success(f"✅ Utente {new_email} creato!")
                st.rerun()
