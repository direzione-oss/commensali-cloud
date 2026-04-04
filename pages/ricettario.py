"""pages/ricettario.py"""
import streamlit as st
from utils.db import get_ricette, insert_ricetta, update_ricetta, delete_ricetta, upload_image
import uuid, time

PORTATE = ["", "Antipasti", "Primi", "Zuppe", "Secondi Carne", "Secondi Pesce", "Contorni", "Dolci", "Lievitati"]
ACCENT = "#f0a500"


def show():
    uid = st.session_state["user_id"]

    # ── Header ─────────────────────────────────────────────
    c1, c2 = st.columns([6, 2])
    with c1:
        st.markdown(f"<h2 style='color:#f0f4f8;border-left:4px solid {ACCENT};padding-left:12px;'>🏠 Il Tuo Ricettario</h2>", unsafe_allow_html=True)
    with c2:
        if st.button("➕ Nuova Ricetta", key="toggle_add_form", use_container_width=True):
            st.session_state["show_add_form"] = not st.session_state.get("show_add_form", False)

    # ── Form aggiunta ───────────────────────────────────────
    if st.session_state.get("show_add_form", False):
        with st.container(border=True):
            st.subheader("✏️ Aggiungi Ricetta")
            with st.form("add_ricetta_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    titolo      = st.text_input("Titolo *", placeholder="es. Risotto ai funghi")
                    portata     = st.selectbox("Portata", PORTATE)
                with col2:
                    foto_file   = st.file_uploader("Foto", type=["jpg", "jpeg", "png"])
                ingredienti = st.text_area("Ingredienti", height=120)
                procedimento = st.text_area("Procedimento", height=150)
                note        = st.text_area("Note", height=80)
                col_s, col_a = st.columns(2)
                with col_s:
                    salva = st.form_submit_button("💾 Salva", use_container_width=True)
                with col_a:
                    annulla = st.form_submit_button("Annulla", use_container_width=True)

            if salva:
                if not titolo:
                    st.error("Il titolo è obbligatorio.")
                else:
                    foto_url = ""
                    if foto_file:
                        fname = f"{uuid.uuid4().hex}.jpg"
                        foto_url = upload_image(foto_file.read(), fname, "ricette")
                    insert_ricetta(uid, {
                        "titolo": titolo, "portata": portata,
                        "ingredienti": ingredienti, "procedimento": procedimento,
                        "note": note, "foto_url": foto_url,
                    })
                    st.success("✅ Ricetta salvata!")
                    st.session_state["show_add_form"] = False
                    time.sleep(0.5)
                    st.rerun()
            if annulla:
                st.session_state["show_add_form"] = False
                st.rerun()

    # ── Filtri ──────────────────────────────────────────────
    ricette = get_ricette(uid)
    if not ricette:
        st.info("Nessuna ricetta ancora. Aggiungine una!")
        return

    fc1, fc2 = st.columns([3, 2])
    with fc1:
        search = st.text_input("🔍 Cerca", placeholder="Cerca per nome...", label_visibility="collapsed")
    with fc2:
        filtro_portata = st.selectbox("Portata", ["Tutte"] + PORTATE[1:], label_visibility="collapsed")

    if search:
        ricette = [r for r in ricette if search.lower() in r["titolo"].lower()]
    if filtro_portata != "Tutte":
        ricette = [r for r in ricette if r.get("portata") == filtro_portata]

    # ── Paginazione ─────────────────────────────────────────
    PER_PAGE = 12
    n_pages  = max(1, -(-len(ricette) // PER_PAGE))
    if "ric_page" not in st.session_state:
        st.session_state["ric_page"] = 0
    page = st.session_state["ric_page"]
    ricette_pag = ricette[page * PER_PAGE:(page + 1) * PER_PAGE]

    # ── Griglia ─────────────────────────────────────────────
    cols = st.columns(3)
    for idx, r in enumerate(ricette_pag):
        with cols[idx % 3]:
            with st.container(border=True):
                # Foto
                if r.get("foto_url"):
                    st.image(r["foto_url"], use_container_width=True)
                # Titolo + badge
                st.markdown(f"**{r['titolo']}**")
                if r.get("portata"):
                    st.markdown(f"<span style='background:rgba(240,165,0,.15);color:#f0a500;border:1px solid rgba(240,165,0,.4);padding:2px 8px;border-radius:20px;font-size:.75em;'>{r['portata']}</span>", unsafe_allow_html=True)

                with st.expander("📋 Dettagli"):
                    if r.get("ingredienti"):
                        st.markdown(f"**Ingredienti:**\n{r['ingredienti']}")
                    if r.get("procedimento"):
                        st.markdown(f"**Procedimento:**\n{r['procedimento']}")
                    if r.get("note"):
                        st.info(r["note"])

                with st.expander("🛠️ Modifica/Elimina"):
                    with st.form(f"edit_{r['id']}"):
                        nt = st.text_input("Titolo", value=r["titolo"], key=f"t_{r['id']}")
                        np = st.selectbox("Portata", PORTATE, index=PORTATE.index(r.get("portata","")) if r.get("portata","") in PORTATE else 0, key=f"p_{r['id']}")
                        ni = st.text_area("Ingredienti", value=r.get("ingredienti",""), key=f"i_{r['id']}")
                        npr = st.text_area("Procedimento", value=r.get("procedimento",""), key=f"pr_{r['id']}")
                        nn = st.text_area("Note", value=r.get("note",""), key=f"n_{r['id']}")
                        nf = st.file_uploader("Cambia foto", type=["jpg","jpeg","png"], key=f"f_{r['id']}")
                        cs, cd = st.columns(2)
                        with cs: salva_mod = st.form_submit_button("💾 Salva modifiche")
                        with cd: elimina   = st.form_submit_button("🗑️ Elimina")

                    if salva_mod:
                        payload = {"titolo": nt, "portata": np, "ingredienti": ni, "procedimento": npr, "note": nn}
                        if nf:
                            payload["foto_url"] = upload_image(nf.read(), f"{uuid.uuid4().hex}.jpg", "ricette")
                        update_ricetta(r["id"], payload)
                        st.success("Salvato!")
                        st.rerun()
                    if elimina:
                        delete_ricetta(r["id"])
                        st.rerun()

    # Navigazione pagine
    if n_pages > 1:
        pp, _, pn = st.columns([1, 3, 1])
        with pp:
            if page > 0 and st.button("◀ Prec.", use_container_width=True):
                st.session_state["ric_page"] -= 1; st.rerun()
        with pn:
            if page < n_pages - 1 and st.button("Succ. ▶", use_container_width=True):
                st.session_state["ric_page"] += 1; st.rerun()
        st.caption(f"Pagina {page+1} di {n_pages}")
